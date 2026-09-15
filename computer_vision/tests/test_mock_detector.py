"""
Unit tests for MockVisionDetector (Phase 1).
Validates determinism, curated demo scenarios, and required model_disclosure.
"""

import pytest
from computer_vision.detection.mock_detector import MockVisionDetector
from computer_vision.schemas import VisionAnalyzeRequest, HazardType, SeverityLevel


@pytest.fixture
def detector():
    return MockVisionDetector()


def test_landslide_scenario_by_keyword(detector):
    req = VisionAnalyzeRequest(
        image_url="assets/sample_landslide_scar.jpg",
        latitude=20.0,
        longitude=75.0
    )
    resp = detector.analyze(req)
    assert resp.image_id == "IMG_CHAMOLI_LS_01"
    assert len(resp.detections) >= 1
    assert resp.detections[0].hazard_type == HazardType.LANDSLIDE
    assert resp.detections[0].confidence == 0.87
    assert resp.detections[0].severity == SeverityLevel.HIGH
    assert "Sen1Floods11" in resp.model_disclosure
    assert "Landslide4Sense" in resp.model_disclosure


def test_landslide_scenario_by_coordinates(detector):
    # Chamoli / Joshimath coordinates
    req = VisionAnalyzeRequest(
        image_url="satellite/patch_01.tif",
        latitude=30.552,
        longitude=79.566
    )
    resp = detector.analyze(req)
    assert resp.image_id == "IMG_CHAMOLI_LS_01"
    assert resp.detections[0].hazard_type == HazardType.LANDSLIDE


def test_flood_scenario_by_keyword(detector):
    req = VisionAnalyzeRequest(
        image_url="drone/flood_water_extent.png",
        latitude=15.0,
        longitude=80.0
    )
    resp = detector.analyze(req)
    assert resp.image_id == "IMG_BRAHMAPUTRA_FLD_02"
    assert resp.detections[0].hazard_type == HazardType.FLOOD
    assert resp.detections[0].confidence == 0.92
    assert resp.detections[0].severity == SeverityLevel.HIGH


def test_flood_scenario_by_coordinates(detector):
    # Assam / Brahmaputra coordinates
    req = VisionAnalyzeRequest(
        image_url="imagery/unlabeled_patch.jpg",
        latitude=26.185,
        longitude=92.931
    )
    resp = detector.analyze(req)
    assert resp.image_id == "IMG_BRAHMAPUTRA_FLD_02"
    assert resp.detections[0].hazard_type == HazardType.FLOOD


def test_infrastructure_scenario(detector):
    req = VisionAnalyzeRequest(
        image_url="site/wayanad_bridge_infrastructure.png",
        latitude=11.685,
        longitude=76.132
    )
    resp = detector.analyze(req)
    assert resp.image_id == "IMG_WAYANAD_INFRA_03"
    assert resp.detections[0].hazard_type == HazardType.INFRASTRUCTURE_DAMAGE
    assert resp.detections[0].severity == SeverityLevel.MODERATE


def test_stable_baseline_scenario(detector):
    req = VisionAnalyzeRequest(
        image_url="survey/safe_plateau.jpg",
        latitude=28.0,
        longitude=77.0
    )
    resp = detector.analyze(req)
    assert resp.image_id == "IMG_PLATEAU_SAFE_04"
    assert resp.detections[0].hazard_type == HazardType.UNKNOWN
    assert resp.detections[0].severity == SeverityLevel.LOW


def test_determinism_across_multiple_runs(detector):
    """Asserts that identical inputs produce 100% identical outputs every time."""
    req = VisionAnalyzeRequest(
        image_url="arbitrary/random_image_99.png",
        latitude=18.421,
        longitude=73.856
    )
    first_resp = detector.analyze(req)

    for _ in range(5):
        subsequent_resp = detector.analyze(req)
        assert first_resp.image_id == subsequent_resp.image_id
        assert len(first_resp.detections) == len(subsequent_resp.detections)
        assert first_resp.detections[0].hazard_type == subsequent_resp.detections[0].hazard_type
        assert first_resp.detections[0].confidence == subsequent_resp.detections[0].confidence
        assert first_resp.detections[0].severity == subsequent_resp.detections[0].severity
        assert first_resp.model_disclosure == subsequent_resp.model_disclosure


def test_model_disclosure_presence_and_truthfulness(detector):
    req = VisionAnalyzeRequest(
        image_url="test.jpg",
        latitude=22.0,
        longitude=88.0
    )
    resp = detector.analyze(req)
    assert hasattr(resp, "model_disclosure")
    assert resp.model_disclosure is not None
    assert len(resp.model_disclosure) > 20
    assert "mock detector for demo purposes" in resp.model_disclosure
