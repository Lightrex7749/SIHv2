# DrishtiSetu — Computer Vision Module (Member 2)

Disaster imagery analysis pipeline specialized in satellite and aerial imagery patches (Sentinel-2 / Bhuvan / aerial) for multi-temporal change detection and visual hazard indicator extraction.

---

## 1. Overview & Architecture

Per **API Contract (v2)** and **Member 2 Brief (v2)**, single-image classification is inherently fragile for high-stakes relocation decisions. This module provides a dual-layer approach:

1. **Phase 1: Deterministic Demo Engine (`MockVisionDetector`)**:
   - Zero-failure, reproducible responses for 4 core hackathon presentation scenarios (Landslide, Flood Inundation, Infrastructure Scour, and Baseline Safe Plateau).
   - Strict adherence to `API_CONTRACT.md` v2 with mandatory `model_disclosure`.
2. **Phase 2: Bi-Temporal Satellite Change Detection (`SatelliteChangeDetector`)**:
   - Computes multi-spectral reflectance delta (Modified Normalized Difference Water Index - MNDWI proxy and Excess Green vegetation index) alongside structural edge displacement between pre-disaster and post-disaster satellite chips.
   - Non-fabricated, calibrated confidence values based on measured ground pixel alteration ratios.
3. **Unified Service (`VisionService`) & FastAPI Router**:
   - Plugs directly into Member 6's central integration backend with one import (`vision_router`).

---

## 2. API Contract v2 Compliance

### Endpoint
`POST /api/v1/vision/analyze`

### Request Payload
```json
{
  "image_url": "computer_vision/demo_assets/chamoli_landslide_post.png",
  "latitude": 30.552,
  "longitude": 79.566,
  "pre_image_url": "computer_vision/demo_assets/chamoli_landslide_pre.png"
}
```

### Response Payload
```json
{
  "image_id": "IMG_CHAMOLI_LS_01",
  "detections": [
    {
      "hazard_type": "LANDSLIDE",
      "confidence": 0.87,
      "severity": "HIGH"
    }
  ],
  "model_disclosure": "Prototype uses a rule-based/mock detector for demo purposes. Production implementation would use a model fine-tuned on Sen1Floods11 (flood) and Landslide4Sense (landslide), both public benchmark datasets."
}
```

### Supported Hazard Types
- `LANDSLIDE`
- `FLOOD`
- `COASTAL_EROSION`
- `CLOUD_BURST_IMPACT`
- `INFRASTRUCTURE_DAMAGE`
- `UNKNOWN`

### Severity Levels
- `LOW`
- `MODERATE`
- `HIGH`
- `CRITICAL`

---

## 3. Integration for Member 6 (FastAPI Backend)

Member 6 can mount this module directly into the main FastAPI application:

```python
from fastapi import FastAPI
from computer_vision.router import vision_router

app = FastAPI(title="DrishtiSetu Integrated Backend")

# Mount the CV router
app.include_router(vision_router)
```

Alternatively, call the service directly in Python:

```python
from computer_vision.service import get_vision_service
from computer_vision.schemas import VisionAnalyzeRequest

service = get_vision_service()
result = service.analyze(VisionAnalyzeRequest(
    image_url="sample/image.jpg",
    latitude=30.123,
    longitude=78.456
))
print(result.model_dump())
```

---

## 4. Curated Demo Scenarios (Zero-Failure on Stage)

| Scenario | Location / Coordinates | Hazard Detected | Severity | Confidence | Notes |
|---|---|---|---|---|---|
| **Chamoli Landslide** | `lat: 30.552, lon: 79.566` | `LANDSLIDE` | `HIGH` | 0.87 | Slope scarp on steep Himalayan habitation ridge. |
| **Brahmaputra Flood** | `lat: 26.185, lon: 92.931` | `FLOOD` | `HIGH` | 0.92 | Surface water inundation submerging agrarian habitations. |
| **Wayanad Infrastructure** | `lat: 11.685, lon: 76.132` | `INFRASTRUCTURE_DAMAGE` | `MODERATE` | 0.79 | Flash flood runoff scouring access bridge abutment. |
| **Safe Relocation Plateau** | `lat: 30.210, lon: 78.850` | `UNKNOWN` | `LOW` | 0.15 | Stable terrain baseline with no critical hazard indicators. |

Pre-generated 256x256 satellite patches for all four scenarios reside in `computer_vision/demo_assets/`.

---

## 5. Model Attribution & Citations

In accordance with ethical AI disclosure rules and hackathon transparency requirements:
- **Change detection & flood extent protocols** inspired by:
  - **Sen1Floods11**: Bonafilia et al., *Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1*, IEEE/CVF CVPRW 2020. [GitHub](https://github.com/cloudtostreet/Sen1Floods11).
- **Landslide visual identification patterns** inspired by:
  - **Landslide4Sense**: Corley et al., *Landslide4Sense: Reference Benchmark for Landslide Detection from Multi-Sensor Satellite Imagery*, IEEE GRSM 2022. [GitHub](https://github.com/isaaccorley/landslide4sense).
- **Foundation architecture reference**:
  - **IBM-NASA Prithvi-100M**: IBM / NASA Geospatial Foundation Model fine-tuned on Sen1Floods11 (Apache-2.0 license). [HuggingFace](https://huggingface.co/ibm-nasa-geospatial/Prithvi-100M-sen1floods11).

> **Integrity Disclosure Statement:**
> "Prototype uses a rule-based/mock detector for demo purposes. Production implementation would use a model fine-tuned on Sen1Floods11 (flood) and Landslide4Sense (landslide), both public benchmark datasets."

---

## 6. Running Tests

Execute the test suite with `pytest`:

```bash
python -m pytest computer_vision/tests/ -v
```
