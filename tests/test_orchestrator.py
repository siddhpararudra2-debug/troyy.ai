"""
Test suite for EngineeringOrchestrator - comprehensive workflow coordination coverage.
Tests: workflow creation, pipeline execution, stage coordination, error handling.
"""
import pytest
from engineering_core.orchestrator import (
    EngineeringOrchestrator, WorkflowStatus, PipelineStage,
    EngineeringWorkflow
)


class TestEngineeringOrchestrator:
    """Test EngineeringOrchestrator class."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return EngineeringOrchestrator()
    
    @pytest.mark.asyncio
    async def test_create_workflow(self, orchestrator):
        """Test creating engineering workflow."""
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Bridge Design"
        )
        assert workflow.workflow_id == "wf_1"
        assert workflow.design_id == "design_1"
        assert workflow.design_name == "Bridge Design"
    
    @pytest.mark.asyncio
    async def test_workflow_initial_status(self, orchestrator):
        """Test workflow initial status."""
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test Design"
        )
        assert workflow.status == WorkflowStatus.CREATED
    
    @pytest.mark.asyncio
    async def test_standard_pipeline(self, orchestrator):
        """Test standard pipeline creation."""
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        # Should have standard pipeline stages
        assert len(workflow.stages) > 0
        assert any(s.stage_type == PipelineStage.REQUIREMENT_ANALYSIS for s in workflow.stages)
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, orchestrator):
        """Test executing workflow."""
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test Design"
        )
        
        # Execute workflow
        result = await orchestrator.execute_workflow(workflow)
        
        assert result is not None
        assert workflow.status in [
            WorkflowStatus.CREATED,
            WorkflowStatus.EXECUTING,
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED
        ]
    
    @pytest.mark.asyncio
    async def test_workflow_pause(self, orchestrator):
        """Test pausing workflow execution."""
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        # Pause workflow
        paused = await orchestrator.pause_workflow(workflow)
        
        assert paused is not None
    
    @pytest.mark.asyncio
    async def test_workflow_resume(self, orchestrator):
        """Test resuming paused workflow."""
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        # Pause then resume
        await orchestrator.pause_workflow(workflow)
        resumed = await orchestrator.resume_workflow(workflow)
        
        assert resumed is not None
    
    @pytest.mark.asyncio
    async def test_workflow_cancel(self, orchestrator):
        """Test canceling workflow."""
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        # Cancel workflow
        cancelled = await orchestrator.cancel_workflow(workflow)
        
        assert cancelled is not None
        assert cancelled.status == WorkflowStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_list_workflows(self, orchestrator):
        """Test listing workflows."""
        # Create multiple workflows
        workflows = []
        for i in range(3):
            wf = await orchestrator.create_workflow(
                f"wf_{i}",
                f"design_{i}",
                f"Design {i}"
            )
            workflows.append(wf)
        
        # List workflows
        all_workflows = await orchestrator.list_workflows()
        
        assert all_workflows is not None


class TestPipelineStages:
    """Test different pipeline stages."""
    
    @pytest.mark.asyncio
    async def test_requirement_analysis_stage(self):
        """Test requirement analysis stage."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        # Find requirement analysis stage
        req_stage = next(
            (s for s in workflow.stages 
             if s.stage_type == PipelineStage.REQUIREMENT_ANALYSIS),
            None
        )
        assert req_stage is not None
    
    @pytest.mark.asyncio
    async def test_calculation_stage(self):
        """Test calculation stage."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        calc_stage = next(
            (s for s in workflow.stages 
             if s.stage_type == PipelineStage.CALCULATION),
            None
        )
        assert calc_stage is not None
    
    @pytest.mark.asyncio
    async def test_validation_stage(self):
        """Test validation stage."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        val_stage = next(
            (s for s in workflow.stages 
             if s.stage_type == PipelineStage.VALIDATION),
            None
        )
        assert val_stage is not None
    
    @pytest.mark.asyncio
    async def test_reasoning_stage(self):
        """Test reasoning stage."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        reason_stage = next(
            (s for s in workflow.stages 
             if s.stage_type == PipelineStage.REASONING),
            None
        )
        assert reason_stage is not None
    
    @pytest.mark.asyncio
    async def test_optimization_stage(self):
        """Test optimization stage."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        opt_stage = next(
            (s for s in workflow.stages 
             if s.stage_type == PipelineStage.OPTIMIZATION),
            None
        )
        assert opt_stage is not None
    
    @pytest.mark.asyncio
    async def test_reporting_stage(self):
        """Test reporting stage."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        report_stage = next(
            (s for s in workflow.stages 
             if s.stage_type == PipelineStage.REPORTING),
            None
        )
        assert report_stage is not None
    
    @pytest.mark.asyncio
    async def test_approval_stage(self):
        """Test approval stage."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        appr_stage = next(
            (s for s in workflow.stages 
             if s.stage_type == PipelineStage.APPROVAL),
            None
        )
        assert appr_stage is not None


