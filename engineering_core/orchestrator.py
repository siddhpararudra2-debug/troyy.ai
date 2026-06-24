"""
Engineering Orchestrator for Engineering OS.
Coordinates all engineering modules in unified workflow.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
import uuid


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    CREATED = "created"
    RUNNING = "running"
    EXECUTING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(str, Enum):
    """Stages in the engineering workflow."""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    CALCULATION = "calculation"
    VALIDATION = "validation"
    REASONING = "reasoning"
    OPTIMIZATION = "optimization"
    REPORTING = "reporting"
    APPROVAL = "approval"

    @property
    def stage_type(self):
        return self


@dataclass
class WorkflowStep:
    """A single step in the workflow."""
    stage: PipelineStage
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.CREATED
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class EngineeringWorkflow:
    """Complete engineering workflow."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    design_id: str = ""
    design_name: str = ""
    
    # Workflow definition
    stages: List[PipelineStage] = field(default_factory=list)
    steps: List[WorkflowStep] = field(default_factory=list)
    
    # Execution
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_stage: int = 0  # Index in stages
    
    # Configuration
    skip_validation: bool = False
    skip_optimization: bool = False
    parallel_execution: bool = False
    
    # Results
    final_design: Dict[str, Any] = field(default_factory=dict)
    design_metrics: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    # Timeline
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class EngineeringOrchestrator:
    """
    Orchestrates complete engineering workflows.
    Coordinates: Calculation → Validation → Reasoning → Optimization → Reporting
    """

    def __init__(self):
        self.workflow_count = 0
        self.running_workflows: Dict[str, EngineeringWorkflow] = {}

    async def create_workflow(
        self,
        workflow_id: str,
        design_id: str,
        design_name: str,
        include_optimization: bool = True,
        include_reasoning: bool = True
    ) -> EngineeringWorkflow:
        """Create a new engineering workflow."""
        self.workflow_count += 1
        
        workflow = EngineeringWorkflow(
            workflow_id=workflow_id,
            design_id=design_id,
            design_name=design_name
        )
        
        # Define standard pipeline
        workflow.stages = [
            PipelineStage.REQUIREMENT_ANALYSIS,
            PipelineStage.CALCULATION,
            PipelineStage.VALIDATION,
        ]
        
        if include_reasoning:
            workflow.stages.append(PipelineStage.REASONING)
        
        if include_optimization:
            workflow.stages.append(PipelineStage.OPTIMIZATION)
        
        workflow.stages.extend([
            PipelineStage.REPORTING,
            PipelineStage.APPROVAL
        ])
        
        # Initialize steps
        for stage in workflow.stages:
            step = WorkflowStep(stage=stage)
            workflow.steps.append(step)
        
        self.running_workflows[workflow.id] = workflow
        self.running_workflows[workflow.workflow_id] = workflow
        return workflow

    async def execute_workflow(
        self,
        workflow: EngineeringWorkflow,
        callbacks: Optional[Dict[str, Callable]] = None
    ) -> EngineeringWorkflow:
        """
        Execute complete workflow pipeline.
        
        callbacks: {
            "on_requirement_analysis": async fn(workflow),
            "on_calculation": async fn(workflow),
            "on_validation": async fn(workflow),
            ...
        }
        """
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        callbacks = callbacks or {}
        
        try:
            for i, stage in enumerate(workflow.stages):
                workflow.current_stage = i
                current_step = workflow.steps[i]
                current_step.status = WorkflowStatus.RUNNING
                current_step.started_at = datetime.utcnow()
                
                try:
                    # Execute stage-specific logic
                    if stage == PipelineStage.REQUIREMENT_ANALYSIS:
                        await self._execute_requirement_analysis(workflow, current_step, callbacks)
                    
                    elif stage == PipelineStage.CALCULATION:
                        await self._execute_calculation(workflow, current_step, callbacks)
                    
                    elif stage == PipelineStage.VALIDATION:
                        await self._execute_validation(workflow, current_step, callbacks)
                    
                    elif stage == PipelineStage.REASONING:
                        await self._execute_reasoning(workflow, current_step, callbacks)
                    
                    elif stage == PipelineStage.OPTIMIZATION:
                        await self._execute_optimization(workflow, current_step, callbacks)
                    
                    elif stage == PipelineStage.REPORTING:
                        await self._execute_reporting(workflow, current_step, callbacks)
                    
                    elif stage == PipelineStage.APPROVAL:
                        await self._execute_approval(workflow, current_step, callbacks)
                    
                    current_step.status = WorkflowStatus.COMPLETED
                    current_step.completed_at = datetime.utcnow()
                    current_step.duration_seconds = (
                        current_step.completed_at - current_step.started_at
                    ).total_seconds()
                
                except Exception as e:
                    current_step.status = WorkflowStatus.FAILED
                    current_step.error = str(e)
                    current_step.completed_at = datetime.utcnow()
                    
                    if not self._can_continue_after_error(stage):
                        workflow.status = WorkflowStatus.FAILED
                        workflow.metadata["error_stage"] = stage.value
                        workflow.metadata["error_message"] = str(e)
                        break
            
            workflow.status = WorkflowStatus.COMPLETED
        
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.metadata["error"] = str(e)
        
        finally:
            workflow.completed_at = datetime.utcnow()
            workflow.total_duration_seconds = (
                workflow.completed_at - workflow.started_at
            ).total_seconds()
        
        return workflow

    async def _execute_requirement_analysis(
        self,
        workflow: EngineeringWorkflow,
        step: WorkflowStep,
        callbacks: Dict[str, Callable]
    ):
        """Execute requirement analysis stage."""
        step.description = "Analyzing design requirements"
        
        if "on_requirement_analysis" in callbacks:
            await callbacks["on_requirement_analysis"](workflow)
        
        # Validate requirements exist
        if not workflow.metadata.get("requirements"):
            raise ValueError("No requirements provided for workflow")
        
        step.output_data["requirements_validated"] = True
        step.output_data["requirement_count"] = len(workflow.metadata.get("requirements", []))

    async def _execute_calculation(
        self,
        workflow: EngineeringWorkflow,
        step: WorkflowStep,
        callbacks: Dict[str, Callable]
    ):
        """Execute calculation stage."""
        step.description = "Performing engineering calculations"
        
        if "on_calculation" in callbacks:
            await callbacks["on_calculation"](workflow)
        
        # Mock calculation results
        step.output_data["calculations_completed"] = True
        step.output_data["calculation_count"] = 1
        
        # Update workflow with calculated values
        if "calculated_parameters" in step.output_data:
            workflow.design_metrics.update(step.output_data["calculated_parameters"])

    async def _execute_validation(
        self,
        workflow: EngineeringWorkflow,
        step: WorkflowStep,
        callbacks: Dict[str, Callable]
    ):
        """Execute validation stage."""
        step.description = "Validating design and calculations"
        
        if "on_validation" in callbacks:
            await callbacks["on_validation"](workflow)
        
        # Check for validation errors
        if step.output_data.get("validation_errors"):
            raise ValueError(f"Validation failed: {step.output_data['validation_errors']}")
        
        step.output_data["validation_passed"] = True

    async def _execute_reasoning(
        self,
        workflow: EngineeringWorkflow,
        step: WorkflowStep,
        callbacks: Dict[str, Callable]
    ):
        """Execute reasoning and decision stage."""
        step.description = "Performing engineering reasoning and decision analysis"
        
        if "on_reasoning" in callbacks:
            await callbacks["on_reasoning"](workflow)
        
        # Generate recommendations
        if "recommendations" in step.output_data:
            workflow.recommendations.extend(step.output_data["recommendations"])
        
        step.output_data["reasoning_completed"] = True

    async def _execute_optimization(
        self,
        workflow: EngineeringWorkflow,
        step: WorkflowStep,
        callbacks: Dict[str, Callable]
    ):
        """Execute optimization stage."""
        step.description = "Optimizing design parameters"
        
        if workflow.skip_optimization:
            step.status = WorkflowStatus.COMPLETED
            return
        
        if "on_optimization" in callbacks:
            await callbacks["on_optimization"](workflow)
        
        # Update design with optimized values
        if "optimized_parameters" in step.output_data:
            workflow.final_design.update(step.output_data["optimized_parameters"])
            workflow.design_metrics.update(step.output_data.get("metrics", {}))
        
        step.output_data["optimization_completed"] = True

    async def _execute_reporting(
        self,
        workflow: EngineeringWorkflow,
        step: WorkflowStep,
        callbacks: Dict[str, Callable]
    ):
        """Execute reporting stage."""
        step.description = "Generating engineering reports"
        
        if "on_reporting" in callbacks:
            await callbacks["on_reporting"](workflow)
        
        # Generate comprehensive report
        step.output_data["report_generated"] = True
        step.output_data["report_types"] = ["calculation", "validation", "optimization"]

    async def _execute_approval(
        self,
        workflow: EngineeringWorkflow,
        step: WorkflowStep,
        callbacks: Dict[str, Callable]
    ):
        """Execute approval stage."""
        step.description = "Final design approval and sign-off"
        
        if "on_approval" in callbacks:
            await callbacks["on_approval"](workflow)
        
        step.output_data["approval_status"] = "approved"
        workflow.metadata["approved_at"] = datetime.utcnow().isoformat()

    def _can_continue_after_error(self, stage: PipelineStage) -> bool:
        """Determine if workflow can continue after error in given stage."""
        # Critical stages that stop workflow
        critical_stages = [
            PipelineStage.VALIDATION,
            PipelineStage.APPROVAL
        ]
        return stage not in critical_stages

    async def generate_workflow_report(self, workflow: EngineeringWorkflow) -> Dict[str, Any]:
        """Generate workflow execution report."""
        return {
            "workflow_id": workflow.workflow_id,
            "design_name": workflow.design_name,
            "status": workflow.status.value,
            "total_duration_seconds": workflow.total_duration_seconds,
            "stages_completed": sum(1 for s in workflow.steps if s.status == WorkflowStatus.COMPLETED),
            "total_stages": len(workflow.stages),
            "steps": [
                {
                    "stage": s.stage.value,
                    "status": s.status.value,
                    "duration": s.duration_seconds,
                    "error": s.error
                }
                for s in workflow.steps
            ],
            "final_design_metrics": workflow.design_metrics,
            "recommendations": workflow.recommendations,
            "success": workflow.status == WorkflowStatus.COMPLETED
        }

    async def pause_workflow(self, workflow_id: Any) -> Optional[EngineeringWorkflow]:
        """Pause a running workflow."""
        if not isinstance(workflow_id, str):
            workflow_obj = workflow_id
            workflow_id = getattr(workflow_obj, "workflow_id", getattr(workflow_obj, "id", ""))
            
        if workflow_id in self.running_workflows:
            workflow = self.running_workflows[workflow_id]
            if workflow.status in [WorkflowStatus.RUNNING, WorkflowStatus.CREATED]:
                workflow.status = WorkflowStatus.PAUSED
                return workflow
        return None

    async def resume_workflow(
        self,
        workflow_id: Any,
        callbacks: Optional[Dict[str, Callable]] = None
    ) -> Optional[EngineeringWorkflow]:
        """Resume a paused workflow."""
        if not isinstance(workflow_id, str):
            workflow_obj = workflow_id
            workflow_id = getattr(workflow_obj, "workflow_id", getattr(workflow_obj, "id", ""))
            
        if workflow_id in self.running_workflows:
            workflow = self.running_workflows[workflow_id]
            if workflow.status == WorkflowStatus.PAUSED:
                workflow.status = WorkflowStatus.RUNNING
                # Continue from current stage
                return await self.execute_workflow(workflow, callbacks)
        return None

    async def cancel_workflow(self, workflow_id: Any) -> Optional[EngineeringWorkflow]:
        """Cancel a workflow."""
        if not isinstance(workflow_id, str):
            workflow_obj = workflow_id
            workflow_id = getattr(workflow_obj, "workflow_id", getattr(workflow_obj, "id", ""))
            
        if workflow_id in self.running_workflows:
            workflow = self.running_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.utcnow()
            return workflow
        return None

    async def list_workflows(self, status: Optional[WorkflowStatus] = None) -> List[EngineeringWorkflow]:
        """List workflows by status."""
        workflows = list(self.running_workflows.values())
        
        if status:
            workflows = [w for w in workflows if w.status == status]
        
        return workflows
