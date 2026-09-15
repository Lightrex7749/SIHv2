"""
DrishtiSetu Computer Vision Module - Pydantic Schemas (API Contract v2 compliant)
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class HazardType(str, Enum):
    LANDSLIDE = "LANDSLIDE"
    FLOOD = "FLOOD"
    COASTAL_EROSION = "COASTAL_EROSION"
    CLOUD_BURST_IMPACT = "CLOUD_BURST_IMPACT"
    INFRASTRUCTURE_DAMAGE = "INFRASTRUCTURE_DAMAGE"
    UNKNOWN = "UNKNOWN"


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectionItem(BaseModel):
    hazard_type: HazardType = Field(
        ...,
        description="Type of disaster hazard detected from visual data"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 (never fabricated on real images)"
    )
    severity: SeverityLevel = Field(
        ...,
        description="Assessed severity level of the hazard"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "hazard_type": "LANDSLIDE",
                "confidence": 0.87,
                "severity": "HIGH"
            }
        }
    }


class VisionAnalyzeRequest(BaseModel):
    image_url: str = Field(
        ...,
        min_length=1,
        description="URL, local file path, or base64 data string of the primary post-event image/satellite patch"
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="WGS84 Latitude of the visual observation"
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="WGS84 Longitude of the visual observation"
    )
    pre_image_url: Optional[str] = Field(
        default=None,
        description="Optional pre-event baseline image/patch URL or path for multi-temporal change detection"
    )

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("image_url cannot be empty or whitespace")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "image_url": "sample/chamoli_landslide.jpg",
                "latitude": 30.123,
                "longitude": 78.456,
                "pre_image_url": "sample/chamoli_pre.jpg"
            }
        }
    }


class VisionAnalyzeResponse(BaseModel):
    image_id: str = Field(
        ...,
        description="Unique identifier for the processed image observation"
    )
    detections: List[DetectionItem] = Field(
        default_factory=list,
        description="List of detected disaster hazard indicators"
    )
    model_disclosure: str = Field(
        ...,
        description="Mandatory transparency disclosure of the underlying model, training data, and prototype status"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "image_id": "IMG001",
                "detections": [
                    {
                        "hazard_type": "LANDSLIDE",
                        "confidence": 0.87,
                        "severity": "HIGH"
                    }
                ],
                "model_disclosure": "Prototype uses a rule-based/mock detector for demo purposes. Production implementation would use a model fine-tuned on Sen1Floods11 (flood) and Landslide4Sense (landslide), both public benchmark datasets."
            }
        }
    }
