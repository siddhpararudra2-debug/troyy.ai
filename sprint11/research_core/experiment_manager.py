"""
Experiment Manager — event-sourced experiment tracking (MLflow-compatible).
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import hashlib
from sprint11.schemas.models import Experiment
from sprint11.schemas.enums import ExperimentState

class ExperimentManager:
    """Tracks experiments with full audit trail."""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.event_log: List[Dict] = []
        self.runs_by_project: Dict[str, List[str]] = {}
        
    def create_experiment(self, project_id: str, name: str,
                         config: Dict = None, parameters: Dict = None,
                         tags: List[str] = None,
                         hypothesis_id: str = None) -> Experiment:
        """Create a new experiment."""
        exp = Experiment(
            project_id=project_id,
            name=name,
            config=config or {},
            parameters=parameters or {},
            tags=tags or [],
            hypothesis_id=hypothesis_id
        )
        self.experiments[exp.id] = exp
        self.runs_by_project.setdefault(project_id, []).append(exp.id)
        self._log_event("CREATED", exp.id, {"name": name})
        return exp
        
    def start_experiment(self, experiment_id: str) -> Experiment:
        """Mark experiment as running."""
        exp = self._get_experiment(experiment_id)
        exp.state = ExperimentState.RUNNING.value
        exp.started_at = datetime.utcnow()
        self._log_event("STARTED", experiment_id)
        return exp
        
    def log_metric(self, experiment_id: str, key: str, value: float,
                  step: int = None) -> None:
        """Log a metric for an experiment."""
        exp = self._get_experiment(experiment_id)
        exp.metrics[key] = value
        self._log_event("METRIC", experiment_id, {"key": key, "value": value, "step": step})
        
    def log_metrics(self, experiment_id: str, metrics: Dict[str, float]) -> None:
        """Log multiple metrics."""
        for k, v in metrics.items():
            self.log_metric(experiment_id, k, v)
        
    def log_artifact(self, experiment_id: str, artifact_ref: str) -> None:
        """Log an artifact reference."""
        exp = self._get_experiment(experiment_id)
        exp.artifacts.append(artifact_ref)
        self._log_event("ARTIFACT", experiment_id, {"ref": artifact_ref})
        
    def log_parameter(self, experiment_id: str, key: str, value: Any) -> None:
        """Log a parameter."""
        exp = self._get_experiment(experiment_id)
        exp.parameters[key] = value
        self._log_event("PARAMETER", experiment_id, {"key": key, "value": value})
        
    def complete_experiment(self, experiment_id: str,
                           final_metrics: Dict[str, float] = None) -> Experiment:
        """Mark experiment as completed."""
        exp = self._get_experiment(experiment_id)
        if final_metrics:
            exp.metrics.update(final_metrics)
        exp.state = ExperimentState.COMPLETED.value
        exp.completed_at = datetime.utcnow()
        self._log_event("COMPLETED", experiment_id, {"metrics": exp.metrics})
        return exp
        
    def fail_experiment(self, experiment_id: str, error: str) -> Experiment:
        """Mark experiment as failed."""
        exp = self._get_experiment(experiment_id)
        exp.state = ExperimentState.FAILED.value
        exp.error_message = error
        exp.completed_at = datetime.utcnow()
        self._log_event("FAILED", experiment_id, {"error": error})
        return exp
        
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        return self.experiments.get(experiment_id)
        
    def list_experiments(self, project_id: str = None,
                        state: str = None) -> List[Experiment]:
        result = list(self.experiments.values())
        if project_id:
            result = [e for e in result if e.project_id == project_id]
        if state:
            result = [e for e in result if e.state == state]
        return sorted(result, key=lambda e: e.created_at, reverse=True)
        
    def compare_experiments(self, experiment_ids: List[str],
                           metric_key: str) -> Dict:
        """Compare experiments by a specific metric."""
        comparisons = []
        for eid in experiment_ids:
            exp = self.experiments.get(eid)
            if exp and metric_key in exp.metrics:
                comparisons.append({
                    "experiment_id": eid,
                    "name": exp.name,
                    "value": exp.metrics[metric_key],
                    "state": exp.state,
                    "parameters": exp.parameters
                })
        comparisons.sort(key=lambda c: c["value"], reverse=True)
        return {
            "metric": metric_key,
            "comparisons": comparisons,
            "best": comparisons[0] if comparisons else None
        }
        
    def get_event_log(self, experiment_id: str = None) -> List[Dict]:
        if experiment_id:
            return [e for e in self.event_log if e["experiment_id"] == experiment_id]
        return self.event_log
        
    def compute_content_hash(self, experiment_id: str) -> str:
        """Compute content hash for reproducibility verification."""
        exp = self._get_experiment(experiment_id)
        content = {
            "config": exp.config,
            "parameters": exp.parameters,
            "metrics": exp.metrics
        }
        json_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
        
    def _get_experiment(self, experiment_id: str) -> Experiment:
        exp = self.experiments.get(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        return exp
        
    def _log_event(self, event_type: str, experiment_id: str,
                  data: Dict = None) -> None:
        self.event_log.append({
            "event_type": event_type,
            "experiment_id": experiment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        })
        # Bound log size
        if len(self.event_log) > 10000:
            self.event_log = self.event_log[-5000:]
