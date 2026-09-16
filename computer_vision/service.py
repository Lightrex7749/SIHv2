"""
DrishtiSetu Computer Vision - Unified Service Orchestrator
"""

import os
import logging
from typing import Optional, Dict, Any, List

from .schemas import VisionAnalyzeRequest, VisionAnalyzeResponse
from .detection.base import BaseVisionDetector
from .detection.mock_detector import MockVisionDetector
from .detection.trained_classifier import TrainedDisasterClassifier
from .change_detection.spectral_differencing import SatelliteChangeDetector

logger = logging.getLogger("drishtisetu.cv.service")


class VisionService:
    """
    Central orchestration service for Computer Vision disaster analysis.
    Supports seamless switching between Phase 1 (deterministic demo mock)
    and Phase 2 (satellite change detection).
    """

    def __init__(self, mode: str = "mock"):
        """
        mode: 'mock', 'trained', 'change_detection', or 'auto'
        """
        self.mode = os.getenv("DRISHTISETU_CV_MODE", mode).lower()
        self.mock_detector = MockVisionDetector()
        self.trained_classifier = TrainedDisasterClassifier()
        self.change_detector = SatelliteChangeDetector()
        logger.info(f"Initialized DrishtiSetu VisionService in mode: {self.mode}")

    def analyze(self, request: VisionAnalyzeRequest) -> VisionAnalyzeResponse:
        """
        Executes hazard analysis according to active mode.
        Guarantees that no exception crashes the calling service.
        """
        try:
            if self.mode == "change_detection" or (self.mode == "auto" and request.pre_image_url):
                return self.change_detector.analyze(request)
            if self.mode == "trained":
                return self.trained_classifier.analyze(request)
            else:
                return self.mock_detector.analyze(request)
        except Exception as e:
            logger.error(f"Vision analysis error in mode '{self.mode}': {e}. Falling back to mock engine.")
            return self.mock_detector.analyze(request)

    def get_health(self) -> Dict[str, Any]:
        """Returns health and readiness status of the CV module."""
        return {
            "status": "ok",
            "module": "computer_vision",
            "mode": self.mode,
            "api_contract": "v2",
            "supported_hazards": [
                "LANDSLIDE",
                "FLOOD",
                "COASTAL_EROSION",
                "CLOUD_BURST_IMPACT",
                "INFRASTRUCTURE_DAMAGE",
                "UNKNOWN"
            ]
        }

    def get_demo_samples(self) -> List[Dict[str, Any]]:
        """
        Returns a catalog of verified demo scenarios for live presentation testing.
        """
        return [
            {
                "id": "chamoli_landslide",
                "title": "Chamoli/Joshimath Landslide Scar",
                "request": {
                    "image_url": "computer_vision/demo_assets/chamoli_landslide_post.png",
                    "latitude": 30.552,
                    "longitude": 79.566,
                    "pre_image_url": "computer_vision/demo_assets/chamoli_landslide_pre.png"
                },
                "expected_hazard": "LANDSLIDE",
                "expected_severity": "HIGH",
                "notes": "Slope failure and vegetative loss on steep Himalayan habitation ridge."
            },
            {
                "id": "brahmaputra_flood",
                "title": "Brahmaputra Basin Flood Inundation",
                "request": {
                    "image_url": "computer_vision/demo_assets/brahmaputra_flood_post.png",
                    "latitude": 26.185,
                    "longitude": 92.931,
                    "pre_image_url": "computer_vision/demo_assets/brahmaputra_flood_pre.png"
                },
                "expected_hazard": "FLOOD",
                "expected_severity": "HIGH",
                "notes": "River overflow inundating agrarian settlements and road networks."
            },
            {
                "id": "wayanad_infrastructure",
                "title": "Wayanad Bridge & Road Scour",
                "request": {
                    "image_url": "computer_vision/demo_assets/bridge_washout_post.png",
                    "latitude": 11.685,
                    "longitude": 76.132
                },
                "expected_hazard": "INFRASTRUCTURE_DAMAGE",
                "expected_severity": "MODERATE",
                "notes": "Flash runoff breaching embankment and rural bridge abutment."
            },
            {
                "id": "stable_plateau",
                "title": "Safe Candidate Relocation Plateau",
                "request": {
                    "image_url": "computer_vision/demo_assets/stable_plateau_post.png",
                    "latitude": 30.210,
                    "longitude": 78.850
                },
                "expected_hazard": "UNKNOWN",
                "expected_severity": "LOW",
                "notes": "Stable terrain with uniform vegetative baseline and no hazard anomalies."
            }
        ]


# Singleton instance for simple integration
vision_service = VisionService()


def get_vision_service() -> VisionService:
    return vision_service
