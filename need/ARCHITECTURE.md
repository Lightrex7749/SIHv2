# DrishtiSetu

## System Architecture (v2 — Hackathon-Hardened)

> **Change log from v1:** added explainability endpoint, decision audit trail, named real data sources, capacity-safety enforcement rule, security deferral note, land-use conflict check, and demo-guardrail requirements. All changes are additive — no existing field names were renamed.

### 1. Project Overview

DrishtiSetu is an AI-driven, GIS-enabled disaster relocation decision-support platform designed to help State Disaster Management Authorities proactively identify unsafe habitation zones, assess vulnerability, evaluate safer relocation sites, estimate carrying capacity, and prioritize relocation actions.

The platform focuses on multi-hazard scenarios including:

* Landslides
* Floods
* Coastal erosion
* Cloudbursts
* Related infrastructure and environmental risks

The system combines:

* GIS and geospatial analysis
* Machine Learning
* Computer Vision
* NLP and RAG
* Agentic AI
* Population vulnerability analysis
* Relocation-site suitability analysis
* Carrying-capacity estimation

The system is intended as a decision-support platform. **It does not autonomously order or execute relocation. Every recommendation must be reviewed and accepted/rejected/deferred by an authorized human authority, and that decision must be permanently logged (see Section 9A).**

---

### 2. Core Architecture

The system follows this high-level pipeline:

```
Public/Prepared Data (named real sources, see DATA_SOURCES.md)
↓
GIS + Data Processing
↓
Hazard Analysis ──────────┐
↓                         │
Computer Vision ──────────┤
↓                         │
Historical Disaster Data ─┤
↓                         │
Population Vulnerability ─┤
↓                         │
Risk Engine (+ /risk/explain) │
↓                         │
Multi-Hazard Risk         │
↓                         │
Relocation Prioritization
↓
Candidate Safe Sites
↓
Land-Use Conflict Check (NEW)
↓
Site Suitability + Capacity (deterministic, LLM cannot override — see 9B)
↓
RAG Knowledge Retrieval (must declare insufficient evidence when applicable)
↓
Agentic Decision Engine
↓
Authority Dashboard → Accept / Reject / Defer (logged to decision_log)
```

---

### 3. System Layers

#### Layer 1 — Frontend

Technology: React, JavaScript/TypeScript, Leaflet or MapLibre, HTML/CSS.

Responsibilities:

- GIS map visualization (basemap should use a real imagery/terrain tile source where possible — Bhuvan WMS or a standard satellite basemap — not a blank vector map)
- Red Zone visualization
- Habitation selection
- Risk dashboard **with a "Why this score?" explainability drawer** (calls `/risk/explain`)
- Vulnerability indicators
- Relocation priority
- Candidate relocation sites, with a visible flag if a site fails the land-use conflict check
- Capacity visualization (must visibly show the raw numbers: population_to_relocate vs site_capacity — never just a green/red badge with no numbers)
- AI-generated recommendation
- Evidence/source display, including an explicit "insufficient evidence" state
- **Authority Action panel**: Accept / Reject / Defer + notes, writing to `decision_log`
- Language toggle (English + at least one Indian language) — MVP can be a static string-table swap

The frontend must NOT contain ML, RAG, CV, or decision-making logic. It must never compute `capacity_sufficient` itself — always display the value returned by the backend.

---

#### Layer 2 — Backend/API

Technology: Python, FastAPI, Pydantic.

Responsibilities:

- API routing
- Request validation
- Response validation
- Communication between modules
- Database interaction
- **Authentication is deferred for hackathon scope** (see Section 9C) — but the FastAPI dependency injection stub for `current_user` must exist unused, so production auth can be added without refactoring routes.
- Aggregation of module outputs
- Writing/reading `decision_log` entries

The backend acts as the central integration layer.

---

#### Layer 3 — Machine Learning

Responsibilities:

- Hazard risk scoring, using a **published, documented formula** (see Section 9D) — not an unexplained black-box number
- Vulnerability scoring
- Overall risk scoring
- Risk classification
- Relocation priority classification
- Per-factor contribution breakdown, exposed via `/api/v1/risk/explain/{habitation_id}`

The ML module must expose stable functions/API-compatible outputs and must never report accuracy/confidence figures that were not actually evaluated.

---

#### Layer 4 — Computer Vision

Responsibilities:

- Disaster imagery analysis, preferably on **satellite/aerial imagery patches (e.g., Sentinel-2 via Sentinel Hub free tier)** for before/after change detection rather than single arbitrary photos
- Flood/water extent detection where feasible
- Landslide/erosion/change detection where feasible
- Infrastructure/environmental visual indicators
- Every output must include a disclosure of training-data scale (e.g., "indicative, trained/fine-tuned on N public samples") — this is a requirement, not a nice-to-have

The CV module must return structured JSON-compatible outputs and must never fabricate confidence values.

---

#### Layer 5 — GIS/Data

Responsibilities:

- Geospatial datasets, **sourced from real, named public datasets** for at least one pilot district (see DATA_SOURCES.md) — synthetic data may fill gaps but must be clearly labeled
- GeoJSON preparation
- Coordinate normalization
- Spatial analysis
- Hazard layers
- Habitation layers
- Candidate relocation site layers
- Infrastructure proximity
- **Land-use conflict layer**: forest cover / eco-sensitive zone / existing settlement overlay used to flag unsuitable candidate sites

Preferred database: PostgreSQL + PostGIS.

---

#### Layer 6 — RAG/NLP

Responsibilities:

- Disaster-management document ingestion (NDMA guidelines, state DM plans, R&R policy documents — see DATA_SOURCES.md)
- Document chunking
- Embeddings
- Semantic retrieval
- Evidence-based answer generation
- Source/page metadata
- **Explicit "insufficient evidence" response path** — must be implemented and testable, not just described

