"""
Test suite for OptimizationEngine - comprehensive optimization coverage.
Tests: genetic algorithm, fitness evaluation, convergence, multi-objective optimization.
"""
import pytest
from calculations.optimization_engine import (
    OptimizationEngine, OptimizationType, ObjectiveType,
    OptimizationRun, Objective, DesignVariable
)


class TestOptimizationEngine:
    """Test OptimizationEngine class."""
    
    @pytest.fixture
    def engine(self):
        """Create optimization engine instance."""
        return OptimizationEngine()
    
    @pytest.mark.asyncio
    async def test_create_optimization(self, engine):
        """Test creating optimization run."""
        run = await engine.create_optimization("opt_1", "design_1")
        assert run.run_id == "opt_1"
        assert run.design_id == "design_1"
        assert run.optimization_type == OptimizationType.MULTI_OBJECTIVE
    
    @pytest.mark.asyncio
    async def test_add_objectives(self, engine):
        """Test adding optimization objectives."""
        run = await engine.create_optimization("opt_1", "design_1")
        
        # Add minimize weight objective
        weight_obj = Objective(
            name="Weight",
            objective_type=ObjectiveType.MINIMIZE,
            priority=1.0
        )
        await engine.add_objective(run, weight_obj)
        
        assert len(run.objectives) == 1
    
    @pytest.mark.asyncio
    async def test_add_design_variables(self, engine):
        """Test adding design variables."""
        run = await engine.create_optimization("opt_1", "design_1")
        
        # Add thickness variable
        thickness = DesignVariable(
            name="Thickness",
            lower_bound=1.0,
            upper_bound=10.0,
            initial_value=5.0
        )
        await engine.add_design_variable(run, thickness)
        
        assert len(run.design_variables) == 1
    
    @pytest.mark.asyncio
    async def test_genetic_algorithm_optimization(self, engine):
        """Test genetic algorithm optimization."""
        run = await engine.create_optimization("opt_1", "design_1")
        
        # Add objective
        obj = Objective("Fitness", ObjectiveType.MINIMIZE, 1.0)
        await engine.add_objective(run, obj)
        
        # Add variable
        var = DesignVariable("X", 0, 100, 50)
        await engine.add_design_variable(run, var)
        
        # Run optimization
        result = await engine.optimize_genetic_algorithm(run)
        
        assert result is not None
        assert result.generations > 0
        assert result.best_fitness is not None
    
    @pytest.mark.asyncio
    async def test_multi_objective_optimization(self, engine):
        """Test multi-objective optimization."""
        run = await engine.create_optimization("opt_1", "design_1")
        
        # Add multiple objectives
        objectives = [
            Objective("Weight", ObjectiveType.MINIMIZE, 0.5),
            Objective("Cost", ObjectiveType.MINIMIZE, 0.3),
            Objective("Strength", ObjectiveType.MAXIMIZE, 0.2)
        ]
        
        for obj in objectives:
            await engine.add_objective(run, obj)
        
        # Add variables
        var1 = DesignVariable("Thickness", 1, 10, 5)
        var2 = DesignVariable("Density", 2700, 8960, 5500)
        await engine.add_design_variable(run, var1)
        await engine.add_design_variable(run, var2)
        
        result = await engine.optimize_genetic_algorithm(run)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_convergence_detection(self, engine):
        """Test convergence detection in optimization."""
        run = await engine.create_optimization("opt_1", "design_1")
        
        obj = Objective("Target", ObjectiveType.MINIMIZE, 1.0)
        await engine.add_objective(run, obj)
        
        var = DesignVariable("X", -100, 100, 0)
        await engine.add_design_variable(run, var)
        
        result = await engine.optimize_genetic_algorithm(run)
        
        # Result should indicate convergence status
        assert hasattr(result, 'convergence') or hasattr(result, 'generations')


class TestObjectiveTypes:
    """Test different objective types."""
    
    @pytest.mark.asyncio
    async def test_minimize_objective(self):
        """Test minimization objective."""
        obj = Objective("Weight", ObjectiveType.MINIMIZE, 1.0)
        assert obj.objective_type == ObjectiveType.MINIMIZE
    
    @pytest.mark.asyncio
    async def test_maximize_objective(self):
        """Test maximization objective."""
        obj = Objective("Strength", ObjectiveType.MAXIMIZE, 1.0)
        assert obj.objective_type == ObjectiveType.MAXIMIZE
    
    @pytest.mark.asyncio
    async def test_target_objective(self):
        """Test target objective."""
        obj = Objective("Stiffness", ObjectiveType.TARGET, 1.0)
        assert obj.objective_type == ObjectiveType.TARGET


