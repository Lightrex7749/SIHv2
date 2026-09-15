"""
DrishtiSetu — Central FastAPI Integration Backend (Member 6)
Integrates ML Risk Engine, Computer Vision, GIS Data, RAG/NLP, and Agentic Relocation
Full compliance with API Contract (v2).
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is on Python sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# Module 1: ML Risk & Explainability
from ml.risk_engine.scoring import (
    RiskInput,
    assess_risk,
    explain_risk_score,
    RiskAnalyzeResponse,
    RiskExplainResponse,
)

# Module 2: Computer Vision Router
from computer_vision import vision_router

# Module 3: GIS Layers & Data
from gis.service import (
    get_habitations,
    get_habitation_by_id,
    get_layer_geojson,
    get_risk_layers_manifest,
    get_relocation_sites,
    get_flood_reference_points,
    get_flood_reference_areas,
)

# Module 4: RAG Query Handler
from rag.api.handler import handle_rag_query

# Module 5: Relocation & Decision Agent
from relocation.site_selection import RelocationEngine, RelocationRecommendResponse
from agents.decision_agent import DecisionAgent, DecisionAnalyzeResponse

# Decision Audit Log
from backend.drishti_db import log_authority_decision, get_decision_history, get_all_decision_logs
from backend.routes.admin import router as admin_router
from backend.routes.community import community_router
from backend.routes.disasters import disasters_router
from backend.routes.location import location_router
from backend.routes.profile import profile_router
from backend.routes.risk import risk_router
from backend.routes.scientist import scientist_router
from backend.routes.telegram import telegram_router
from backend.routes.weather import weather_router

# Create FastAPI App
app = FastAPI(
    title="DrishtiSetu Disaster Relocation Decision-Support Platform",
    description="AI-driven, GIS-enabled multi-hazard relocation decision-support system (SIH 2026)",
    version="2.0.0",
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Computer Vision router (POST /api/v1/vision/analyze)
app.include_router(vision_router)

# Mount the operational APIs consumed by the frontend dashboard.
app.include_router(admin_router)
app.include_router(community_router)
app.include_router(disasters_router)
app.include_router(location_router)
app.include_router(profile_router)
app.include_router(risk_router)
app.include_router(scientist_router)
app.include_router(telegram_router)
app.include_router(weather_router)

decision_agent = DecisionAgent()
relocation_engine = RelocationEngine()


# -------------------------------------------------------------
# Section 9C: Security Deferral Stub for Future RBAC
# -------------------------------------------------------------
async def get_current_user_stub():
    """
    FastAPI dependency injection stub for future RBAC authentication.
    Currently returns an authorized District Officer identity for MVP scope.
    """
    return {
        "user_id": "OFFICER_CHAMOLI_01",
        "name": "District Disaster Management Officer",
        "role": "DISTRICT_OFFICER",
        "district": "Chamoli",
    }


# -------------------------------------------------------------
# 1. Health Check
# -------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "drishtisetu"
    }


# -------------------------------------------------------------
# 2. Habitations
# -------------------------------------------------------------
@app.get("/api/v1/habitations", tags=["Habitations"])
async def list_habitations():
    return get_habitations()


@app.get("/api/v1/habitations/{habitation_id}", tags=["Habitations"])
async def get_habitation(habitation_id: str):
    hab = get_habitation_by_id(habitation_id)
    if not hab:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "HABITATION_NOT_FOUND", "message": f"Habitation {habitation_id} was not found."}}
        )
    return hab


# -------------------------------------------------------------
# 3. Risk Analysis & Explainability (Module 1)
# -------------------------------------------------------------
@app.post("/api/v1/risk/analyze", response_model=RiskAnalyzeResponse, tags=["Risk Engine"])
async def analyze_risk(data: RiskInput):
    return assess_risk(data)


@app.get("/api/v1/risk/explain/{habitation_id}", response_model=RiskExplainResponse, tags=["Risk Engine"])
async def explain_risk(habitation_id: str):
    hab = get_habitation_by_id(habitation_id)
    if not hab:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "HABITATION_NOT_FOUND", "message": f"Habitation {habitation_id} was not found."}}
        )
    risk_input = RiskInput(
        habitation_id=hab["id"],
        rainfall=hab.get("rainfall", 120.0),
        elevation=hab.get("elevation", 1500.0),
        slope=hab.get("slope", 30.0),
        population=hab["population"],
        historical_events=hab.get("historical_events", 3),
        infrastructure_access_score=hab.get("infrastructure_access_score", 45.0),
        demographic_vulnerability=hab.get("vulnerability_score", 60.0),
    )
    return explain_risk_score(risk_input)


# -------------------------------------------------------------
# 5 & 6. GIS Risk Layers (Module 3)
# -------------------------------------------------------------
@app.get("/api/v1/gis/risk-layers", tags=["GIS"])
async def get_risk_layers():
    return get_risk_layers_manifest()


@app.get("/api/v1/gis/layers/{layer_name}", tags=["GIS"])
async def get_gis_layer(layer_name: str):
    return get_layer_geojson(layer_name)


@app.get("/api/v1/gis/flood-reference-points", tags=["GIS"])
async def get_flood_points():
    return get_flood_reference_points()


@app.get("/api/v1/gis/flood-reference-areas", tags=["GIS"])
async def get_flood_areas():
    return get_flood_reference_areas()


# -------------------------------------------------------------
# 7. RAG Knowledge Query (Module 4)
# -------------------------------------------------------------
class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Disaster management or relocation query")


@app.post("/api/v1/rag/query", tags=["RAG / NLP"])
async def query_rag(payload: RAGQueryRequest):
    return handle_rag_query(payload.question)


# -------------------------------------------------------------
# 8. Relocation Recommendation (Module 5)
# -------------------------------------------------------------
class RelocationRecommendRequest(BaseModel):
    habitation_id: str


@app.post("/api/v1/relocation/recommend", response_model=RelocationRecommendResponse, tags=["Relocation"])
async def recommend_relocation(payload: RelocationRecommendRequest):
    try:
        return relocation_engine.recommend_site(payload.habitation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "HABITATION_NOT_FOUND", "message": str(e)}}
        )


# -------------------------------------------------------------
# 9. Main Decision Analysis Pipeline (Module 5 Central)
# -------------------------------------------------------------
class DecisionAnalyzeRequest(BaseModel):
    habitation_id: str


@app.post("/api/v1/decision/analyze", response_model=DecisionAnalyzeResponse, tags=["Decision Support"])
async def analyze_decision(payload: DecisionAnalyzeRequest):
    try:
        return decision_agent.analyze(payload.habitation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "HABITATION_NOT_FOUND", "message": str(e)}}
        )


# -------------------------------------------------------------
# 9A. Authority Decision Audit Log (NEW — Required Feature)
# -------------------------------------------------------------
class DecisionLogRequest(BaseModel):
    habitation_id: str
    recommendation_id: Optional[str] = None
    reviewed_by: str = Field(..., min_length=2, description="Reviewing official name/title")
    decision: str = Field(..., pattern="^(ACCEPTED|REJECTED|DEFERRED)$", description="ACCEPTED, REJECTED, or DEFERRED")
    notes: Optional[str] = Field(default="", description="Authority action rationale or execution directives")


@app.post("/api/v1/decision/log", tags=["Authority Decision Log"])
async def record_decision_action(
    payload: DecisionLogRequest,
    current_user: dict = Depends(get_current_user_stub)
):
    """
    Permanently logs an authorized official's review action on a recommendation.
    Append-only audit trail guaranteeing human accountability.
    """
    entry = log_authority_decision(
        habitation_id=payload.habitation_id,
        decision=payload.decision,
        reviewed_by=payload.reviewed_by,
        recommendation_id=payload.recommendation_id,
        notes=payload.notes
    )
    return entry


@app.get("/api/v1/decision/log", tags=["Authority Decision Log"])
async def list_all_decision_logs():
    """
    Retrieves full chronological audit trail across all habitations.
    """
    return get_all_decision_logs()


@app.get("/api/v1/decision/log/{habitation_id}", tags=["Authority Decision Log"])
async def get_decision_audit_trail(habitation_id: str):
    """
    Retrieves chronological history of all decisions taken for a habitation.
    """
    return get_decision_history(habitation_id)


# -------------------------------------------------------------
# 10. AI Consultation & Decision Advisory (OpenRouter nemotron-3)
# -------------------------------------------------------------
class AIConsultRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language disaster management query")
    habitation_id: Optional[str] = Field(default=None, description="Optional habitation ID context")


@app.post("/api/v1/ai/consult", tags=["AI Advisory"])
async def consult_ai_advisor(payload: AIConsultRequest):
    """
    Consults DrishtiSetu AI Disaster Relocation Advisor powered by
    nvidia/nemotron-3-ultra-550b-a55b via OpenRouter.
    """
    from backend.ai_service import generate_ai_consultation

    hab_context = None
    dec_context = None
    if payload.habitation_id:
        hab_context = get_habitation_by_id(payload.habitation_id)
        try:
            dec = decision_agent.analyze(payload.habitation_id)
            dec_context = dec.model_dump()
        except Exception:
            pass

    return generate_ai_consultation(
        query=payload.query,
        habitation_context=hab_context,
        decision_context=dec_context
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