The RAG system must distinguish retrieved evidence from model-generated interpretation and must never invent sources or page numbers.

---

#### Layer 7 — Agentic AI

The agent layer coordinates outputs from the other modules.

Agents:

1. Risk Agent
2. Vulnerability Agent
3. Relocation Agent
4. Capacity Agent
5. Decision Agent

Rules:

- Agents use tools/functions/APIs rather than duplicating underlying ML/GIS/RAG logic.
- **`capacity_sufficient` is computed deterministically in code before any LLM call and passed into the LLM as a fixed, non-negotiable fact.** The LLM may explain reasoning but must never recompute or contradict this value. This must be covered by a unit test (see Member 5 doc).

---

### 4. Main Decision Pipeline

For a selected habitation:

1. Retrieve habitation data.
2. Retrieve hazard information.
3. Retrieve historical disaster information.
4. Calculate hazard/risk score (documented formula).
5. Calculate population vulnerability.
6. Determine overall risk.
7. Determine relocation priority.
8. Identify candidate safer sites.
9. Run land-use conflict check on candidate sites.
10. Calculate site suitability.
11. Estimate site carrying capacity (deterministic).
12. Check residual hazard.
13. Check accessibility and essential infrastructure.
14. Retrieve relevant disaster-management guidance using RAG (or declare insufficient evidence).
15. Decision Agent combines structured data and evidence.
16. Generate an explainable recommendation, including estimated relocation cost where feasible.
17. Display result on the dashboard.
18. Authority reviews and records Accept/Reject/Defer decision → `decision_log`.

---

### 5. Module Ownership

Unchanged — see CONTRIBUTING.md.

---

### 6. Shared Rules

All modules must:

- Use the agreed API contracts.
- Use the agreed database schema.
- Use stable field names.
- Return structured JSON.
- Support mock data during development, clearly labeled as mock.
- Include tests, run against the shared Postman/contract-test collection before every PR.
- Avoid unnecessary dependencies.
- Avoid modifying unrelated modules.
- Document important assumptions.
- Never fabricate real-world data.
- Never claim unsupported model accuracy.
- Never let generative/LLM output override a deterministic numeric calculation.

---

### 7. Technology Stack

Frontend: React + JavaScript/TypeScript + Leaflet/MapLibre (+ Bhuvan WMS basemap where possible)

Backend: Python + FastAPI + Pydantic

Database: PostgreSQL + PostGIS

ML: Python + scikit-learn and/or XGBoost + **SHAP for explainability**

Data: Pandas + NumPy + GeoPandas

Computer Vision: OpenCV + a pretrained/fine-tuned model on a public flood/landslide dataset (e.g., Sen1Floods11, Landslide4Sense)

RAG: Python + embeddings + vector retrieval + pgvector where practical

AI: LLM accessed through configurable environment variables

Containerization: Docker + Docker Compose

Version Control: Git + GitHub

Contract testing: Schemathesis (or equivalent) run in CI against the OpenAPI spec, to catch field renames before merge.

---

### 8. Design Principle

DrishtiSetu must be built as ONE integrated platform. Mock implementations should be created first so integration can begin before every AI model is complete. Every module must be replaceable without requiring major frontend changes.

---

### 9. New Sections (Hackathon-Hardening Additions)

#### 9A. Decision Audit Trail

Every recommendation shown to an authority must be logged with an Accept/Reject/Defer decision, reviewer identity (free text acceptable for MVP), notes, and timestamp. See `decision_log` in DATABASE_SCHEMA.md. This is a required, not optional, feature.

#### 9B. Capacity Safety Rule

`capacity_sufficient` must be computed as a pure deterministic boolean (`population_to_relocate <= site_capacity * safety_margin`) before any LLM involvement. The LLM must never be allowed to state otherwise. A unit test must exist that attempts to trick the LLM into contradicting this and asserts the API still returns the correct value.

#### 9C. Security Deferral (explicit, not silent)

Authentication/RBAC is out of scope for the hackathon build, but the stub dependency must exist in FastAPI routes so production auth (District Officer / State Authority / Read-only Viewer roles) can be added without route refactoring. State this explicitly in the pitch — do not let it appear as an oversight.

#### 9D. Published Scoring Formula

```
hazard_score = w1·normalize(rainfall_intensity)
             + w2·normalize(slope)
             + w3·normalize(inverse_elevation_stability)
             + w4·normalize(historical_event_frequency)

vulnerability_score = v1·normalize(population_density)
                     + v2·normalize(inverse_infrastructure_access)
                     + v3·normalize(demographic_vulnerability_index)

overall_score = α·hazard_score + β·vulnerability_score + γ·historical_score
```

Weights must be documented in `/ml/risk_engine/README.md`, either sourced from a real framework (e.g., NDMA HVRA methodology, INFORM Risk Index structure) or derived via a documented AHP pairwise-comparison exercise by the team. Arbitrary undocumented weights are not acceptable.

#### 9E. Land-Use Conflict Check

Before a candidate relocation site is recommended, it must be checked against a forest-cover / eco-sensitive-zone / existing-settlement layer. Sites that conflict must be flagged, not silently excluded — the reasoning output should state why a site was down-ranked or excluded.

#### 9F. Multi-Language & Offline Note

MVP should support at least English + one Indian language via a string-table toggle. Full offline-sync support is out of scope for the hackathon but should be named as a documented future-work item in the pitch, since target users operate in low-connectivity terrain.

---

### 10. Decision-Support Disclaimer

The system provides AI-assisted decision support. It must not claim that its recommendations are legally binding or guaranteed to be safe. Final relocation decisions remain with authorized disaster-management authorities, and every such decision is recorded in `decision_log`.
