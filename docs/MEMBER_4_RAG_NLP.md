You are Member 4 of the DrishtiSetu SIH 2026 development team. (v2 brief)

ROLE:
RAG + NLP Engineer

==================================================
WHAT'S NEW IN v2 (read this first)
==================================================

Your original brief already required "clearly indicate when evidence is
insufficient" as a soft principle. The audit upgraded this to a **required,
testable, demoable feature**:

1. Response contract now includes a new `evidence_sufficient` boolean field
   (see API_CONTRACT.md §7). When retrieval confidence/relevance is below a
   threshold you define, return `evidence_sufficient: false`, an empty or
   minimal `sources` array, and an honest "insufficient evidence" answer
   string — never a confident-sounding guess.
2. You must identify (and the team must rehearse) at least one real demo
   query that intentionally triggers this path, so judges see the guardrail
   fire live. This is one of the most persuasive moments in the whole demo.
3. Prioritize ingesting real NDMA/state disaster-management documents (see
   DATA_SOURCES.md v2) rather than placeholder text, so the "evidence" shown
   on stage is genuinely sourced.

Everything else in your original scope is unchanged.

==================================================
MANDATORY DOCUMENTS
==================================================

Before coding, read (v2 versions):
/docs/ARCHITECTURE.md
/docs/API_CONTRACT.md
/docs/DATABASE_SCHEMA.md
/docs/DATA_SOURCES.md
/docs/CONTRIBUTING.md
/docs/INTEGRATION_GUIDE.md
/docs/DEMO_FLOW.md

==================================================
OWNERSHIP
==================================================

Primary ownership: /rag/
Structure: /rag/documents/, /rag/ingestion/, /rag/retrieval/, /rag/generation/
Do not independently modify: /ml/, /computer_vision/, /gis/, /agents/, /frontend/

==================================================
OBJECTIVE
==================================================

Build an evidence-grounded RAG system for disaster-management knowledge,
retrieving from authoritative documents and providing source-aware answers
— including an honest "insufficient evidence" response when appropriate.

Potential knowledge: disaster management guidelines, relocation planning
principles, hazard mitigation guidance, vulnerability assessment guidance,
rehabilitation and resettlement guidance, site-selection considerations,
disaster preparedness documents. (See DATA_SOURCES.md v2 for real,
named sources — NDMA guidelines, National Disaster Management Plan, state
R&R policy documents.)

==================================================
RAG PIPELINE (unchanged structure)
==================================================

Documents → Text extraction → Cleaning → Chunking → Metadata → Embeddings →
Vector storage/retrieval → Relevant chunks → LLM generation → Answer + sources

==================================================
API CONTRACT (v2 — new required field)
==================================================

Endpoint: POST /api/v1/rag/query

Input:
```json
{"question": "What factors should be considered when planning relocation from a landslide-prone habitation?"}
```

Output when evidence found:
```json
{"answer": "...", "sources": [{"title": "Document Title", "source": "Source Organization", "page": 12}], "evidence_sufficient": true}
```

Output when evidence NOT found (NEW — required path):
```json
{"answer": "Insufficient evidence was retrieved from the available knowledge base to answer this question reliably.", "sources": [], "evidence_sufficient": false}
```

Do not change this contract without approval, other than the additive
`evidence_sufficient` field above.

==================================================
SOURCE QUALITY (unchanged, now with real sources to use)
==================================================

Prioritize: government documents (NDMA, state SDMAs), official
disaster-management organizations, research institutions, peer-reviewed
research, international organizations. Avoid unreliable blogs as primary
evidence. Every document must have metadata.

==================================================
ANTI-HALLUCINATION (now enforced via evidence_sufficient)
==================================================

The system must: retrieve evidence before answering, provide source
metadata, avoid unsupported factual claims, clearly indicate when evidence
is insufficient (via the new field, not just prose hedging), avoid inventing
citations, avoid inventing document pages. Define a concrete relevance/
similarity threshold below which `evidence_sufficient` flips to false — this
threshold should be documented in your README, not implicit.

==================================================
DATABASE
==================================================

Use `knowledge_documents` as defined in `/docs/DATABASE_SCHEMA.md`. Do not
independently redesign the database.

==================================================
MOCK MODE
==================================================

Create a mock retrieval mode so the integration member can test the endpoint
before the complete vector database is available. Mock and real modes must
return the same API structure, including `evidence_sufficient`.

==================================================
TESTING
==================================================

Test: document ingestion, chunking, metadata, retrieval, no-result query
(NEW: assert `evidence_sufficient: false` and empty/minimal sources),
source attribution, malformed document, empty question, mock query.

==================================================
AI AGENT RULES
==================================================

Do not: build a separate chatbot application, change the frontend, modify
ML/CV logic, fabricate sources, fabricate page numbers, claim an LLM
response is authoritative by itself, hard-code answers as if from documents.

Before completion: test ingestion, retrieval, API output (including the new
field), verify source metadata, document datasets/documents used (cite
real ones per DATA_SOURCES.md v2), list dependencies, list limitations, and
(NEW) identify at least one query that reliably demonstrates the
insufficient-evidence path for the team's demo script.

FINAL PRINCIPLE:

The RAG system exists to provide evidence and contextual knowledge to the
decision engine, complementing structured GIS/ML outputs. Admitting
uncertainty when evidence is thin is now a demonstrated feature, not a
fallback you hope never triggers.
