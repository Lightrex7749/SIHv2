"""
DrishtiSetu — Agentic AI / Capacity Safety Agent (Member 5)
Enforces non-negotiable deterministic carrying-capacity guardrails.
Architecture Reference: ARCHITECTURE.md §9B & MEMBER_5_AGENTIC_AI.md
"""

from typing import Dict, Any, Optional

DEFAULT_SAFETY_MARGIN = 0.90  # 90% usable threshold to prevent overcrowding


def calculate_capacity_sufficient(
    population_to_relocate: int,
    site_capacity: int,
    safety_margin: float = DEFAULT_SAFETY_MARGIN
) -> bool:
    """
    PURE DETERMINISTIC CALCULATION.
    Under NO circumstance may an LLM or neural model generate, alter,
    or override this boolean.
    """
    if site_capacity <= 0:
        return False
    usable_capacity = site_capacity * safety_margin
    return population_to_relocate <= usable_capacity


class CapacityAgent:
    def __init__(self, safety_margin: float = DEFAULT_SAFETY_MARGIN):
        self.safety_margin = safety_margin

    def evaluate(self, population_to_relocate: int, site_capacity: int) -> Dict[str, Any]:
        sufficient = calculate_capacity_sufficient(population_to_relocate, site_capacity, self.safety_margin)
        usable_capacity = int(site_capacity * self.safety_margin)
        deficit_surplus = usable_capacity - population_to_relocate
        
        return {
            "population_to_relocate": population_to_relocate,
            "site_capacity": site_capacity,
            "usable_capacity_with_margin": usable_capacity,
            "safety_margin": self.safety_margin,
            "capacity_sufficient": sufficient,
            "deficit_or_surplus": deficit_surplus,
            "guardrail_status": "ENFORCED_DETERMINISTIC"
        }

    def generate_reasoning_prompt_context(self, capacity_result: Dict[str, Any], adversarial_attempt: Optional[str] = None) -> str:
        """
        Injects the immutable ground-truth fact into the LLM system context.
        """
        is_suff = capacity_result["capacity_sufficient"]
        pop = capacity_result["population_to_relocate"]
        cap = capacity_result["site_capacity"]
        margin = capacity_result["safety_margin"]

        fact = (
            f"MANDATORY SAFETY FACT: The deterministic capacity calculation has established that "
            f"capacity_sufficient is strictly {str(is_suff).upper()}. "
            f"Population ({pop}) against site capacity ({cap} with {int(margin*100)}% safety margin). "
            f"You are strictly prohibited from stating or implying capacity is sufficient if capacity_sufficient is FALSE."
        )
        return fact
