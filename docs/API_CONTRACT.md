# DrishtiSetu

## API Contract (v2)

Base URL: `/api/v1`

All API responses must use JSON.

> **v2 changes:** added `/risk/explain`, `/decision/log` (POST + GET), `status` field on relocation recommendation, `estimated_cost` field, `land_use_conflict` field on candidate sites. All v1 fields are unchanged — this is additive only.

---

# 1. Health Check

## GET /health

```json
{
  "status": "ok",
  "service": "drishtisetu"
}
```

---

# 2. Get Habitation

## GET /api/v1/habitations/{habitation_id}

```json
{
  "id": "H001",
  "name": "Sample Habitation",
  "district": "Sample District",
  "state": "Sample State",
  "latitude": 30.123,
  "longitude": 78.456,
  "population": 1250,
  "vulnerability_score": 72.5,
  "risk_score": 81.2,
  "risk_level": "HIGH",
  "relocation_priority": "IMMEDIATE"
}
```

---

# 3. Risk Analysis

## POST /api/v1/risk/analyze

### Request

```json
{
  "habitation_id": "H001",
  "rainfall": 120.0,
  "elevation": 850.0,
  "slope": 32.0,
  "population": 1250,
  "historical_events": 4
}
```

### Response

```json
{
  "habitation_id": "H001",
  "hazard_score": 82.0,
  "vulnerability_score": 71.0,
  "historical_score": 76.0,
  "overall_score": 78.5,
  "risk_level": "HIGH",
  "relocation_priority": "IMMEDIATE"
}
```

Risk levels: LOW / MODERATE / HIGH / CRITICAL
Relocation priorities: MONITOR / LONG_TERM / SHORT_TERM / IMMEDIATE

The exact scoring methodology must be documented by the ML module (see ARCHITECTURE.md §9D).

---

# 3A. Risk Explainability (NEW)

## GET /api/v1/risk/explain/{habitation_id}

Returns the per-factor contribution breakdown behind a risk score. This is required — do not ship the risk score without this endpoint.

### Response

```json
{
  "habitation_id": "H001",
  "overall_score": 78.5,
  "factors": [
    { "name": "rainfall_intensity", "contribution": 22.4, "weight": 0.3, "raw_value": 120.0 },
    { "name": "slope", "contribution": 18.1, "weight": 0.25, "raw_value": 32.0 },
    { "name": "historical_event_frequency", "contribution": 15.0, "weight": 0.2, "raw_value": 4 },
    { "name": "population_density", "contribution": 12.5, "weight": 0.15, "raw_value": 1250 },
    { "name": "infrastructure_access", "contribution": 10.5, "weight": 0.1, "raw_value": null }
  ],
  "formula_version": "v1.0",
  "methodology_reference": "docs/DATA_SOURCES.md#scoring-methodology"
}
```

Contributions should sum (approximately) to `overall_score`. `factors` order = descending contribution.

---

# 4. Computer Vision Analysis

## POST /api/v1/vision/analyze

### Request

```json
{
  "image_url": "sample/image.jpg",
  "latitude": 30.123,
  "longitude": 78.456
}
```

### Response

```json
{
  "image_id": "IMG001",
  "detections": [
    {
      "hazard_type": "LANDSLIDE",
      "confidence": 0.87,
      "severity": "HIGH"
    }
  ],
  "model_disclosure": "Indicative only — fine-tuned on public dataset, N=<sample_count> training samples."
}
```

`model_disclosure` is a required new field — do not omit it. Possible hazard types: LANDSLIDE, FLOOD, COASTAL_EROSION, CLOUD_BURST_IMPACT, INFRASTRUCTURE_DAMAGE, UNKNOWN.

The CV module must not fabricate confidence values for real images.

---

# 5. GIS Risk Layers

## GET /api/v1/gis/risk-layers

```json
{
  "layers": [
    { "name": "red_zones", "type": "geojson", "url": "/api/v1/gis/layers/red-zones" },
    { "name": "habitations", "type": "geojson", "url": "/api/v1/gis/layers/habitations" },
    { "name": "relocation_sites", "type": "geojson", "url": "/api/v1/gis/layers/relocation-sites" },
    { "name": "land_use_conflict", "type": "geojson", "url": "/api/v1/gis/layers/land-use-conflict" }
  ]
}
```

`land_use_conflict` is a new optional layer (forest cover / eco-sensitive zone / existing settlement overlay).

---

# 6. Get GIS Layer

## GET /api/v1/gis/layers/{layer_name}

GeoJSON FeatureCollection.

```json
{
  "type": "FeatureCollection",
  "features": []
}
```

---

# 7. RAG Query

## POST /api/v1/rag/query

### Request

```json
{
  "question": "What factors should be considered when planning relocation from a landslide-prone habitation?"
}
```

