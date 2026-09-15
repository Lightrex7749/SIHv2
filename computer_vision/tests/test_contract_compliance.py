"""
Strict Contract Compliance Test Suite.
Validates the Computer Vision output matches docs/API_CONTRACT.md (v2) Section 4.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from computer_vision.router import router as vision_router

app = FastAPI()
app.include_router(vision_router)
client = TestClient(app)

ALLOWED_HAZARDS = {
    "LANDSLIDE",
    "FLOOD",
    "COASTAL_EROSION",
    "CLOUD_BURST_IMPACT",
    "INFRASTRUCTURE_DAMAGE",
    "UNKNOWN"
}

ALLOWED_SEVERITIES = {"LOW", "MODERATE", "HIGH", "CRITICAL"}


def test_contract_section_4_conformance():
    """
    Validates:
    1. Base URL / Request schema: {"image_url": str, "latitude": float, "longitude": float}
    2. Response fields:
       - image_id: string
       - detections: list of {hazard_type: str, confidence: float, severity: str}
       - model_disclosure: non-empty string
    3. Exactly allowed hazard types and confidence range [0.0, 1.0].
    """
    request_body = {
        "image_url": "sample/image.jpg",
        "latitude": 30.123,
        "longitude": 78.456
    }
    response = client.post("/api/v1/vision/analyze", json=request_body)
    assert response.status_code == 200

    data = response.json()

    # Verify top-level fields
    assert set(data.keys()) == {"image_id", "detections", "model_disclosure"}, (
        f"Response keys {set(data.keys())} do not strictly match contract keys."
    )

    assert isinstance(data["image_id"], str) and len(data["image_id"]) > 0
    assert isinstance(data["model_disclosure"], str) and len(data["model_disclosure"]) > 10
    assert isinstance(data["detections"], list)

    # Verify detection items
    for detection in data["detections"]:
        assert set(detection.keys()) == {"hazard_type", "confidence", "severity"}
        assert detection["hazard_type"] in ALLOWED_HAZARDS, f"Unexpected hazard: {detection['hazard_type']}"
        assert detection["severity"] in ALLOWED_SEVERITIES, f"Unexpected severity: {detection['severity']}"
        assert isinstance(detection["confidence"], (float, int))
        assert 0.0 <= detection["confidence"] <= 1.0
