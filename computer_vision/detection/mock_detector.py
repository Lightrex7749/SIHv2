"""
Mock Vision Detector - Phase 1 Deterministic Demonstration Engine (API Contract v2 compliant)
"""

import hashlib
from typing import Dict, Any, List
from .base import BaseVisionDetector
from ..schemas import (
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
    DetectionItem,
    HazardType,
    SeverityLevel,
)


class MockVisionDetector(BaseVisionDetector):
    """
    High-reliability mock detector engineered for hackathon presentation and contract adherence.
    Provides 100% deterministic outputs for fixed demo scenarios and reproducible hash-based
    outputs for arbitrary inputs.
    """

    MODEL_DISCLOSURE: str = (
        "Prototype uses a rule-based/mock detector for demo purposes. Production "
        "implementation would use a model fine-tuned on Sen1Floods11 (flood) and "
        "Landslide4Sense (landslide), both public benchmark datasets."
    )

    # 4 Predefined Demo Scenarios aligned with DEMO_FLOW.md
    DEMO_CATALOG: Dict[str, Dict[str, Any]] = {
        "landslide": {
            "image_id": "IMG_CHAMOLI_LS_01",
            "detections": [
                {
                    "hazard_type": HazardType.LANDSLIDE,
                    "confidence": 0.87,
                    "severity": SeverityLevel.HIGH,
                }
            ],
            "description": "Slope displacement and scarp formation identified along steep habitation ridge (Chamoli/Joshimath sector)."
        },
        "flood": {
            "image_id": "IMG_BRAHMAPUTRA_FLD_02",
            "detections": [
                {
                    "hazard_type": HazardType.FLOOD,
                    "confidence": 0.92,
                    "severity": SeverityLevel.HIGH,
                }
            ],
            "description": "Extensive surface water inundation submerging access roads and low-lying residential clusters."
        },
        "infrastructure": {
            "image_id": "IMG_WAYANAD_INFRA_03",
            "detections": [
                {
                    "hazard_type": HazardType.INFRASTRUCTURE_DAMAGE,
                    "confidence": 0.79,
                    "severity": SeverityLevel.MODERATE,
                }
            ],
            "description": "Erosion scour cutting through rural link bridge and retaining structure."
        },
        "baseline": {
            "image_id": "IMG_PLATEAU_SAFE_04",
            "detections": [
                {
                    "hazard_type": HazardType.UNKNOWN,
                    "confidence": 0.15,
                    "severity": SeverityLevel.LOW,
                }
            ],
            "description": "Vegetated plateau showing uniform ground cover with no critical hazard anomalies."
        },
        "coastal": {
            "image_id": "IMG_PURI_COASTAL_05",
            "detections": [
                {
                    "hazard_type": HazardType.COASTAL_EROSION,
                    "confidence": 0.84,
                    "severity": SeverityLevel.HIGH,
                }
            ],
            "description": "Active shoreline recession and seawall scouring observed."
        },
        "cloudburst": {
            "image_id": "IMG_KEDARNATH_CB_06",
            "detections": [
                {
                    "hazard_type": HazardType.CLOUD_BURST_IMPACT,
                    "confidence": 0.89,
                    "severity": SeverityLevel.CRITICAL,
                }
            ],
            "description": "Debris fan accumulation and sudden flash gully expansion from torrential cloudburst."
        }
    }

    def analyze(self, request: VisionAnalyzeRequest) -> VisionAnalyzeResponse:
        """
        Deterministically evaluates the request based on URL keyword matches,
        coordinate proximity, or stable SHA-256 hash.
        """
        url_lower = request.image_url.lower()

        # 1. Match by keyword in image_url / filename
        matched_key = None
        for key in ["landslide", "flood", "infrastructure", "baseline", "safe", "coastal", "cloudburst"]:
            if key in url_lower:
                matched_key = "baseline" if key == "safe" else key
                break

        # 2. Match by geographic pilot coordinates if not matched by filename
        if not matched_key:
            # Uttarakhand / Chamoli area (~30.0 - 30.8 N, 79.0 - 80.0 E) -> Landslide
            if 29.5 <= request.latitude <= 31.5 and 78.0 <= request.longitude <= 80.5:
                matched_key = "landslide"
            # Assam / Brahmaputra basin (~25.5 - 27.5 N, 91.0 - 95.0 E) -> Flood
            elif 25.0 <= request.latitude <= 28.0 and 90.0 <= request.longitude <= 96.0:
                matched_key = "flood"
            # Kerala / Western Ghats (~9.5 - 12.5 N, 75.5 - 77.5 E) -> Infrastructure / Landslide
            elif 9.0 <= request.latitude <= 13.0 and 75.0 <= request.longitude <= 77.5:
                matched_key = "infrastructure"

        # 3. If matched, return the curated demonstration scenario
        if matched_key and matched_key in self.DEMO_CATALOG:
            scenario = self.DEMO_CATALOG[matched_key]
            return VisionAnalyzeResponse(
                image_id=scenario["image_id"],
                detections=[
                    DetectionItem(**d) for d in scenario["detections"]
                ],
                model_disclosure=self.MODEL_DISCLOSURE
            )

        # 4. Fallback: Stable deterministic hash for arbitrary input
        digest = hashlib.sha256(f"{request.image_url}_{request.latitude}_{request.longitude}".encode()).hexdigest()
        image_id = f"IMG-{digest[:8].upper()}"

        # Deterministic pseudo-random selections based on hash
        hazard_candidates = [
            HazardType.LANDSLIDE,
            HazardType.FLOOD,
            HazardType.INFRASTRUCTURE_DAMAGE,
            HazardType.COASTAL_EROSION,
            HazardType.UNKNOWN
        ]
        hazard_idx = int(digest[8:10], 16) % len(hazard_candidates)
        selected_hazard = hazard_candidates[hazard_idx]

        # Deterministic confidence between 0.65 and 0.94
        raw_conf = 0.65 + (int(digest[10:12], 16) % 30) / 100.0
        confidence = round(raw_conf, 2)

        if confidence >= 0.85:
            severity = SeverityLevel.HIGH
        elif confidence >= 0.70:
            severity = SeverityLevel.MODERATE
        else:
            severity = SeverityLevel.LOW

        detections = []
        if selected_hazard != HazardType.UNKNOWN:
            detections.append(
                DetectionItem(
                    hazard_type=selected_hazard,
                    confidence=confidence,
                    severity=severity
                )
            )
        else:
            detections.append(
                DetectionItem(
                    hazard_type=HazardType.UNKNOWN,
                    confidence=0.20,
                    severity=SeverityLevel.LOW
                )
            )

        return VisionAnalyzeResponse(
            image_id=image_id,
            detections=detections,
            model_disclosure=self.MODEL_DISCLOSURE
        )
