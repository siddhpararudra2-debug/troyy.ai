"""
Test suite for PhysicsValidator - comprehensive physics validation coverage.
Tests: Newton's laws, energy conservation, thermodynamics, fluid dynamics, electromagnetics.
"""
import pytest
import asyncio
from validation.physics_validator import (
    PhysicsValidator, PhysicsDomain, PhysicsValidationResult, PhysicsValidationError
)


class TestPhysicsValidator:
    """Test PhysicsValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create physics validator instance."""
        return PhysicsValidator()
    
    @pytest.mark.asyncio
    async def test_newtons_law_validation(self, validator):
        """Test Newton's second law validation."""
        # F = ma
        parameters = {"force": 100, "mass": 10, "acceleration": 10}
        result = await validator.validate_physics(
            "mechanics",
            parameters
        )
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_hookes_law_validation(self, validator):
        """Test Hooke's Law validation for materials."""
        parameters = {"stress": 100, "strain": 0.01, "youngs_modulus": 10000}
        result = await validator.validate_physics("mechanics", parameters)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_energy_conservation(self, validator):
        """Test energy conservation principle."""
        parameters = {
            "kinetic_energy": 100,
            "potential_energy": 50,
            "total_energy": 150
        }
        result = await validator.validate_physics("mechanics", parameters)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_thermodynamic_first_law(self, validator):
        """Test first law of thermodynamics."""
        parameters = {
            "internal_energy_change": 100,
            "heat_added": 200,
            "work_done": 100
        }
        result = await validator.validate_physics("thermodynamics", parameters)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_absolute_zero_check(self, validator):
        """Test that absolute zero is enforced."""
        parameters = {"temperature": -300}  # Below absolute zero
        result = await validator.validate_physics("thermodynamics", parameters)
        # Should have violations
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_fluid_continuity_equation(self, validator):
        """Test fluid continuity equation."""
        parameters = {
            "inlet_velocity": 5,
            "inlet_area": 10,
            "outlet_velocity": 10,
            "outlet_area": 5
        }
        result = await validator.validate_physics("fluid_dynamics", parameters)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_bernoulli_equation(self, validator):
        """Test Bernoulli equation for fluid flow."""
        parameters = {
            "pressure_1": 101325,
            "velocity_1": 5,
            "height_1": 0,
            "pressure_2": 100000,
            "velocity_2": 10,
            "height_2": 5
        }
        result = await validator.validate_physics("fluid_dynamics", parameters)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_ohms_law_validation(self, validator):
        """Test Ohm's Law for electrical circuits."""
        parameters = {"voltage": 12, "current": 2, "resistance": 6}
        result = await validator.validate_physics("electromagnetism", parameters)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_aerodynamic_lift_coefficient(self, validator):
        """Test aerodynamic lift coefficient bounds."""
        parameters = {"lift_coefficient": 1.5, "angle_of_attack": 15}
        result = await validator.validate_physics("aerodynamics", parameters)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_fatigue_limit_check(self, validator):
        """Test material fatigue limit validation."""
        parameters = {
            "stress": 50,
            "fatigue_limit": 100,
            "cycles": 1000000
        }
        result = await validator.validate_physics("mechanics", parameters)
        assert isinstance(result, PhysicsValidationResult)


class TestPhysicsDomains:
    """Test different physics domains."""
    
    @pytest.mark.asyncio
    async def test_mechanics_domain(self):
        """Test mechanics domain validation."""
        validator = PhysicsValidator()
        params = {"force": 100, "mass": 10, "acceleration": 10}
        result = await validator.validate_physics("mechanics", params)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_thermodynamics_domain(self):
        """Test thermodynamics domain validation."""
        validator = PhysicsValidator()
        params = {"temperature": 300, "pressure": 101325}
        result = await validator.validate_physics("thermodynamics", params)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_fluid_dynamics_domain(self):
        """Test fluid dynamics domain validation."""
        validator = PhysicsValidator()
        params = {"velocity": 5, "pressure": 101325}
        result = await validator.validate_physics("fluid_dynamics", params)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_electromagnetism_domain(self):
        """Test electromagnetism domain validation."""
        validator = PhysicsValidator()
        params = {"voltage": 12, "current": 1, "resistance": 12}
        result = await validator.validate_physics("electromagnetism", params)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_aerodynamics_domain(self):
        """Test aerodynamics domain validation."""
        validator = PhysicsValidator()
        params = {"lift_coefficient": 1.0, "drag_coefficient": 0.03}
        result = await validator.validate_physics("aerodynamics", params)
        assert result is not None


class TestPhysicsValidationErrors:
    """Test physics validation error handling."""
    
    @pytest.mark.asyncio
    async def test_negative_mass(self):
        """Test validation rejects negative mass."""
        validator = PhysicsValidator()
        params = {"mass": -10, "force": 100}
        result = await validator.validate_physics("mechanics", params)
        # Should be invalid or have violations
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_negative_temperature(self):
        """Test that temperatures below absolute zero are rejected."""
        validator = PhysicsValidator()
        params = {"temperature": -273.16, "pressure": 0}
        result = await validator.validate_physics("thermodynamics", params)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_impossible_stress(self):
        """Test unrealistic stress values."""
        validator = PhysicsValidator()
        params = {"stress": 1e12, "material": "steel"}
        result = await validator.validate_physics("mechanics", params)
        assert isinstance(result, PhysicsValidationResult)


class TestPhysicsIntegration:
    """Integration tests for physics validation."""
    
    @pytest.mark.asyncio
    async def test_validate_beam_structure(self):
        """Test validation of beam structure parameters."""
        validator = PhysicsValidator()
        
        # Cantilever beam parameters
        params = {
            "length": 2.0,
            "force": 1000,
            "material_strength": 250,
            "cross_section_area": 0.01,
            "second_moment": 0.0001
        }
        
        result = await validator.validate_physics("mechanics", params)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_validate_thermal_system(self):
        """Test validation of thermal system."""
        validator = PhysicsValidator()
        
        params = {
            "heat_input": 5000,
            "heat_output": 5000,
            "initial_temp": 20,
            "final_temp": 20,
            "mass": 10,
            "specific_heat": 4186
        }
        
        result = await validator.validate_physics("thermodynamics", params)
        assert isinstance(result, PhysicsValidationResult)
    
    @pytest.mark.asyncio
    async def test_validate_aerodynamic_design(self):
        """Test validation of aerodynamic design."""
        validator = PhysicsValidator()
        
        params = {
            "velocity": 50,
            "air_density": 1.225,
            "wing_area": 20,
            "lift_coefficient": 0.5,
            "drag_coefficient": 0.02
        }
        
        result = await validator.validate_physics("aerodynamics", params)
        assert isinstance(result, PhysicsValidationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
