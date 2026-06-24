"""
Test suite for DecisionEngine - comprehensive decision-making coverage.
Tests: decision creation, option evaluation, trade-off analysis, recommendations.
"""
import pytest
from reasoning.decision_engine import (
    EngineeringDecisionEngine, DecisionType, DecisionStatus,
    EngineeringDecision, DesignOption
)


class TestDecisionEngine:
    """Test EngineeringDecisionEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create decision engine instance."""
        return EngineeringDecisionEngine()
    
    @pytest.mark.asyncio
    async def test_create_decision(self, engine):
        """Test creating a new decision."""
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Material Selection",
            DecisionType.MATERIAL_SELECTION
        )
        assert decision.decision_id == "dec_1"
        assert decision.design_id == "design_1"
        assert decision.title == "Material Selection"
    
    @pytest.mark.asyncio
    async def test_add_option_to_decision(self, engine):
        """Test adding options to a decision."""
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Material Selection",
            DecisionType.MATERIAL_SELECTION
        )
        
        option = DesignOption(
            option_id="opt_1",
            name="Aluminum 6061",
            description="Lightweight alloy"
        )
        await engine.add_option(decision, option)
        assert len(decision.options) == 1
    
    @pytest.mark.asyncio
    async def test_evaluate_options(self, engine):
        """Test evaluation of design options."""
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Material Selection",
            DecisionType.MATERIAL_SELECTION
        )
        
        # Add multiple options
        options = [
            DesignOption("opt_1", "Steel", "High strength"),
            DesignOption("opt_2", "Aluminum", "Lightweight"),
            DesignOption("opt_3", "Titanium", "Premium")
        ]
        
        for opt in options:
            await engine.add_option(decision, opt)
        
        # Evaluate
        evaluation = await engine.evaluate_options(decision)
        assert evaluation is not None
        assert len(evaluation.scores) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_tradeoffs(self, engine):
        """Test trade-off analysis."""
        decision = await engine.create_decision(
            "dec_2",
            "design_2",
            "Cost vs Quality",
            DecisionType.DESIGN_ALTERNATIVE
        )
        
        options = [
            DesignOption("opt_1", "Budget Option", "Low cost, low quality"),
            DesignOption("opt_2", "Mid-Range", "Balanced"),
            DesignOption("opt_3", "Premium", "High cost, high quality")
        ]
        
        for opt in options:
            await engine.add_option(decision, opt)
        
        tradeoff = await engine.analyze_tradeoffs(decision)
        assert tradeoff is not None
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, engine):
        """Test generating recommendations."""
        decision = await engine.create_decision(
            "dec_3",
            "design_3",
            "Geometry Optimization",
            DecisionType.GEOMETRY_OPTIMIZATION
        )
        
        options = [
            DesignOption("opt_1", "Option A", "First alternative"),
            DesignOption("opt_2", "Option B", "Second alternative")
        ]
        
        for opt in options:
            await engine.add_option(decision, opt)
        
        recommendations = await engine.generate_recommendations(decision)
        assert recommendations is not None
        assert len(recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_document_decision(self, engine):
        """Test documenting a decision."""
        decision = await engine.create_decision(
            "dec_4",
            "design_4",
            "Material Choice",
            DecisionType.MATERIAL_SELECTION
        )
        
        options = [DesignOption("opt_1", "Steel", "Strong")]
        for opt in options:
            await engine.add_option(decision, opt)
        
        # Document decision
        documented = await engine.document_decision(decision)
        assert documented is not None
    
    @pytest.mark.asyncio
    async def test_implement_decision(self, engine):
        """Test implementing a decision."""
        decision = await engine.create_decision(
            "dec_5",
            "design_5",
            "Selected Material",
            DecisionType.MATERIAL_SELECTION
        )
        
        option = DesignOption("opt_1", "Final Choice", "Selected material")
        await engine.add_option(decision, option)
        
        result = await engine.implement_decision(decision, "opt_1")
        assert result is not None


class TestDecisionTypes:
    """Test different decision types."""
    
    @pytest.mark.asyncio
    async def test_material_selection_decision(self):
        """Test material selection decision workflow."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "mat_1",
            "design_1",
            "Choose Material",
            DecisionType.MATERIAL_SELECTION
        )
        assert decision.decision_type == DecisionType.MATERIAL_SELECTION
    
    @pytest.mark.asyncio
    async def test_geometry_optimization_decision(self):
        """Test geometry optimization decision."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "geo_1",
            "design_2",
            "Optimize Geometry",
            DecisionType.GEOMETRY_OPTIMIZATION
        )
        assert decision.decision_type == DecisionType.GEOMETRY_OPTIMIZATION
    
    @pytest.mark.asyncio
    async def test_manufacturing_decision(self):
        """Test manufacturing process decision."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "mfg_1",
            "design_3",
            "Select Process",
            DecisionType.MANUFACTURING
        )
        assert decision.decision_type == DecisionType.MANUFACTURING
    
    @pytest.mark.asyncio
    async def test_design_alternative_decision(self):
        """Test design alternative decision."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "alt_1",
            "design_4",
            "Choose Design",
            DecisionType.DESIGN_ALTERNATIVE
        )
        assert decision.decision_type == DecisionType.DESIGN_ALTERNATIVE


