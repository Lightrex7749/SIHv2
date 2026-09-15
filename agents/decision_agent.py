"""
DrishtiSetu — Agentic AI / Central Decision Agent (Member 5)
Synthesizes ML Risk, GIS Data, Relocation Analysis, Capacity Safety, and RAG Policy Evidence
into an explainable, structured decision recommendation.
Contract Reference: API_CONTRACT.md v2 §9
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from gis.service import get_habitation_by_id
from ml.risk_engine.scoring import RiskInput, assess_risk
from rag.api.handler import handle_rag_query


class HabitationSummary(BaseModel):
    id: str
    name: str
    population: int


class RiskSummary(BaseModel):
    hazard_score: float
    vulnerability_score: float
    overall_score: float
    risk_level: str
    relocation_priority: str


class RelocationSummary(BaseModel):
    recommended_site: str
    suitability_score: float
    capacity: int
    capacity_sufficient: bool
    land_use_conflict: bool
    estimated_cost: Optional[int] = None


class EvidenceItem(BaseModel):
    title: str
    source: str
    page: Optional[int] = None


class DecisionAnalyzeResponse(BaseModel):
    habitation: HabitationSummary
    risk: RiskSummary
    relocation: RelocationSummary
    reasoning: List[str]
    evidence: List[EvidenceItem]
    evidence_sufficient: bool
    recommendation: str


class DecisionAgent:
    def __init__(self):
        from relocation.site_selection import RelocationEngine
        self.relocation_engine = RelocationEngine()

    def analyze(self, habitation_id: str) -> DecisionAnalyzeResponse:
        habitation = get_habitation_by_id(habitation_id)
        if not habitation:
            raise ValueError(f"Habitation '{habitation_id}' not found.")

        # 1. ML Risk & Vulnerability Assessment
        risk_input = RiskInput(
            habitation_id=habitation["id"],
            rainfall=habitation.get("rainfall", 120.0),
            elevation=habitation.get("elevation", 1500.0),
            slope=habitation.get("slope", 30.0),
            population=habitation["population"],
            historical_events=habitation.get("historical_events", 3),
        )
        risk_result = assess_risk(risk_input)

        # 2. Relocation & Capacity Evaluation (Deterministic)
        relocation_result = self.relocation_engine.recommend_site(habitation["id"])

        # 3. RAG Policy Evidence Retrieval
        rag_query = f"What factors should be considered when planning relocation from a {habitation.get('hazard_type', 'landslide')}-prone habitation in the Himalayas?"
        rag_output = handle_rag_query(rag_query)

        # 4. Structured Reasoning Synthesis
        reasoning: List[str] = []
        if risk_result.risk_level in ["HIGH", "CRITICAL"]:
            reasoning.append(f"High multi-hazard risk detected ({risk_result.risk_level} — score {risk_result.overall_score})")
        else:
            reasoning.append(f"Moderate multi-hazard baseline ({risk_result.risk_level} — score {risk_result.overall_score})")

        if risk_result.vulnerability_score >= 60.0:
            reasoning.append(f"High population vulnerability ({habitation['population']} inhabitants exposed with terrain isolation)")

        if relocation_result.capacity_sufficient:
            reasoning.append(
                f"Candidate site ({relocation_result.recommended_site.name}) has sufficient carrying capacity "
                f"({relocation_result.population_to_relocate} vs {relocation_result.site_capacity} capacity)"
            )
        else:
            reasoning.append(
                f"WARNING: Candidate site exhibits capacity deficit "
                f"({relocation_result.population_to_relocate} population exceeds safety threshold of {relocation_result.site_capacity})"
            )

        if not relocation_result.recommended_site.land_use_conflict:
            reasoning.append("No land-use conflict detected on candidate site (clear of eco-sensitive/forest zones)")
        else:
            reasoning.append(f"LAND-USE CONFLICT FLAGGED: {relocation_result.recommended_site.land_use_conflict_reason}")

        if relocation_result.suitability_score >= 80.0:
            reasoning.append(f"Candidate site possesses high composite accessibility and infrastructure suitability ({relocation_result.suitability_score}%)")

        # 5. Recommendation Formulations
        if risk_result.relocation_priority == "IMMEDIATE" and relocation_result.capacity_sufficient and not relocation_result.recommended_site.land_use_conflict:
            rec_text = "PRIORITIZE IMMEDIATE RELOCATION PLANNING"
        elif risk_result.relocation_priority == "SHORT_TERM" and relocation_result.capacity_sufficient:
            rec_text = "RECOMMEND PHASED RELOCATION MASTER PLAN"
        elif relocation_result.recommended_site.land_use_conflict:
            rec_text = "SELECT ALTERNATE SITE DUE TO ECO-SENSITIVE LAND-USE CONFLICT"
        elif not relocation_result.capacity_sufficient:
            rec_text = "MULTIPLE RECEPTION SITES REQUIRED DUE TO POPULATION DEFICIT"
        else:
            rec_text = "MONITOR HAZARD THRESHOLDS AND MAINTAIN EARLY WARNING READINESS"

        # Evidence parsing
        evidence_items = []
        for s in rag_output.get("sources", []):
            evidence_items.append(EvidenceItem(
                title=s.get("title", "Disaster Management Guideline"),
                source=s.get("source", "NDMA / MoRD"),
                page=s.get("page")
            ))

        return DecisionAnalyzeResponse(
            habitation=HabitationSummary(
                id=habitation["id"],
                name=habitation["name"],
                population=habitation["population"]
            ),
            risk=RiskSummary(
                hazard_score=risk_result.hazard_score,
                vulnerability_score=risk_result.vulnerability_score,
                overall_score=risk_result.overall_score,
                risk_level=risk_result.risk_level,
                relocation_priority=risk_result.relocation_priority
            ),
            relocation=RelocationSummary(
                recommended_site=relocation_result.recommended_site.site_id,
                suitability_score=relocation_result.suitability_score,
                capacity=relocation_result.site_capacity,
                capacity_sufficient=relocation_result.capacity_sufficient,
                land_use_conflict=relocation_result.recommended_site.land_use_conflict,
                estimated_cost=relocation_result.estimated_cost
            ),
            reasoning=reasoning,
            evidence=evidence_items,
            evidence_sufficient=rag_output.get("evidence_sufficient", True),
            recommendation=rec_text
        )
