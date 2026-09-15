"""
DrishtiSetu — Risk Agent (Member 5)
Consumes hazard indicators, slope, rainfall, and historical disaster frequency.
"""

from typing import Dict, Any
from ml.risk_engine.scoring import RiskInput, assess_risk, explain_risk_score


class RiskAgent:
    def evaluate(self, habitation_data: Dict[str, Any]) -> Dict[str, Any]:
        risk_input = RiskInput(
            habitation_id=habitation_data["id"],
            rainfall=float(habitation_data.get("rainfall", 120.0)),
            elevation=float(habitation_data.get("elevation", 1800.0)),
            slope=float(habitation_data.get("slope", 30.0)),
            population=int(habitation_data.get("population", 1000)),
            historical_events=int(habitation_data.get("historical_events", 2)),
            infrastructure_access_score=float(habitation_data.get("infrastructure_score", 50.0)),
            demographic_vulnerability=float(habitation_data.get("demographic_score", 50.0))
        )
        assessment = assess_risk(risk_input)
        explanation = explain_risk_score(risk_input)

        return {
            "habitation_id": assessment.habitation_id,
            "overall_score": assessment.overall_score,
            "risk_level": assessment.risk_level,
            "relocation_priority": assessment.relocation_priority,
            "hazard_score": assessment.hazard_score,
            "factors": [f.model_dump() for f in explanation.factors],
            "formula_version": explanation.formula_version
        }
