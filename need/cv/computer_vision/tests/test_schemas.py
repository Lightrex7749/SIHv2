"""
Unit tests for Computer Vision Pydantic Schemas.
"""

import pytest
from pydantic import ValidationError
from computer_vision.schemas import (
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
    DetectionItem,
    HazardType,
    SeverityLevel
)


def test_valid_request():
    req = VisionAnalyzeRequest(
        image_url="sample/image.jpg",
        latitude=30.123,
        longitude=78.456
    )
    assert req.image_url == "sample/image.jpg"
    assert req.latitude == 30.123
    assert req.longitude == 78.456
    assert req.pre_image_url is None


def test_request_empty_image_url_fails():
    with pytest.raises(ValidationError):
        VisionAnalyzeRequest(
            image_url="",
            latitude=30.123,
            longitude=78.456
        )


def test_request_invalid_coordinates_fail():
    with pytest.raises(ValidationError):
        VisionAnalyzeRequest(
            image_url="test.jpg",
            latitude=95.0,  # Invalid latitude (> 90)
            longitude=78.456
        )

    with pytest.raises(ValidationError):
        VisionAnalyzeRequest(
            image_url="test.jpg",
            latitude=30.0,
            longitude=195.0  # Invalid longitude (> 180)
        )


def test_valid_response():
    resp = VisionAnalyzeResponse(
        image_id="IMG001",
        detections=[
            DetectionItem(
                hazard_type=HazardType.LANDSLIDE,
                confidence=0.87,
                severity=SeverityLevel.HIGH
            )
        ],
        model_disclosure="Indicative only — fine-tuned on public dataset."
    )
    assert resp.image_id == "IMG001"
    assert len(resp.detections) == 1
    assert resp.detections[0].hazard_type == HazardType.LANDSLIDE
    assert resp.detections[0].confidence == 0.87
    assert resp.detections[0].severity == SeverityLevel.HIGH
    assert "Indicative only" in resp.model_disclosure


def test_response_missing_disclosure_fails():
    with pytest.raises(ValidationError):
        # model_disclosure is mandatory per v2 contract
        VisionAnalyzeResponse(
            image_id="IMG001",
            detections=[]
            # model_disclosure omitted
        )


def test_detection_item_confidence_bounds():
    with pytest.raises(ValidationError):
        DetectionItem(
            hazard_type=HazardType.FLOOD,
            confidence=1.5,  # Out of bounds (> 1.0)
            severity=SeverityLevel.HIGH
        )

    with pytest.raises(ValidationError):
        DetectionItem(
            hazard_type=HazardType.FLOOD,
            confidence=-0.1,  # Out of bounds (< 0.0)
            severity=SeverityLevel.HIGH
        )