### Response (evidence found)

```json
{
  "answer": "Retrieved evidence-based answer...",
  "sources": [
    { "title": "Document Title", "source": "Source Organization", "page": 12 }
  ],
  "evidence_sufficient": true
}
```

### Response (evidence NOT found — required path, must be implemented)

```json
{
  "answer": "Insufficient evidence was retrieved from the available knowledge base to answer this question reliably.",
  "sources": [],
  "evidence_sufficient": false
}
```

`evidence_sufficient` is a new required field. RAG responses must provide sources whenever available and must never fabricate them.

---

# 8. Relocation Recommendation

## POST /api/v1/relocation/recommend

### Request

```json
{
  "habitation_id": "H001"
}
```

### Response

```json
{
  "habitation_id": "H001",
  "recommended_site": {
    "site_id": "S001",
    "name": "Candidate Site A",
    "land_use_conflict": false
  },
  "suitability_score": 84.5,
  "site_capacity": 1800,
  "population_to_relocate": 1250,
  "capacity_sufficient": true,
  "estimated_cost": 62500000,
  "cost_basis": "population_to_relocate x per_capita_resettlement_benchmark (see DATA_SOURCES.md)",
  "recommendation": "SUITABLE",
  "status": "PROPOSED"
}
```

`land_use_conflict`, `estimated_cost`, `cost_basis`, and `status` are new fields. `status` supports: PROPOSED / APPROVED / IN_PROGRESS / COMPLETED / REJECTED. `capacity_sufficient` MUST be computed deterministically — see ARCHITECTURE.md §9B — and never generated or altered by an LLM call.

---

# 9. Decision Analysis

Main integration endpoint.

## POST /api/v1/decision/analyze

### Request

```json
{
  "habitation_id": "H001"
}
```

### Response

```json
{
  "habitation": { "id": "H001", "name": "Sample Habitation", "population": 1250 },
  "risk": {
    "hazard_score": 82.0,
    "vulnerability_score": 71.0,
    "overall_score": 78.5,
    "risk_level": "HIGH",
    "relocation_priority": "IMMEDIATE"
  },
  "relocation": {
    "recommended_site": "S001",
    "suitability_score": 84.5,
    "capacity": 1800,
    "capacity_sufficient": true,
    "land_use_conflict": false,
    "estimated_cost": 62500000
  },
  "reasoning": [
    "High multi-hazard risk",
    "High population vulnerability",
    "Candidate site has sufficient estimated capacity",
    "Candidate site has comparatively better accessibility",
    "No land-use conflict detected on candidate site"
  ],
  "evidence": [
    { "title": "Relevant Disaster Management Guidance", "page": 12, "source": "Authority/Organization" }
  ],
  "evidence_sufficient": true,
  "recommendation": "PRIORITIZE IMMEDIATE RELOCATION PLANNING"
}
```

---

# 9A. Decision Log (NEW)

## POST /api/v1/decision/log

Records an authority's action on a recommendation. Required feature — not optional.

### Request

```json
{
  "habitation_id": "H001",
  "recommendation_id": "REC001",
  "reviewed_by": "District Officer, Sample District",
  "decision": "ACCEPTED",
  "notes": "Approved for phase 1 implementation, budget pending."
}
```

`decision` supports: ACCEPTED / REJECTED / DEFERRED.

### Response

```json
{
  "id": "LOG001",
  "habitation_id": "H001",
  "recommendation_id": "REC001",
  "decision": "ACCEPTED",
  "reviewed_by": "District Officer, Sample District",
  "notes": "Approved for phase 1 implementation, budget pending.",
  "reviewed_at": "2026-09-14T10:00:00Z"
}
```

## GET /api/v1/decision/log/{habitation_id}

Returns the full history of authority decisions for a habitation, ordered newest-first. Same object shape as above, as a list.

---

# 10. Error Format

```json
{
  "error": {
    "code": "HABITATION_NOT_FOUND",
    "message": "Habitation H001 was not found."
  }
}
```

---

# 11. API Compatibility Rules

Do NOT:

* Rename endpoints without agreement.
* Rename response fields independently.
* Change data types without agreement.
* Return different structures for mock and production implementations.
* Put model-specific internal data into public API responses unnecessarily.
* Merge a PR that fails the shared contract test suite (`/tests/contract/`) against this document.

Mock services must implement the same API contract as the final services, including all v2 additive fields above.

---

# 12. Main Integration Rule

The frontend must be able to work with mock API responses before the actual ML/CV/RAG/agent implementations are complete. This ensures individual modules can be developed independently and integrated incrementally.

Before every PR, run the shared contract test collection (`/tests/contract/drishtisetu.postman_collection.json` or equivalent Schemathesis run) against your module's mock and real implementations to catch field drift immediately — this replaces relying on manual review to catch renamed fields.
