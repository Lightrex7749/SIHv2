"""
DrishtiSetu — Carrying Capacity Analysis Module (Member 5)
Pure deterministic evaluation of candidate site carrying capacity against incoming population.
Reference: MEMBER_5_AGENTIC_AI.md & GLOBAL_AGENT_INSTRUCTIONS.md Rule 21
"""

from typing import Dict, Any
from agents.capacity_agent import calculate_capacity_sufficient, DEFAULT_SAFETY_MARGIN


def evaluate_site_capacity(
    population_to_relocate: int,
    site_capacity: int,
    safety_margin: float = DEFAULT_SAFETY_MARGIN
) -> Dict[str, Any]:
    """
    Deterministic carrying capacity check.
    Enforces that incoming population does not exceed usable site capacity.
    """
    sufficient = calculate_capacity_sufficient(population_to_relocate, site_capacity, safety_margin)
    usable_capacity = int(site_capacity * safety_margin)
    deficit_or_surplus = usable_capacity - population_to_relocate

    return {
        "population_to_relocate": population_to_relocate,
        "raw_site_capacity": site_capacity,
        "usable_capacity_at_safety_margin": usable_capacity,
        "safety_margin_percentage": int(safety_margin * 100),
        "capacity_sufficient": sufficient,
        "margin_headroom_persons": deficit_or_surplus,
        "rule_enforced": "population <= site_capacity * 0.90 (Deterministic Code Guardrail)"
    }
