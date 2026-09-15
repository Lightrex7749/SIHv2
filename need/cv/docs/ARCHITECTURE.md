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

#### Layer 2 — Backend/API
Technology: Python, FastAPI, Pydantic.

#### Layer 3 — Machine Learning
Hazard risk scoring, vulnerability scoring, overall risk scoring, and factor explainability via `/api/v1/risk/explain/{habitation_id}`.

#### Layer 4 — Computer Vision (Member 2)
Disaster imagery analysis on satellite/aerial patches for hazard indicator extraction and change detection with mandatory `model_disclosure`.

#### Layer 5 — GIS/Data
Geospatial datasets, PostGIS tables, hazard layers, relocation sites, and land-use conflict check.

#### Layer 6 — RAG/NLP
Disaster management document retrieval with evidence-sufficient / insufficient-evidence responses.

#### Layer 7 — Agentic AI
Orchestrates decisions with deterministic capacity safety rule.
