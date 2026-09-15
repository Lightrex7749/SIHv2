# DrishtiSetu

## Database Schema (v2)

Database: PostgreSQL
Geospatial extension: PostGIS

> **v2 changes:** added `decision_log` table, added `land_use_conflict`, `estimated_capacity` clarifications, `status` and `estimated_cost` fields to `relocation_recommendations`, added `land_use_zones` table. All original tables/fields retained unchanged.

---

# 1. habitations

* id
* name
* district
* state
* latitude
* longitude
* population
* vulnerability_score
* risk_score
* risk_level
* relocation_priority
* geometry

---

# 2. hazards

* id
* habitation_id
* hazard_type
* severity
* source
* event_date
* geometry

Hazard types: LANDSLIDE / FLOOD / COASTAL_EROSION / CLOUD_BURST

---

# 3. disaster_history

* id
* habitation_id
* hazard_type
* event_date
* severity
* source
* description

---

# 4. infrastructure

* id
* name
* type
* latitude
* longitude
* capacity
* geometry

Infrastructure types: HOSPITAL / SCHOOL / ROAD / WATER_SOURCE / SHELTER / HEALTH_CENTER

---

# 5. relocation_sites

* id
* name
* latitude
* longitude
* available_area
* estimated_capacity
* hazard_score
* road_access_score
* healthcare_access_score
* water_access_score
* school_access_score
* suitability_score
* **land_use_conflict** (boolean, NEW — true if site overlaps forest/eco-sensitive/existing-settlement zone)
* **land_use_conflict_reason** (text, nullable, NEW)
* geometry

---

# 6. cv_detections

* id
* image_id
* location_id
* hazard_type
* confidence
* severity
* **model_disclosure** (text, NEW — e.g. "fine-tuned on N public samples, indicative only")
* detected_at

---

# 7. risk_assessments

* id
* habitation_id
* hazard_score
* vulnerability_score
* historical_score
* infrastructure_score
* overall_score
* risk_level
* **formula_version** (text, NEW — references the documented scoring formula version used)
* created_at

---

# 8. relocation_recommendations

* id
* habitation_id
* site_id
* suitability_score
* capacity_available
* recommendation
* reasoning
* **status** (text, NEW — PROPOSED / APPROVED / IN_PROGRESS / COMPLETED / REJECTED, default PROPOSED)
* **estimated_cost** (numeric, nullable, NEW)
* **cost_basis** (text, nullable, NEW)
* created_at

---

# 9. knowledge_documents

* id
* title
* source
* document_type
* page
* content
* embedding

---

# 9A. decision_log (NEW TABLE — required)

Records every authority action taken on a recommendation. This is the audit trail that makes the system accountable rather than autonomous.

* id
* habitation_id (fk → habitations)
* recommendation_id (fk → relocation_recommendations)
* reviewed_by (text — free-text name/role acceptable for MVP; becomes a real user_id once auth is added)
* decision (text — ACCEPTED / REJECTED / DEFERRED)
* notes (text, nullable)
* reviewed_at (timestamp)

---

# 9B. land_use_zones (NEW TABLE — supports the land-use conflict check)

* id
* zone_type (text — FOREST / ECO_SENSITIVE / EXISTING_SETTLEMENT / PROTECTED)
* source (text — cite the real dataset, see DATA_SOURCES.md)
* geometry

---

# 10. Relationships

```
habitations
├── hazards
├── disaster_history
├── risk_assessments
├── relocation_recommendations
│     └── decision_log
└── (spatially joined to) relocation_sites

relocation_sites
├── infrastructure
└── (spatially checked against) land_use_zones

cv_detections
└── habitation/location

knowledge_documents
└── RAG retrieval
```

---

# 11. Database Rules

1. IDs must be stable.
2. Do not rename columns independently.
3. Use appropriate foreign keys.
4. Latitude/longitude must use a consistent coordinate reference system (WGS84 / EPSG:4326 recommended).
5. Geospatial fields should use PostGIS where appropriate.
6. Mock data must be clearly identifiable (`source = 'SYNTHETIC_DEMO'` convention recommended on relevant tables).
7. Real-world data sources must be documented in `/docs/DATA_SOURCES.md`.
8. Do not insert fabricated government data.
9. **New:** `decision_log` entries are append-only — never update or delete a logged decision; if a decision is revised, insert a new row referencing the same `recommendation_id`.
