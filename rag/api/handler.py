"""
DrishtiSetu RAG/NLP module — framework-agnostic query handler.

Why this file exists: tonight's build sandbox has no outbound network, so
`pip install fastapi uvicorn pydantic` (per requirements.txt) could not be run here
— those packages are not present in this container (see README.md "Limitations").
Rather than leave the pipeline unexercised, the actual retrieval + generation logic
lives here as a plain Python function with no framework dependency, and
api/main.py's FastAPI route is a thin wrapper around it (see the `_handle` call in
main.py). This means:
  * The pipeline shown in this repo has genuinely been run end-to-end tonight
    (see tests/test_rag.py and the README's worked examples), not just written.
  * Once fastapi/uvicorn/pydantic are installed in a real dev/CI environment
    (`pip install -r requirements.txt`), api/main.py runs unchanged on top of the
    same handler — nothing here needs to change.

Returns a plain dict matching API_CONTRACT.md v2 section 7 exactly:
    {"answer": str, "sources": [{"title", "source", "page"}], "evidence_sufficient": bool}
"""

import os

try:
    from generation.generator import generate_answer
    from retrieval.retriever import Retriever
except ImportError:
    from rag.generation.generator import generate_answer
    from rag.retrieval.retriever import Retriever

_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


_MOCK_FOUND_KEYWORDS = ("relocation", "landslide", "habitation")


def _mock_response(question: str) -> dict:
    if any(k in question.lower() for k in _MOCK_FOUND_KEYWORDS):
        return {
            "answer": (
                "[MOCK] Relocation planning from a landslide-prone habitation should "
                "weigh hazard zonation, site suitability and capacity, land-use "
                "conflicts, and applicable rehabilitation and resettlement policy."
            ),
            "sources": [
                {
                    "title": "National Disaster Management Guidelines: Management of "
                    "Landslides and Snow Avalanches",
                    "source": "National Disaster Management Authority (NDMA)",
                    "page": 43,
                }
            ],
            "evidence_sufficient": True,
        }
    return {
        "answer": (
            "Insufficient evidence was retrieved from the available knowledge base "
            "to answer this question reliably."
        ),
        "sources": [],
        "evidence_sufficient": False,
    }


def handle_rag_query(question: str, mode: str = None) -> dict:
    """Core handler shared by the FastAPI route and by tests/manual runs."""
    if not question or not question.strip():
        raise ValueError("question must be a non-empty string")

    mode = mode or os.environ.get("RAG_MODE", "real")

    if mode == "mock":
        return _mock_response(question)

    retriever = get_retriever()
    results = retriever.search(question)
    evidence_sufficient = retriever.is_evidence_sufficient(results)
    top_chunks = results[:2] if evidence_sufficient else []

    answer, sources, evidence_sufficient = generate_answer(
        question, top_chunks, evidence_sufficient, mode="extractive"
    )
    return {
        "answer": answer,
        "sources": sources,
        "evidence_sufficient": evidence_sufficient,
    }
