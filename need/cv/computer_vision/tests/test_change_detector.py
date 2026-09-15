"""
Unit tests for SatelliteChangeDetector (Phase 2 bi-temporal change detection).
"""

import os
import pytest
from computer_vision.change_detection.spectral_differencing import SatelliteChangeDetector
from computer_vision.schemas import VisionAnalyzeRequest, HazardType, SeverityLevel

DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "demo_assets")


@pytest.fixture
def change_detector():
    return SatelliteChangeDetector(demo_assets_dir=DEMO_DIR)


def test_landslide_change_detection(change_detector):
    post_path = os.path.join(DEMO_DIR, "chamoli_landslide_post.png")
    pre_path = os.path.join(DEMO_DIR, "chamoli_landslide_pre.png")

    req = VisionAnalyzeRequest(
        image_url=post_path,
        latitude=30.552,
        longitude=79.566,
        pre_image_url=pre_path
    )
    resp = change_detector.analyze(req)

    assert resp.image_id.startswith("IMG_SAT_")
    assert len(resp.detections) >= 1
    assert resp.detections[0].hazard_type == HazardType.LANDSLIDE
    assert resp.detections[0].severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    assert 0.65 <= resp.detections[0].confidence <= 0.98
    assert "Bi-temporal change detection pipeline" in resp.model_disclosure


def test_flood_change_detection(change_detector):
    post_path = os.path.join(DEMO_DIR, "brahmaputra_flood_post.png")
    pre_path = os.path.join(DEMO_DIR, "brahmaputra_flood_pre.png")

    req = VisionAnalyzeRequest(
        image_url=post_path,
        latitude=26.185,
        longitude=92.931,
        pre_image_url=pre_path
    )
    resp = change_detector.analyze(req)

    assert resp.image_id.startswith("IMG_SAT_")
    assert len(resp.detections) >= 1
    assert resp.detections[0].hazard_type == HazardType.FLOOD
    assert resp.detections[0].severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    assert 0.70 <= resp.detections[0].confidence <= 0.98


def test_unchanged_baseline_detection(change_detector):
    pre_path = os.path.join(DEMO_DIR, "stable_plateau_post.png")
    req = VisionAnalyzeRequest(
        image_url=pre_path,
        latitude=30.210,
        longitude=78.850,
        pre_image_url=pre_path  # Identical pre and post
    )
    resp = change_detector.analyze(req)

    assert resp.detections[0].hazard_type == HazardType.UNKNOWN
    assert resp.detections[0].severity == SeverityLevel.LOW


def test_missing_files_fallback_without_crash(change_detector):
    req = VisionAnalyzeRequest(
        image_url="non_existent_satellite_file.png",
        latitude=30.552,
        longitude=79.566
    )
    # Must never raise an unhandled exception or crash the service
    resp = change_detector.analyze(req)
    assert resp.image_id.startswith("IMG_SAT_")
    assert len(resp.detections) >= 1
    assert "model_disclosure" in resp.model_dump()
