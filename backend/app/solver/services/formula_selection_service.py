"""
Troy — Formula Selection Service
Queries the central formula registry, evaluates formula relevance for the
given variables, and sequences them so that inputs are resolved sequentially.

Performance target: <100 ms.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Set

from app.calculations.registry import registry
from app.solver.models.domain_models import FormulaSelectionData, VariableData

logger = logging.getLogger("solver.services.formula_selection")


class FormulaSelectionService:
    """Selects and sequences formulas to resolve unknown engineering variables."""

    async def select_formulas(
        self,
        domain: str,
        variables: VariableData,
    ) -> List[FormulaSelectionData]:
        """
        Query the FormulaRegistry, score formulas by how many unknowns they can
        resolve, and return a dependency-ordered list of selections.
        """
        # Start with variables we already have values for
        known_names: Set[str] = set()
        known_names.update(variables.known.keys())
        known_names.update(variables.derived.keys())
        known_names.update(variables.constants.keys())

        # Unknowns we want to resolve
        target_unknowns = set(variables.unknown)

        logger.debug(f"Target unknowns: {target_unknowns}, Knowns: {known_names}")

        # Get all formulas for this domain (or all if multi-domain)
        all_formulas = registry.list_all()
        if domain != "multi":
            domain_formulas = registry.list_by_domain(domain)
        else:
            domain_formulas = all_formulas

        # Let's perform a multi-pass dependency resolution to chain formulas.
        # In each pass, we check which formulas can be executed (all parameters resolved)
        # and resolve their outputs, adding them to the resolved set.
        resolved = set(known_names)
        # Also map alias symbols/names to resolve mismatches if any
        # (e.g. m_total -> m, thrust_total -> T, f_safety -> f_safety, etc.)
        self._add_common_aliases(resolved)

        selected_formulas: List[FormulaSelectionData] = []
        unused_formulas = list(domain_formulas)
        
        # Limit to prevent infinite loops
        max_passes = 10
        for pass_idx in range(max_passes):
            progressed = False
            executable_in_this_pass = []

            for f in list(unused_formulas):
                # Check if all parameters are resolved (or have defaults)
                unresolved_params = []
                for p in f.parameters:
                    # check parameter name or symbol
                    p_names = [p.name, p.symbol]
                    # Also clean symbol of LaTeX backslashes or curly braces
                    clean_sym = p.symbol.replace("\\", "").replace("{", "").replace("}", "")
                    p_names.append(clean_sym)
                    
                    if not any(name in resolved for name in p_names) and p.default is None:
                        unresolved_params.append(p.name)

                if not unresolved_params:
                    # Formula is executable!
                    # Calculate relevance score based on outputs matching target unknowns
                    matching_outputs = [o.name for o in f.outputs if o.name in target_unknowns]
                    
                    # If it resolves an unknown or contributes to the chain, select it
                    # (we also allow intermediate formulas even if their outputs aren't directly in unknown)
                    relevance = 1.0 if matching_outputs else 0.5
                    
                    executable_in_this_pass.append((f, relevance))
                    unused_formulas.remove(f)
                    progressed = True

            if not progressed:
                break

            # Sort by relevance to execute the most useful first
            executable_in_this_pass.sort(key=lambda x: x[1], reverse=True)

            for f, relevance in executable_in_this_pass:
                # Add outputs to resolved set
                for o in f.outputs:
                    resolved.add(o.name)
                    # Add standard aliases
                    self._add_common_aliases(resolved)

                dependencies = []
                for p in f.parameters:
                    dependencies.append(p.name)

                selected_formulas.append(
                    FormulaSelectionData(
                        formula_id=f.id,
                        name=f.name,
                        relevance_score=relevance,
                        reasoning=f"Resolves {', '.join(o.name for o in f.outputs)} using {', '.join(p.name for p in f.parameters)}.",
                        required_inputs=[p.name for p in f.parameters],
                        expected_outputs=[o.name for o in f.outputs],
                        dependencies=dependencies,
                    )
                )

        logger.info(
            f"Selected {len(selected_formulas)} formulas for domain={domain}"
        )
        return selected_formulas

    def _add_common_aliases(self, resolved: Set[str]) -> None:
        """Map common engineering variable names/symbols to ensure chaining."""
        aliases = [
            ("m_payload", "m"),
            ("m_total", "m"),
            ("m", "T"),             # In simple drone equations, thrust = weight
            ("T_total", "T"),
            ("f_safety", "f_safety"),
            ("capacity_mah", "capacity_mah"),
            ("voltage", "voltage"),
            ("eta", "eta"),
            ("P_hover", "P"),       # Power hover mapping
            ("arm_length", "arm_length"),
            ("L", "L"),
            ("D", "D"),
            ("q", "q"),
            ("v", "v"),
            ("rho", "rho"),
            ("S", "S"),
            ("C_L", "C_L"),
            ("C_D", "C_D"),
            ("Re", "Re"),
            ("M", "M"),
        ]
        for src, dest in aliases:
            if src in resolved:
                resolved.add(dest)
            if dest in resolved:
                resolved.add(src)
