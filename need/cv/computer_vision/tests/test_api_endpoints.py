"""
Unit and integration tests for Computer Vision FastAPI endpoints using TestClient.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from computer_vision.router import router as vision_router

app = FastAPI(title="DrishtiSetu Test App")
app.include_router(vision_router)
client = TestClient(app)


def test_api_health():
    response = client.get("/api/v1/vision/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["module"] == "computer_vision"
    assert data["api_contract"] == "v2"


def test_api_demo_samples():
    response = client.get("/api/v1/vision/demo-samples")
    assert response.status_code == 200
    samples = response.json()
    assert isinstance(samples, list)
    assert len(samples) >= 4
    sample_ids = [s["id"] for s in samples]
    assert "chamoli_landslide" in sample_ids
    assert "brahmaputra_flood" in sample_ids


def test_api_analyze_valid_landslide():
    payload = {
        "image_url": "sample/chamoli_landslide.jpg",
        "latitude": 30.552,
        "longitude": 79.566
    }
    response = client.post("/api/v1/vision/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "image_id" in data
    assert "detections" in data
    assert "model_disclosure" in data
    assert len(data["detections"]) > 0

    first_det = data["detections"][0]
    assert first_det["hazard_type"] == "LANDSLIDE"
    assert first_det["severity"] == "HIGH"
    assert isinstance(first_det["confidence"], float)
    assert "Sen1Floods11" in data["model_disclosure"]


def test_api_analyze_missing_field_returns_422():
    # Missing image_url
    invalid_payload = {
        "latitude": 30.123,
        "longitude": 78.456
    }
    response = client.post("/api/v1/vision/analyze", json=invalid_payload)
    assert response.status_code == 422


def test_api_analyze_invalid_coords_returns_422():
    invalid_payload = {
        "image_url": "sample.jpg",
        "latitude": 120.0,  # Invalid
        "longitude": 78.456
    }
    response = client.post("/api/v1/vision/analyze", json=invalid_payload)
    assert response.status_code == 422