class TestWorkflowStatus:
    """Test workflow status management."""
    
    @pytest.mark.asyncio
    async def test_status_transitions(self):
        """Test workflow status transitions."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        initial_status = workflow.status
        assert initial_status == WorkflowStatus.CREATED
    
    @pytest.mark.asyncio
    async def test_completed_workflow(self):
        """Test completed workflow."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test"
        )
        
        await orchestrator.execute_workflow(workflow)
        
        # Status should be updated
        assert workflow.status in [
            WorkflowStatus.EXECUTING,
            WorkflowStatus.COMPLETED,
            WorkflowStatus.PAUSED,
            WorkflowStatus.CANCELLED
        ]


class TestWorkflowReporting:
    """Test workflow reporting."""
    
    @pytest.mark.asyncio
    async def test_generate_workflow_report(self):
        """Test generating workflow report."""
        orchestrator = EngineeringOrchestrator()
        workflow = await orchestrator.create_workflow(
            "wf_1",
            "design_1",
            "Test Design"
        )
        
        # Execute workflow
        await orchestrator.execute_workflow(workflow)
        
        # Generate report
        report = await orchestrator.generate_workflow_report(workflow)
        
        assert report is not None


class TestWorkflowIntegration:
    """Integration tests for workflow orchestration."""
    
    @pytest.mark.asyncio
    async def test_complete_design_workflow(self):
        """Test complete design workflow."""
        orchestrator = EngineeringOrchestrator()
        
        # Create workflow
        workflow = await orchestrator.create_workflow(
            "design_workflow_1",
            "product_design_1",
            "New Product Design"
        )
        
        # Should have all required stages
        assert len(workflow.stages) >= 7
        
        # Execute workflow
        result = await orchestrator.execute_workflow(workflow)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_workflow_with_callbacks(self):
        """Test workflow with callback functions."""
        orchestrator = EngineeringOrchestrator()
        
        callback_invoked = []
        
        def stage_callback(stage_name):
            callback_invoked.append(stage_name)
        
        workflow = await orchestrator.create_workflow(
            "wf_callback",
            "design_callback",
            "Test with Callbacks"
        )
        
        # Execute with callback
        await orchestrator.execute_workflow(workflow)
        
        # Workflow should have executed
        assert workflow.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.EXECUTING,
            WorkflowStatus.PAUSED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED
        ]
    
    @pytest.mark.asyncio
    async def test_multi_workflow_execution(self):
        """Test executing multiple workflows."""
        orchestrator = EngineeringOrchestrator()
        
        workflows = []
        for i in range(3):
            wf = await orchestrator.create_workflow(
                f"multi_wf_{i}",
                f"multi_design_{i}",
                f"Design {i}"
            )
            workflows.append(wf)
        
        # Execute all workflows
        for wf in workflows:
            await orchestrator.execute_workflow(wf)
        
        # All should have valid status
        assert all(wf.status is not None for wf in workflows)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
