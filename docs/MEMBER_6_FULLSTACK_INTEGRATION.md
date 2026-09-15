You are Member 6 of the DrishtiSetu SIH 2026 development team. (v2 brief)

ROLE:
Full-Stack + Backend + Integration Engineer — also responsible for keeping
the complete project runnable and for the biggest new feature in v2: the
Authority decision log.

==================================================
WHAT'S NEW IN v2 (read this first)
==================================================

The pre-submission audit identified that the system currently generates
recommendations with no accountability trail — for a government
decision-support tool, that's the single biggest gap between "student
project" and "deployable prototype." Your v2 additions:

1. **Authority Action panel** (Accept / Reject / Defer + notes) on the
   dashboard, writing to the new `decision_log` table via the new
   `POST /api/v1/decision/log` and `GET /api/v1/decision/log/{habitation_id}`
   endpoints. This is a required feature, not optional polish.
2. **"Why this score?" explainability drawer** wired to Member 1's new
   `GET /api/v1/risk/explain/{habitation_id}` endpoint.
3. **Land-use conflict indicator** on candidate site cards/map (consumes
   Member 3's new `land_use_conflict` field/layer).
4. **Evidence-insufficient state** in the RAG evidence panel (consumes
   Member 4's new `evidence_sufficient` field) — must render distinctly
   from a normal evidence result, not just an empty list.
5. **Language toggle** (English + at least one Indian language) on the
   dashboard — a static string-table swap is sufficient for MVP.
6. **Contract test suite** (`/tests/contract/`) that every member's module
   must pass before merge — you own setting this up (Schemathesis against
   the OpenAPI spec, or a Postman/Newman collection matching
   `API_CONTRACT.md` v2) and running it in CI or as a pre-merge script.
7. Auth is still explicitly deferred for MVP, but add the unused FastAPI
   `current_user` dependency stub on protected-in-future routes so
   production RBAC can be layered in without refactoring.

Everything else in your original scope (map, dashboard, backend routing,
Docker, integration ownership) is unchanged.

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

Primary ownership: /frontend/, /backend/, /tests/integration/, (NEW) /tests/contract/
Also maintain: docker-compose.yml, requirements.txt, .env.example
You are the primary integration owner.

==================================================
FRONTEND
==================================================

Build a professional disaster-management authority dashboard (React + Leaflet
or MapLibre, ideally with a real basemap — Bhuvan WMS or standard satellite
tiles, per ARCHITECTURE.md).

The dashboard should include (original 15 items + 5 new):

1. GIS map
2. Habitation markers
3. Red Zones
4. Hazard layers
5. Selected habitation details
6. Risk score
7. Vulnerability score
8. Risk level
9. Relocation priority
10. Candidate relocation sites
11. Site suitability
12. Carrying capacity — must show raw numbers (population vs. capacity), not
    just a badge
13. AI recommendation, including estimated cost where available
14. Evidence/source panel, with a visible "insufficient evidence" state (NEW)
15. Loading/error states
16. (NEW) "Why this score?" explainability drawer
17. (NEW) Land-use conflict indicator on candidate sites
18. (NEW) Authority Action panel: Accept / Reject / Defer + notes → decision_log
19. (NEW) Decision history view (reads GET /decision/log/{habitation_id})
20. (NEW) Language toggle (English + 1 regional language)

==================================================
BACKEND
==================================================

Use Python, FastAPI, Pydantic. Implement the agreed APIs (v2 — 2 new
endpoints marked NEW):

GET /health
GET /api/v1/habitations/{habitation_id}
POST /api/v1/risk/analyze
GET /api/v1/risk/explain/{habitation_id}                  (NEW)
POST /api/v1/vision/analyze
GET /api/v1/gis/risk-layers
GET /api/v1/gis/layers/{layer_name}
POST /api/v1/rag/query
POST /api/v1/relocation/recommend
POST /api/v1/decision/analyze
POST /api/v1/decision/log                                  (NEW)
GET /api/v1/decision/log/{habitation_id}                   (NEW)

==================================================
IMPORTANT (unchanged)
==================================================

Do NOT duplicate ML, CV, GIS, RAG, or relocation logic inside the frontend.
The frontend communicates with APIs. The backend coordinates modules and
now also owns writing/reading `decision_log`.

==================================================
MOCK-FIRST DEVELOPMENT
==================================================

Initially implement mock services, including mocked versions of the two new
endpoints, using the exact v2 response structures in `/docs/API_CONTRACT.md`.
The dashboard must work even if ML/CV/RAG/GIS/agentic layers are incomplete.
Later replace mocks with actual modules without redesigning the frontend.

==================================================
MAIN DEMO (v2 — extended with Authority Action step)
==================================================

```
User opens dashboard
  ↓
GIS map loads (incl. land-use conflict layer)
  ↓
User selects habitation
  ↓
Frontend calls POST /api/v1/decision/analyze
  ↓
Backend obtains: risk (+explain) + vulnerability + GIS (+land-use check)
                 + relocation (+cost) + capacity (deterministic)
                 + RAG evidence (or evidence_sufficient=false)
  ↓
Backend returns structured decision
  ↓
Frontend displays: risk, vulnerability, relocation priority, recommended
site, capacity, suitability, cost, reasons, evidence
  ↓
NEW: Authority reviews and submits Accept/Reject/Defer via Authority Action
     panel → POST /api/v1/decision/log
  ↓
NEW: Decision persisted and visible on reload via GET /decision/log/{id}
```

==================================================
DATABASE
==================================================

Use PostgreSQL/PostGIS per `/docs/DATABASE_SCHEMA.md` v2 — includes the new
`decision_log` and `land_use_zones` tables, and new fields on
`relocation_recommendations` and `relocation_sites`. Do not create a
separate schema.

==================================================
INTEGRATION TESTS (v2 — new required cases)
==================================================

Create tests covering: health endpoint, habitation retrieval, risk API,
(NEW) risk explain API, vision API, GIS API (incl. land-use-conflict layer),
RAG API (incl. evidence_sufficient=false path), relocation API (incl. cost/
status fields), decision API, (NEW) decision log POST + GET round-trip,
complete end-to-end flow including the Authority Action step.

At least one integration test should simulate the full chain:
habitation → risk (+explain) → relocation (+land-use check) → capacity
→ recommendation → decision_log entry.

==================================================
CONTRACT TEST SUITE (NEW — you own this)
==================================================

Set up `/tests/contract/` with either:
* A Schemathesis run against the FastAPI-generated OpenAPI spec, validating
  responses match `/docs/API_CONTRACT.md` v2 shapes, or
* A Postman/Newman collection with one request per endpoint and assertions
  on required fields (including all v2 additive fields).

Every member must run this against their module (mock or real) before
merging a PR — this is what actually prevents silent field renames from
breaking integration, rather than relying on manual review.

==================================================
DOCKER
==================================================

Provide Docker configuration for frontend, backend, PostgreSQL/PostGIS.
Use environment variables. Do not commit API keys. Provide `.env.example`.

==================================================
UI REQUIREMENTS
==================================================

The UI should look like a professional disaster-management command
dashboard. Prioritize: map-first layout, clear risk indicators, clean cards,
readable charts, clear recommendation panel, evidence/source panel
(including the insufficient-evidence state), Authority Action panel,
responsive layout, loading states, error states. Do not overcomplicate the UI.

==================================================
AI CODING RULES
==================================================

You are NOT allowed to: redesign the architecture, create new APIs
unnecessarily beyond the two documented v2 additions, change shared field
names, create a second backend, create a second database, duplicate AI
logic, break mock services, remove functionality merely to make integration
easier.

If another module is incomplete, use its documented mock contract.

==================================================
INTEGRATION RESPONSIBILITY
==================================================

When another member submits their module: inspect their code, verify API
compatibility (run the contract test suite), run unit tests, run integration
tests, integrate incrementally, do not blindly merge AI-generated code.

If an integration conflict occurs: prefer the existing project contracts.
Do not solve conflicts by silently changing shared architecture.

==================================================
FINAL ACCEPTANCE TEST (v2 — extended)
==================================================

The project must support this demo:

1. Open dashboard.
2. Display GIS map (incl. land-use conflict layer).
3. Select a habitation.
4. Display risk + explainability drawer.
5. Display vulnerability.
6. Display relocation priority.
7. Display candidate relocation sites (incl. land-use conflict flag).
8. Display site capacity (with raw numbers).
9. Display suitability and estimated cost.
10. Retrieve RAG evidence (incl. an insufficient-evidence example).
11. Generate agentic recommendation.
12. Display reasoning.
13. (NEW) Authority submits Accept/Reject/Defer decision, persisted and
    visible on reload.
14. Complete the workflow without crashing.

FINAL PRINCIPLE:

Your primary responsibility is to ensure all six modules become ONE
reliable, explainable, accountable working SIH prototype. A simple
integrated system with a working audit trail is more valuable — and more
convincing to a judging panel — than six sophisticated modules that cannot
communicate with each other or show their work.
