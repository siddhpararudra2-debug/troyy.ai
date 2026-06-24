"""
Improvement Planner — generates improvement plans based on capability gaps.
"""
from typing import Dict, List
from datetime import datetime, timedelta
from sprint11.self_improvement.capability_analyzer import CapabilityAnalyzer
from sprint11.schemas.models import ImprovementPlan

class ImprovementPlanner:
    """Plans agent improvement based on capability analysis."""
    
    # Improvement actions by capability
    IMPROVEMENT_ACTIONS = {
        "reasoning": [
            {"action": "practice_chain_of_thought", "effort": 1.0, "impact": 0.8},
            {"action": "study_logical_fallacies", "effort": 0.5, "impact": 0.5},
            {"action": "solve_puzzles", "effort": 0.7, "impact": 0.6},
        ],
        "coding": [
            {"action": "implement_algorithms", "effort": 1.0, "impact": 0.9},
            {"action": "code_review_practice", "effort": 0.5, "impact": 0.6},
            {"action": "refactor_exercises", "effort": 0.7, "impact": 0.7},
        ],
        "design": [
            {"action": "study_design_patterns", "effort": 0.8, "impact": 0.7},
            {"action": "analyze_case_studies", "effort": 0.6, "impact": 0.6},
            {"action": "iterate_on_designs", "effort": 1.0, "impact": 0.9},
        ],
        "planning": [
            {"action": "decompose_problems", "effort": 0.7, "impact": 0.7},
            {"action": "study_planning_methods", "effort": 0.5, "impact": 0.5},
            {"action": "practice_scheduling", "effort": 0.8, "impact": 0.8},
        ],
        "safety": [
            {"action": "study_failure_modes", "effort": 0.8, "impact": 0.9},
            {"action": "review_safety_cases", "effort": 0.6, "impact": 0.7},
            {"action": "simulate_hazards", "effort": 1.0, "impact": 0.8},
        ],
    }
    
    def __init__(self, capability_analyzer: CapabilityAnalyzer):
        self.capability_analyzer = capability_analyzer
        self.plans: Dict[str, ImprovementPlan] = {}
        
    def create_improvement_plan(self, agent_id: str,
                               required_capabilities: Dict[str, float] = None,
                               target_overall: float = 0.8) -> ImprovementPlan:
        """Create an improvement plan for an agent."""
        profile = self.capability_analyzer.get_agent_profile(agent_id)
        caps_by_name = {c["capability_name"]: c for c in profile["capabilities"]}
        
        # Identify gaps
        gaps = []
        if required_capabilities:
            for cap_name, required in required_capabilities.items():
                current = caps_by_name.get(cap_name, {}).get("score", 0.0)
                if current < required:
                    gaps.append((cap_name, current, required))
                    
        # Also check overall profile
        profile_vec = profile.get("profile_vector", [])
        if profile_vec:
            overall = sum(profile_vec) / len(profile_vec)
            if overall < target_overall:
                from sprint11.self_improvement.capability_analyzer import CapabilityAnalyzer
                for i, dim in enumerate(CapabilityAnalyzer.CAPABILITY_DIMENSIONS):
                    if i < len(profile_vec) and profile_vec[i] < target_overall:
                        current = profile_vec[i]
                        if not any(g[0] == dim for g in gaps):
                            gaps.append((dim, current, target_overall))
                            
        # Sort by priority (largest gap first)
        gaps.sort(key=lambda g: g[2] - g[1], reverse=True)
        
        # Generate actions
        actions = []
        for cap_name, current, target in gaps[:5]:  # Top 5 gaps
            cap_actions = self.IMPROVEMENT_ACTIONS.get(cap_name, [])
            if cap_actions:
                best = max(cap_actions, key=lambda a: a["impact"] / a["effort"])
                actions.append({
                    "capability": cap_name,
                    "action": best["action"],
                    "current_score": current,
                    "target_score": target,
                    "expected_impact": best["impact"],
                    "effort": best["effort"],
                    "estimated_completion_days": int(best["effort"] * 7)
                })
                
        # Create plan
        plan = ImprovementPlan(
            agent_id=agent_id,
            target_capability=gaps[0][0] if gaps else "overall",
            current_score=gaps[0][1] if gaps else 0.0,
            target_score=gaps[0][2] if gaps else target_overall,
            actions=actions
        )
        
        self.plans[plan.id] = plan
        return plan
        
    def get_plan(self, plan_id: str) -> Optional[ImprovementPlan]:
        return self.plans.get(plan_id)
        
    def list_plans(self, agent_id: str = None) -> List[ImprovementPlan]:
        plans = list(self.plans.values())
        if agent_id:
            plans = [p for p in plans if p.agent_id == agent_id]
        return plans
        
    def estimate_improvement_timeline(self, plan: ImprovementPlan) -> Dict:
        """Estimate timeline for plan completion."""
        if not plan.actions:
            return {"total_days": 0, "milestones": []}
            
        total_effort = sum(a["effort"] for a in plan.actions)
        total_days = int(total_effort * 7)  # 1 week per unit effort
        
        milestones = []
        cumulative_days = 0
        for action in plan.actions:
            cumulative_days += int(action["effort"] * 7)
            milestones.append({
                "action": action["action"],
                "capability": action["capability"],
                "completion_day": cumulative_days,
                "expected_score_after": min(1.0, action["current_score"] + action["expected_impact"] * 0.5)
            })
            
        return {
            "total_days": total_days,
            "total_effort": total_effort,
            "milestones": milestones,
            "estimated_completion": (datetime.utcnow() + timedelta(days=total_days)).isoformat()
        }
