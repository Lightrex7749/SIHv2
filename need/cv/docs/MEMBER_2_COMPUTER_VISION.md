# Member 2: Computer Vision Engineer (v2 brief)

ROLE: Computer Vision Engineer — Disaster Image Analysis

## Overview
Disaster imagery analysis specializing in satellite/aerial imagery patches (e.g., Sentinel-2) for before/after change detection and visual hazard indicator extraction.

## Mandatory Endpoint
- `POST /api/v1/vision/analyze`

### Input Contract
```json
{
  "image_url": "sample/image.jpg",
  "latitude": 30.123,
  "longitude": 78.456
}
```

### Output Contract
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

## Supported Hazard Types
- `LANDSLIDE`
- `FLOOD`
- `COASTAL_EROSION`
- `CLOUD_BURST_IMPACT`
- `INFRASTRUCTURE_DAMAGE`
- `UNKNOWN`

## Key Requirements
1. **Model Disclosure**: Mandatory field disclosing training-data scale and model nature honestly.
2. **Determinism in Mock Mode**: Provide fixed mappings for sample coordinates/images for zero-failure hackathon demonstrations.
3. **Change Detection**: Pre/post patch comparison for defensible disaster delta calculations.
4. **Clean Decoupling**: Standalone service that Member 6 (Backend & Integration) can mount or import effortlessly.
