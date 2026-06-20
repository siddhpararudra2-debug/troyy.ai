from app.schematic_engine.schemas.engineering_report import ReportContext, EngineeringReport

class PinMappingService:
    def assign_pins(self, mcu_pinout: dict, required_functions: dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Assign MCU physical pins to required peripheral functions without conflicts"],
            assumptions=["Each physical pin can only be assigned to one function", "Alternate functions are mutually exclusive per pin"],
            constraints=["No pin collisions", "All required functions must be mapped"],
            formula_selection="Constraint Satisfaction Problem (CSP) via Backtracking",
            formula_explanation="Uses depth-first search with backtracking to find a valid variable assignment.",
            unit_analysis="Pins and functions are categorical variables."
        ) as ctx:
            # Flatten available pins for each function
            func_to_pins = {}
            for pin, funcs in mcu_pinout.items():
                for f in funcs:
                    func_to_pins.setdefault(f, []).append(pin)
                    
            # Check basic feasibility
            for func, count in required_functions.items():
                if func not in func_to_pins or len(func_to_pins[func]) < count:
                    raise ValueError(f"ERC ERROR: Insufficient pins for function {func}. Required: {count}, Available: {len(func_to_pins.get(func, []))}")
                    
            # Backtracking solver
            assignment = {}
            used_pins = set()
            
            def backtrack(func_list, idx):
                if idx == len(func_list):
                    return True
                func = func_list[idx]
                for pin in func_to_pins[func]:
                    if pin not in used_pins:
                        assignment[func] = pin
                        used_pins.add(pin)
                        if backtrack(func_list, idx + 1):
                            return True
                        used_pins.remove(pin)
                        del assignment[func]
                return False
                
            func_list = []
            for func, count in required_functions.items():
                func_list.extend([func] * count)
                
            if not backtrack(func_list, 0):
                raise ValueError("ERC ERROR: No valid pin mapping exists (constraint conflict).")
                
            ctx.add_intermediate("CSP Resolution", "Backtracking Search", {"assignments": len(assignment)})
            
            ctx.finalize(
                final_results={"pin_mapping": assignment, "unassigned_pins": list(set(mcu_pinout.keys()) - used_pins)},
                interpretation=f"Successfully mapped {len(assignment)} functions. {len(set(mcu_pinout.keys()) - used_pins)} pins remain available for future expansion."
            )
        return ctx.report
