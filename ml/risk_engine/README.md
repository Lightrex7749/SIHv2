# DrishtiSetu — ML / Risk Engine (Member 1)

Explainable multi-hazard risk assessment and vulnerability scoring engine for disaster relocation prioritization.

---

## 1. Published Scoring Formula (v1.0)

In accordance with `ARCHITECTURE.md` Section 9D and `API_CONTRACT.md` v2 Section 3A, every score returned by this engine is traceable to the published, non-arbitrary formula below:

```
hazard_score = w1 · normalize(rainfall_intensity)
             + w2 · normalize(slope)
             + w3 · normalize(inverse_elevation_stability)
             + w4 · normalize(historical_event_frequency)

vulnerability_score = v1 · normalize(population_density)
                     + v2 · normalize(inverse_infrastructure_access)
                     + v3 · normalize(demographic_vulnerability_index)

overall_score = α · hazard_score + β · vulnerability_score + γ · historical_score
```

### Documented Baseline Weights:
- **Hazard Weights** ($\sum = 1.0$):
  - $w_1$ (Rainfall Intensity): `0.30` (IMD trigger threshold calibration)
  - $w_2$ (Terrain Slope): `0.25` (Himalayan shear failure angle $\ge 35^\circ$)
  - $w_3$ (Elevation Instability): `0.20` (High relief mass-wasting energy)
  - $w_4$ (Historical Frequency): `0.25` (Repeat landslide/flash-flood events)
- **Vulnerability Weights** ($\sum = 1.0$):
  - $v_1$ (Population Exposed): `0.40` (Direct human life at risk)
  - $v_2$ (Infrastructure Isolation): `0.35` (Inverse road/healthcare proximity)
  - $v_3$ (Demographic Index): `0.25` (Children, elderly, vulnerable groups)
- **Overall Aggregation Weights** ($\sum = 1.0$):
  - $\alpha$ (Hazard): `0.50`
  - $\beta$ (Vulnerability): `0.35`
  - $\gamma$ (Historical): `0.15`

*Note: These weights represent a documented starting baseline grounded in the NDMA Hazard Vulnerability Risk Assessment (HVRA) structure and INFORM Risk Index methodology.*

---

## 2. Explainability Endpoint (`/api/v1/risk/explain/{habitation_id}`)

Unlike black-box models that output a single unexplained number, this engine decomposes every calculation into the per-factor contribution points summing to the overall score.

Example output:
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

---

## 3. Classification Thresholds

| Overall Score Range | Risk Level | Relocation Priority | Recommended Authority Action |
|---|---|---|---|
| 80.0 – 100.0 | **CRITICAL** | **IMMEDIATE** | Expedite urgent relocation planning to candidate safe site |
| 60.0 – 79.9 | **HIGH** | **SHORT_TERM** | Prepare phased relocation master plan within current fiscal year |
| 40.0 – 59.9 | **MODERATE** | **LONG_TERM** | Structural mitigation + seasonal early warning monitoring |
| 0.0 – 39.9 | **LOW** | **MONITOR** | Routine periodic hazard assessment |

---

## 4. Reference Credit

Explainability decomposition pattern inspired by BHUSHAKTI-AI (`github.com/DISHITACHAUHAN/BHUSHAKTI-AI`), scoring logic and mathematical normalization is our own implementation.