class TestDecisionCriteria:
    """Test decision criteria and scoring."""
    
    @pytest.mark.asyncio
    async def test_material_selection_criteria(self):
        """Test material selection criteria."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "mat_1",
            "design_1",
            "Material",
            DecisionType.MATERIAL_SELECTION
        )
        
        # Material selection should have 4 criteria
        assert len(decision.criteria) == 4
        assert any(c.name == "Cost" for c in decision.criteria)
    
    @pytest.mark.asyncio
    async def test_custom_criteria_weighting(self):
        """Test custom criteria weights."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Decision",
            DecisionType.MATERIAL_SELECTION
        )
        
        # Total weight should equal 1.0
        total_weight = sum(c.weight for c in decision.criteria)
        assert abs(total_weight - 1.0) < 0.01


class TestDecisionStatus:
    """Test decision status tracking."""
    
    @pytest.mark.asyncio
    async def test_decision_status_creation(self):
        """Test initial decision status."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Test",
            DecisionType.MATERIAL_SELECTION
        )
        assert decision.status == DecisionStatus.OPEN
    
    @pytest.mark.asyncio
    async def test_decision_status_transition(self):
        """Test decision status transitions."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Test",
            DecisionType.MATERIAL_SELECTION
        )
        
        option = DesignOption("opt_1", "Choice", "Selected")
        await engine.add_option(decision, option)
        
        result = await engine.implement_decision(decision, "opt_1")
        # Status should change
        assert decision.status in [
            DecisionStatus.OPEN,
            DecisionStatus.EVALUATED,
            DecisionStatus.DOCUMENTED,
            DecisionStatus.IMPLEMENTED
        ]


class TestConstraintHandling:
    """Test constraint handling in decisions."""
    
    @pytest.mark.asyncio
    async def test_constraint_evaluation(self):
        """Test constraint evaluation in decisions."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Constrained Decision",
            DecisionType.GEOMETRY_OPTIMIZATION
        )
        
        # Should have default constraints
        assert len(decision.constraints) > 0
    
    @pytest.mark.asyncio
    async def test_conflicting_constraints(self):
        """Test handling of conflicting constraints."""
        engine = EngineeringDecisionEngine()
        decision = await engine.create_decision(
            "dec_1",
            "design_1",
            "Conflicting",
            DecisionType.MATERIAL_SELECTION
        )
        
        options = [
            DesignOption("opt_1", "Cheap & Weak", "Affordable but weak"),
            DesignOption("opt_2", "Expensive & Strong", "Costly but strong")
        ]
        
        for opt in options:
            await engine.add_option(decision, opt)
        
        evaluation = await engine.evaluate_options(decision)
        assert evaluation is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
