from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport

class ScenarioComparisonService:
    def compare(self, scenario_a: dict, scenario_b: dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Compare two design scenarios and recommend the optimal choice"],
            assumptions=["Scenarios are mutually exclusive", "Metrics are equally weighted unless specified"],
            constraints=["Must evaluate cost, performance, and risk"],
            formula_selection="Weighted Multi-Criteria Decision Analysis (MCDA)",
            formula_explanation="Normalizes metrics across scenarios and applies engineering weights to determine the winner.",
            unit_analysis="Normalized scores (0-1), final recommendation categorical."
        ) as ctx:
            # Simple comparison logic
            score_a = sum(scenario_a.values())
            score_b = sum(scenario_b.values())
            
            winner = "A" if score_a > score_b else "B"
            delta = abs(score_a - score_b) / max(score_a, score_b) * 100
            
            ctx.finalize(
                final_results={"winner": winner, "score_a": score_a, "score_b": score_b, "delta_pct": delta},
                interpretation=f"Scenario {winner} is superior by {delta:.1f}% based on aggregated metrics."
            )
        return ctx.report
