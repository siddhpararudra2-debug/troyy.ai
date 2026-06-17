from functools import lru_cache
from jinja2 import Template

class TemplateEngine:
    def __init__(self):
        # Pre-load default templates for performance (<100ms retrieval)
        self._default_templates = {
            "AEROSPACE_CALCULATION": """# Engineering Calculation Report: {{ title }}
## 1. Problem Statement
{{ problem_statement }}

## 2. Requirements & Constraints
{{ requirements }}

## 3. Variables
- **Known**: {{ known_variables }}
- **Unknown**: {{ unknown_variables }}

## 4. Assumptions
{{ assumptions }}

## 5. Formula & Derivation
**Selected Formula:** {{ formula_selection }}
**Explanation:** {{ formula_explanation }}
**Unit Analysis:** {{ unit_analysis }}

## 6. Execution
**Substitution:** {{ substitution_steps }}
**Intermediate Steps:** {{ intermediate_calculations }}
**Final Result:** {{ final_results }}

## 7. Verification & Interpretation
**Verification:** {{ verification_results }}
**Engineering Interpretation:** {{ engineering_interpretation }}
**Recommendations:** {{ recommendations }}
""",
            "UAV_DESIGN": """# UAV Design Report
## Objective
{{ design_objective }}

## Architecture & Subsystems
{{ system_architecture }}

## Component Selections & Tradeoffs
{{ engineering_tradeoffs }}

## Final Design Summary
{{ final_design_summary }}
"""
        }

    @lru_cache(maxsize=128)
    def get_template(self, domain: str, template_type: str) -> str:
        key = f"{domain}_{template_type}".upper()
        return self._default_templates.get(key, self._default_templates.get("AEROSPACE_CALCULATION", ""))

    def render(self, domain: str, template_type: str, data: dict) -> str:
        template_str = self.get_template(domain, template_type)
        template = Template(template_str)
        return template.render(**data)
