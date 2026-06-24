"""
Hypothesis Generator — generates testable engineering hypotheses.
"""
from typing import Dict, List
import random
from sprint11.schemas.models import Hypothesis

class HypothesisGenerator:
    """Generates testable hypotheses from problem statements."""
    
    # Domain-specific hypothesis templates
    TEMPLATES = {
        "AEROSPACE": [
            "A {config} wing configuration will improve L/D by {pct}% at cruise",
            "Using {material} instead of {baseline} will reduce structural mass by {pct}%",
            "Implementing {control} control will reduce tracking error by {pct}%",
            "A {propulsion} propulsion system will increase range by {pct}%",
        ],
        "ROBOTICS": [
            "A {mechanism} mechanism will increase workspace volume by {pct}%",
            "Using {actuator} actuators will improve bandwidth to {value} Hz",
            "Implementing {control} control will reduce settling time by {pct}%",
            "A {gripper} gripper will handle objects from {min_size} to {max_size} mm",
        ],
        "ELECTRONICS": [
            "A {topology} converter topology will achieve {pct}% efficiency at {power}W",
            "Using {filter} filtering will reduce noise by {db} dB",
            "A {architecture} PCB architecture will reduce EMI by {db} dB",
            "{component} placement strategy will reduce thermal hotspot by {delta_t}°C",
        ],
        "MANUFACTURING": [
            "{process} process will reduce cycle time by {pct}%",
            "Using {tool} tooling will improve surface finish to {roughness} Ra",
            "{strategy} strategy will reduce material waste by {pct}%",
            "{automation} automation will increase throughput by {pct}%",
        ],
    }
    
    # Feature pools for template filling
    FEATURE_POOLS = {
        "AEROSPACE": {
            "config": ["blended-wing-body", "box-wing", "canard", "tail-sitter"],
            "material": ["carbon composite", "titanium alloy", "aluminum-lithium"],
            "baseline": ["aluminum 6061", "steel", "fiberglass"],
            "control": ["adaptive", "MPC", "gain-scheduled", "neural"],
            "propulsion": ["hybrid-electric", "hydrogen fuel cell", "distributed"],
        },
        "ROBOTICS": {
            "mechanism": ["parallel", "cable-driven", "continuum", "soft"],
            "actuator": ["quasi-direct-drive", "SEA", "hydraulic", "piezo"],
            "control": ["impedance", "adaptive", "robust", "learning-based"],
            "gripper": ["soft pneumatic", "underactuated", "magnetic", "vacuum"],
        },
        "ELECTRONICS": {
            "topology": ["active clamp flyback", "LLC resonant", "buck-boost", "push-pull"],
            "filter": ["LC pi", "common mode choke", "active ripple cancelation"],
            "architecture": ["4-layer coplanar", "star-grounded", "split ground-plane"],
            "component": ["centralized power stage", "symmetrical path", "decoupled thermal"],
        },
        "MANUFACTURING": {
            "process": ["high-speed machining", "additive-subtle hybrid", "lean layout"],
            "tool": ["coated carbide", "polycrystalline diamond", "ceramic insert"],
            "strategy": ["nesting optimization", "near-net-shape casting", "sheet layout"],
            "automation": ["collaborative robots", "AGV logistics", "smart vision sorting"],
        }
    }

    def generate(self, project_id: str, domain: str, count: int = 3) -> List[Hypothesis]:
        """Generate testable hypotheses for a given project and domain."""
        domain = domain.upper()
        if domain not in self.TEMPLATES:
            domain = "ROBOTICS"  # Default domain
            
        templates = self.TEMPLATES[domain]
        pool = self.FEATURE_POOLS[domain]
        
        hypotheses = []
        for _ in range(min(count, len(templates))):
            template = random.choice(templates)
            
            # Format arguments
            kwargs = {}
            for placeholder in pool.keys():
                if f"{{{placeholder}}}" in template:
                    kwargs[placeholder] = random.choice(pool[placeholder])
                    
            # Numerical placeholders
            if "{pct}" in template:
                kwargs["pct"] = random.randint(10, 40)
            if "{value}" in template:
                kwargs["value"] = random.randint(50, 200)
            if "{db}" in template:
                kwargs["db"] = random.randint(6, 20)
            if "{delta_t}" in template:
                kwargs["delta_t"] = random.randint(5, 25)
            if "{power}" in template:
                kwargs["power"] = random.randint(50, 500)
            if "{min_size}" in template:
                kwargs["min_size"] = random.randint(1, 10)
            if "{max_size}" in template:
                kwargs["max_size"] = random.randint(50, 200)
            if "{roughness}" in template:
                kwargs["roughness"] = round(random.uniform(0.4, 3.2), 1)
                
            statement = template.format(**kwargs)
            
            hypothesis = Hypothesis(
                project_id=project_id,
                statement=statement,
                rationale=f"Based on historical optimization patterns and performance characteristics in the {domain.lower()} domain.",
                testable_predictions=[
                    f"Testing this configuration will yield measurable improvement over baseline standard configurations.",
                    f"Measured variance will fall within acceptable statistical confidence limits."
                ]
            )
            hypotheses.append(hypothesis)
            
        return hypotheses
