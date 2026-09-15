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
* land_use_conflict (boolean)
* land_use_conflict_reason (text, nullable)
* geometry

---

# 6. cv_detections
* id
* image_id
* location_id
* hazard_type
* confidence
* severity
* model_disclosure (text, NEW — e.g. "fine-tuned on N public samples, indicative only")
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
* formula_version (text)
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
* status (text: PROPOSED / APPROVED / IN_PROGRESS / COMPLETED / REJECTED)
* estimated_cost (numeric, nullable)
* cost_basis (text, nullable)
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

# 9A. decision_log (NEW TABLE)
* id
* habitation_id (fk → habitations)
* recommendation_id (fk → relocation_recommendations)
* reviewed_by (text)
* decision (text: ACCEPTED / REJECTED / DEFERRED)
* notes (text, nullable)
* reviewed_at (timestamp)

---

# 9B. land_use_zones (NEW TABLE)
* id
* zone_type (text: FOREST / ECO_SENSITIVE / EXISTING_SETTLEMENT / PROTECTED)
* source (text)
* geometry
