"""
Research Orchestrator — coordinates research workflows.
"""
from typing import Dict, List, Optional
from datetime import datetime
from sprint11.research_core.experiment_manager import ExperimentManager
from sprint11.research_core.evaluation_engine import EvaluationEngine
from sprint11.schemas.models import ResearchProject

class ResearchOrchestrator:
    """Orchestrates end-to-end research workflows."""
    
    def __init__(self):
        self.experiments = ExperimentManager()
        self.evaluation = EvaluationEngine()
        self.projects: Dict[str, ResearchProject] = {}
        
        # Register default rubrics
        self._register_default_rubrics()
        
    def _register_default_rubrics(self):
        """Register standard evaluation rubrics."""
        self.evaluation.register_rubric("engineering_design", {
            "criteria": [
                {"name": "feasibility", "weight": 0.25, "target": 0.8},
                {"name": "performance", "weight": 0.25, "target": 0.9},
                {"name": "cost_efficiency", "weight": 0.2, "target": 0.7},
                {"name": "safety_margin", "weight": 0.2, "target": 1.5},
                {"name": "manufacturability", "weight": 0.1, "target": 0.8}
            ],
            "pass_threshold": 0.7
        })
        
        self.evaluation.register_rubric("simulation_accuracy", {
            "criteria": [
                {"name": "error_pct", "weight": 0.4, "target": 5.0},
                {"name": "convergence", "weight": 0.3, "target": 1.0},
                {"name": "runtime_ratio", "weight": 0.3, "target": 1.0}
            ],
            "pass_threshold": 0.75
        })
        
    def create_project(self, name: str, domain: str, objective: str) -> ResearchProject:
        """Create a new research project."""
        project = ResearchProject(name=name, domain=domain, objective=objective)
        self.projects[project.id] = project
        return project
        
    def run_experiment(self, project_id: str, name: str,
                      runner_fn, config: Dict = None,
                      parameters: Dict = None, rubric: str = None,
                      hypothesis_id: str = None) -> Dict:
        """Run an experiment with full tracking."""
        # Create experiment
        exp = self.experiments.create_experiment(
            project_id, name, config, parameters,
            hypothesis_id=hypothesis_id
        )
        
        # Update project
        project = self.projects.get(project_id)
        if project:
            project.experiment_ids.append(exp.id)
            if hypothesis_id and hypothesis_id not in project.hypothesis_ids:
                project.hypothesis_ids.append(hypothesis_id)
                
        try:
            # Start
            self.experiments.start_experiment(exp.id)
            
            # Run
            result = runner_fn(exp.parameters)
            
            # Log metrics
            if isinstance(result, dict) and "metrics" in result:
                self.experiments.log_metrics(exp.id, result["metrics"])
                
            # Evaluate if rubric provided
            evaluation = None
            if rubric and isinstance(result, dict) and "metrics" in result:
                evaluation = self.evaluation.evaluate(rubric, result["metrics"])
                
            # Complete
            final_metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
            self.experiments.complete_experiment(exp.id, final_metrics)
            
            return {
                "experiment_id": exp.id,
                "status": "COMPLETED",
                "result": result,
                "evaluation": evaluation,
                "content_hash": self.experiments.compute_content_hash(exp.id)
            }
            
        except Exception as e:
            self.experiments.fail_experiment(exp.id, str(e))
            return {
                "experiment_id": exp.id,
                "status": "FAILED",
                "error": str(e)
            }
            
    def get_project(self, project_id: str) -> Optional[ResearchProject]:
        return self.projects.get(project_id)
        
    def list_projects(self) -> List[ResearchProject]:
        return list(self.projects.values())
        
    def get_project_summary(self, project_id: str) -> Dict:
        """Get comprehensive project summary."""
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}
            
        experiments = self.experiments.list_experiments(project_id)
        completed = [e for e in experiments if e.state == "COMPLETED"]
        failed = [e for e in experiments if e.state == "FAILED"]
        
        # Aggregate metrics
        all_metrics = {}
        for exp in completed:
            for k, v in exp.metrics.items():
                all_metrics.setdefault(k, []).append(v)
                
        metric_summary = {}
        for k, values in all_metrics.items():
            metric_summary[k] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
            
        return {
            "project": project.model_dump(),
            "experiment_count": len(experiments),
            "completed": len(completed),
            "failed": len(failed),
            "metric_summary": metric_summary,
            "insights_count": len(project.insights)
        }
