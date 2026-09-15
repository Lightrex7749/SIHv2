"""
DrishtiSetu RAG/NLP module — FastAPI route.

Implements POST /api/v1/rag/query exactly per API_CONTRACT.md v2 section 7,
including the `evidence_sufficient` field. Owned module: /rag/. Does not touch
/ml/, /computer_vision/, /gis/, /agents/, or /frontend/, per
GLOBAL_AGENT_INSTRUCTIONS.md rule 8 and MEMBER_4_RAG_NLP.md ownership.

This file is a thin wrapper around api/handler.py's handle_rag_query(), which
contains the actual, already-tested retrieval + generation logic. See
handler.py's module docstring for why the split exists (fastapi/pydantic were
not installable in tonight's sandboxed build environment — no outbound network).

Mode selection via the RAG_MODE environment variable ("mock" or "real", default
"real") — see MEMBER_4_RAG_NLP.md "Mock Mode".

Run (once fastapi/uvicorn are installed — see requirements.txt):
    uvicorn api.main:app --reload --port 8004
Member 6's backend skeleton would instead mount this router at /api/v1/rag/*.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from api.handler import handle_rag_query

app = FastAPI(title="DrishtiSetu RAG/NLP Service")


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class SourceItem(BaseModel):
    title: str
    source: str
    page: int | None = None


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    evidence_sufficient: bool


@app.post("/api/v1/rag/query", response_model=RagQueryResponse)
def rag_query(request: RagQueryRequest) -> RagQueryResponse:
    result = handle_rag_query(request.question)
    return RagQueryResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok", "service": "drishtisetu-rag"}
