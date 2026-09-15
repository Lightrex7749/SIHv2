"""
DrishtiSetu — Relocation Site Selection & Capacity Engine (Member 5)
Ranks candidate relocation sites, checks land-use conflicts, and estimates resettlement cost.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from gis.service import get_relocation_sites, get_habitation_by_id
from agents.capacity_agent import calculate_capacity_sufficient, CapacityAgent

# Real benchmark reference from DATA_SOURCES.md (Standard State/National Resettlement Norm: ₹50,000 per capita)
PER_CAPITA_RESETTLEMENT_BENCHMARK = 50000  # ₹50,000 / capita


class RecommendedSiteInfo(BaseModel):
    site_id: str
    name: str
    land_use_conflict: bool
    land_use_conflict_reason: Optional[str] = None


class RelocationRecommendResponse(BaseModel):
    habitation_id: str
    recommended_site: RecommendedSiteInfo
    suitability_score: float
    site_capacity: int
    population_to_relocate: int
    capacity_sufficient: bool
    estimated_cost: Optional[int] = None
    cost_basis: Optional[str] = None
    recommendation: str
    status: str = "PROPOSED"


class RelocationEngine:
    def __init__(self, cost_per_capita: int = PER_CAPITA_RESETTLEMENT_BENCHMARK):
        self.cost_per_capita = cost_per_capita
        self.capacity_agent = CapacityAgent()

    def recommend_site(self, habitation_id: str) -> RelocationRecommendResponse:
        habitation = get_habitation_by_id(habitation_id)
        if not habitation:
            raise ValueError(f"Habitation {habitation_id} not found in GIS database.")

        population = habitation["population"]
        candidate_sites = get_relocation_sites()
        region = habitation.get("region", "Chamoli")
        regional_sites = [site for site in candidate_sites if site.get("region", "Chamoli") == region]
        if regional_sites:
            candidate_sites = regional_sites

        # Ranking logic:
        # 1. Non-conflicting sites preferred over conflicting ones.
        # 2. Higher suitability score preferred.
        # 3. Sufficient capacity preferred.
        def rank_key(s):
            has_conflict = s.get("land_use_conflict", False)
            sufficient = calculate_capacity_sufficient(population, s["estimated_capacity"])
            # Penalize conflicting sites by -50 points
            score = s["suitability_score"]
            if has_conflict:
                score -= 50.0
            if not sufficient:
                score -= 20.0
            return score

        ranked = sorted(candidate_sites, key=rank_key, reverse=True)
        best_site = ranked[0] if ranked else None

        if not best_site:
            raise RuntimeError("No candidate relocation sites found in GIS database.")

        capacity_eval = self.capacity_agent.evaluate(population, best_site["estimated_capacity"])
        capacity_sufficient = capacity_eval["capacity_sufficient"]
        has_conflict = best_site.get("land_use_conflict", False)

        # Estimated cost calculation
        estimated_cost = population * self.cost_per_capita
        cost_basis = (
            f"{population} persons × ₹{self.cost_per_capita:,} per capita resettlement & infrastructure norm "
            f"(National Rehabilitation and Resettlement Policy benchmark, see docs/DATA_SOURCES.md)"
        )

        if has_conflict:
            recommendation = "UNSUITABLE_LAND_USE_CONFLICT"
        elif not capacity_sufficient:
            recommendation = "CAPACITY_DEFICIT_ALTERNATIVE_REQUIRED"
        elif best_site["suitability_score"] >= 75.0:
            recommendation = "SUITABLE"
        else:
            recommendation = "CONDITIONALLY_SUITABLE"

        return RelocationRecommendResponse(
            habitation_id=habitation_id,
            recommended_site=RecommendedSiteInfo(
                site_id=best_site["site_id"],
                name=best_site["name"],
                land_use_conflict=has_conflict,
                land_use_conflict_reason=best_site.get("land_use_conflict_reason")
            ),
            suitability_score=best_site["suitability_score"],
            site_capacity=best_site["estimated_capacity"],
            population_to_relocate=population,
            capacity_sufficient=capacity_sufficient,
            estimated_cost=estimated_cost,
            cost_basis=cost_basis,
            recommendation=recommendation,
            status="PROPOSED"
        )