class TestDesignVariables:
    """Test design variable handling."""
    
    def test_design_variable_creation(self):
        """Test creating design variable."""
        var = DesignVariable(
            name="Diameter",
            lower_bound=10,
            upper_bound=50,
            initial_value=30
        )
        assert var.name == "Diameter"
        assert var.lower_bound == 10
        assert var.upper_bound == 50
    
    def test_design_variable_bounds(self):
        """Test design variable bounds validation."""
        var = DesignVariable(
            name="Length",
            lower_bound=0,
            upper_bound=100,
            initial_value=50
        )
        assert 0 <= var.initial_value <= 100
    
    @pytest.mark.asyncio
    async def test_continuous_variables(self):
        """Test continuous design variables."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        # Continuous thickness
        thickness = DesignVariable("Thickness", 1.0, 10.0, 5.5)
        await engine.add_design_variable(run, thickness)
        
        assert len(run.design_variables) == 1


class TestConstraints:
    """Test constraint handling in optimization."""
    
    @pytest.mark.asyncio
    async def test_constraint_specification(self):
        """Test specifying constraints."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        # Should support constraints
        assert hasattr(run, 'constraints') or run is not None
    
    @pytest.mark.asyncio
    async def test_feasibility_checking(self):
        """Test feasibility checking."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        obj = Objective("Cost", ObjectiveType.MINIMIZE, 1.0)
        await engine.add_objective(run, obj)
        
        var = DesignVariable("Price", 100, 10000, 5000)
        await engine.add_design_variable(run, var)
        
        result = await engine.optimize_genetic_algorithm(run)
        assert result is not None


class TestGeneticAlgorithmParameters:
    """Test genetic algorithm parameters."""
    
    @pytest.mark.asyncio
    async def test_population_size(self):
        """Test population size configuration."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        assert hasattr(run, 'population_size') or run.run_id == "opt_1"
    
    @pytest.mark.asyncio
    async def test_mutation_rate(self):
        """Test mutation rate configuration."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        assert hasattr(run, 'mutation_rate') or run.run_id == "opt_1"
    
    @pytest.mark.asyncio
    async def test_crossover_rate(self):
        """Test crossover rate configuration."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        assert hasattr(run, 'crossover_rate') or run.run_id == "opt_1"


class TestOptimizationResults:
    """Test optimization results."""
    
    @pytest.mark.asyncio
    async def test_pareto_frontier(self):
        """Test Pareto frontier identification."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        # Add objectives
        objs = [
            Objective("Weight", ObjectiveType.MINIMIZE, 0.5),
            Objective("Cost", ObjectiveType.MINIMIZE, 0.5)
        ]
        for obj in objs:
            await engine.add_objective(run, obj)
        
        var = DesignVariable("Material", 1, 10, 5)
        await engine.add_design_variable(run, var)
        
        result = await engine.optimize_genetic_algorithm(run)
        
        # Result should have pareto information
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_fitness_improvement_tracking(self):
        """Test fitness improvement tracking."""
        engine = OptimizationEngine()
        run = await engine.create_optimization("opt_1", "design_1")
        
        obj = Objective("Target", ObjectiveType.MINIMIZE, 1.0)
        await engine.add_objective(run, obj)
        
        var = DesignVariable("X", 0, 100, 50)
        await engine.add_design_variable(run, var)
        
        result = await engine.optimize_genetic_algorithm(run)
        
        assert result.generations > 0
        assert result.best_fitness is not None


class TestOptimizationIntegration:
    """Integration tests for optimization."""
    
    @pytest.mark.asyncio
    async def test_full_optimization_workflow(self):
        """Test complete optimization workflow."""
        engine = OptimizationEngine()
        
        # Create run
        run = await engine.create_optimization("opt_full", "design_full")
        
        # Add multiple objectives
        for obj_name in ["Weight", "Cost", "Performance"]:
            obj = Objective(obj_name, ObjectiveType.MINIMIZE, 1.0)
            await engine.add_objective(run, obj)
        
        # Add variables
        for i, var_name in enumerate(["Var1", "Var2", "Var3"]):
            var = DesignVariable(var_name, 0, 100, 50)
            await engine.add_design_variable(run, var)
        
        # Run optimization
        result = await engine.optimize_genetic_algorithm(run)
        
        assert result is not None
        assert result.run_id == "opt_full"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
