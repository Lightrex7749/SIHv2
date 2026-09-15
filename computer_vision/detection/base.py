"""
Base Vision Detector Abstract Interface
"""

from abc import ABC, abstractmethod
from ..schemas import VisionAnalyzeRequest, VisionAnalyzeResponse


class BaseVisionDetector(ABC):
    """
    Abstract base detector for all DrishtiSetu Computer Vision modules.
    Guarantees strict compliance with API Contract v2.
    """

    @abstractmethod
    def analyze(self, request: VisionAnalyzeRequest) -> VisionAnalyzeResponse:
        """
        Processes an analysis request and returns a contract-compliant VisionAnalyzeResponse.
        Must include the mandatory model_disclosure string.
        """
        pass
