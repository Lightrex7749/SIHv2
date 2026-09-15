"""
DrishtiSetu — ML / Risk Engine (Member 1)
Explainable Multi-Hazard Risk & Vulnerability Scoring Service
Formula Version: v1.0
Methodology Reference: docs/DATA_SOURCES.md#scoring-methodology
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RiskInput(BaseModel):
    habitation_id: str
    rainfall: float = Field(..., ge=0.0, description="Rainfall intensity in mm (e.g. 24h or peak)")
    elevation: float = Field(..., ge=0.0, description="Elevation in meters")
    slope: float = Field(..., ge=0.0, le=90.0, description="Slope gradient in degrees")
    population: int = Field(..., ge=0, description="Inhabitant count")
    historical_events: int = Field(..., ge=0, description="Recorded past disaster events")
    infrastructure_access_score: Optional[float] = Field(default=50.0, ge=0.0, le=100.0, description="Access index 0-100 where 100 is excellent")
    demographic_vulnerability: Optional[float] = Field(default=50.0, ge=0.0, le=100.0, description="Elderly/children/socio-economic index 0-100")


class FactorContribution(BaseModel):
    name: str
    contribution: float
    weight: float
    raw_value: Optional[float]


class RiskExplainResponse(BaseModel):
    habitation_id: str
    overall_score: float
    factors: List[FactorContribution]
    formula_version: str = "v1.0"
    methodology_reference: str = "docs/DATA_SOURCES.md#scoring-methodology"


class RiskAnalyzeResponse(BaseModel):
    habitation_id: str
    hazard_score: float
    vulnerability_score: float
    historical_score: float
    overall_score: float
    risk_level: str
    relocation_priority: str


# Documented Baseline Weights (Illustrative baseline per Section 9D of ARCHITECTURE.md)
# Hazard Sub-weights (sum to 1.0)
W_RAINFALL = 0.30
W_SLOPE = 0.25
W_ELEVATION_STABILITY = 0.20
W_HIST_FREQ = 0.25

# Vulnerability Sub-weights (sum to 1.0)
V_POPULATION = 0.40
V_INFRASTRUCTURE = 0.35
V_DEMOGRAPHIC = 0.25

# Overall Risk Component Weights (sum to 1.0)
ALPHA_HAZARD = 0.50
BETA_VULNERABILITY = 0.35
GAMMA_HISTORICAL = 0.15


def clamp(val: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(val, max_val))


def normalize_rainfall(rainfall_mm: float) -> float:
    # 0 to 200mm mapping to 0 - 100 (100mm+ in 24h is IMD Heavy/Very Heavy rain threshold)
    return clamp((rainfall_mm / 180.0) * 100.0)


def normalize_slope(slope_deg: float) -> float:
    # 0 to 40 degrees mapping to 0 - 100 (Himalayan shear failure begins at 25-30 deg)
    return clamp((slope_deg / 38.0) * 100.0)


def normalize_elevation_instability(elevation_m: float) -> float:
    # Elevation instability for Himalayan slopes (normalized against 2500m)
    return clamp((elevation_m / 2500.0) * 100.0)


def normalize_historical(events: int) -> float:
    # 0 to 6 historical events mapping to 0 - 100
    return clamp((events / 6.0) * 100.0)


def normalize_population(pop: int) -> float:
    # 0 to 2000 habitation population normalized to 0 - 100
    return clamp((pop / 2000.0) * 100.0)


def normalize_inverse_infra(access_score: float) -> float:
    # Lower access (isolated village) = higher vulnerability
    return clamp(100.0 - access_score)


def calculate_hazard_score(rainfall: float, slope: float, elevation: float, historical_events: int) -> float:
    h1 = normalize_rainfall(rainfall)
    h2 = normalize_slope(slope)
    h3 = normalize_elevation_instability(elevation)
    h4 = normalize_historical(historical_events)
    
    score = (W_RAINFALL * h1) + (W_SLOPE * h2) + (W_ELEVATION_STABILITY * h3) + (W_HIST_FREQ * h4)
    return round(clamp(score), 1)


def calculate_vulnerability_score(population: int, infrastructure_access: float, demographic_vuln: float) -> float:
    v1 = normalize_population(population)
    v2 = normalize_inverse_infra(infrastructure_access)
    v3 = clamp(demographic_vuln)
    
    score = (V_POPULATION * v1) + (V_INFRASTRUCTURE * v2) + (V_DEMOGRAPHIC * v3)
    return round(clamp(score), 1)


def calculate_overall_risk(hazard_score: float, vulnerability_score: float, historical_score: float) -> float:
    score = (ALPHA_HAZARD * hazard_score) + (BETA_VULNERABILITY * vulnerability_score) + (GAMMA_HISTORICAL * historical_score)
    return round(clamp(score), 1)


def classify_risk_level(overall_score: float) -> str:
    if overall_score >= 80.0:
        return "CRITICAL"
    elif overall_score >= 60.0:
        return "HIGH"
    elif overall_score >= 40.0:
        return "MODERATE"
    else:
        return "LOW"


def determine_relocation_priority(risk_level: str, overall_score: float) -> str:
    if risk_level == "CRITICAL" or overall_score >= 80.0:
        return "IMMEDIATE"
    elif risk_level == "HIGH" or overall_score >= 60.0:
        return "SHORT_TERM"
    elif risk_level == "MODERATE" or overall_score >= 40.0:
        return "LONG_TERM"
    else:
        return "MONITOR"


def assess_risk(data: RiskInput) -> RiskAnalyzeResponse:
    hist_score = round(normalize_historical(data.historical_events), 1)
    hazard = calculate_hazard_score(data.rainfall, data.slope, data.elevation, data.historical_events)
    vulnerability = calculate_vulnerability_score(
        data.population,
        data.infrastructure_access_score or 50.0,
        data.demographic_vulnerability or 50.0
    )
    overall = calculate_overall_risk(hazard, vulnerability, hist_score)
    risk_lvl = classify_risk_level(overall)
    priority = determine_relocation_priority(risk_lvl, overall)

    return RiskAnalyzeResponse(
        habitation_id=data.habitation_id,
        hazard_score=hazard,
        vulnerability_score=vulnerability,
        historical_score=hist_score,
        overall_score=overall,
        risk_level=risk_lvl,
        relocation_priority=priority
    )


def explain_risk_score(data: RiskInput) -> RiskExplainResponse:
    """
    Computes per-factor breakdown where weighted factor contributions
    sum approximately to the overall score.
    """
    hist_score = normalize_historical(data.historical_events)
    h1 = normalize_rainfall(data.rainfall)
    h2 = normalize_slope(data.slope)
    h3 = normalize_elevation_instability(data.elevation)
    h4 = hist_score
    
    v1 = normalize_population(data.population)
    v2 = normalize_inverse_infra(data.infrastructure_access_score or 50.0)
    v3 = clamp(data.demographic_vulnerability or 50.0)

    # Net contribution of each raw input factor to overall_score:
    # overall = ALPHA_HAZARD * (W1*h1 + W2*h2 + W3*h3 + W4*h4) 
    #         + BETA_VULN * (V1*v1 + V2*v2 + V3*v3)
    #         + GAMMA_HIST * hist_score
    c_rainfall = ALPHA_HAZARD * W_RAINFALL * h1
    c_slope = ALPHA_HAZARD * W_SLOPE * h2
    c_elevation = ALPHA_HAZARD * W_ELEVATION_STABILITY * h3
    c_hist_events = (ALPHA_HAZARD * W_HIST_FREQ * h4) + (GAMMA_HISTORICAL * hist_score)
    c_population = BETA_VULNERABILITY * V_POPULATION * v1
    c_infra = BETA_VULNERABILITY * V_INFRASTRUCTURE * v2
    c_demographic = BETA_VULNERABILITY * V_DEMOGRAPHIC * v3

    overall = round(c_rainfall + c_slope + c_elevation + c_hist_events + c_population + c_infra + c_demographic, 1)

    factors = [
        FactorContribution(name="rainfall_intensity", contribution=round(c_rainfall, 1), weight=round(ALPHA_HAZARD * W_RAINFALL, 3), raw_value=float(data.rainfall)),
        FactorContribution(name="slope", contribution=round(c_slope, 1), weight=round(ALPHA_HAZARD * W_SLOPE, 3), raw_value=float(data.slope)),
        FactorContribution(name="historical_event_frequency", contribution=round(c_hist_events, 1), weight=round((ALPHA_HAZARD * W_HIST_FREQ) + GAMMA_HISTORICAL, 3), raw_value=float(data.historical_events)),
        FactorContribution(name="population_density", contribution=round(c_population, 1), weight=round(BETA_VULNERABILITY * V_POPULATION, 3), raw_value=float(data.population)),
        FactorContribution(name="elevation_stability", contribution=round(c_elevation, 1), weight=round(ALPHA_HAZARD * W_ELEVATION_STABILITY, 3), raw_value=float(data.elevation)),
        FactorContribution(name="infrastructure_access", contribution=round(c_infra, 1), weight=round(BETA_VULNERABILITY * V_INFRASTRUCTURE, 3), raw_value=float(data.infrastructure_access_score or 50.0)),
        FactorContribution(name="demographic_vulnerability", contribution=round(c_demographic, 1), weight=round(BETA_VULNERABILITY * V_DEMOGRAPHIC, 3), raw_value=float(data.demographic_vulnerability or 50.0)),
    ]

    # Sort factors descending by contribution
    factors.sort(key=lambda f: f.contribution, reverse=True)

    return RiskExplainResponse(
        habitation_id=data.habitation_id,
        overall_score=overall,
        factors=factors,
        formula_version="v1.0",
        methodology_reference="docs/DATA_SOURCES.md#scoring-methodology"
    )
