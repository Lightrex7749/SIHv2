"""Optional EfficientNet disaster classifier supplied by the CV team."""

import hashlib
import logging
import os
from pathlib import Path

from .base import BaseVisionDetector
from ..preprocessing.image_loader import load_image, ImageLoadError
from ..schemas import (
    DetectionItem,
    HazardType,
    SeverityLevel,
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
)

logger = logging.getLogger("drishtisetu.cv.trained_classifier")


class TrainedDisasterClassifier(BaseVisionDetector):
    """Lazy-loaded EfficientNet-B0 classifier for local image files."""

    CLASSES = ("earthquake", "smoke", "landslide", "fire", "flood", "normal")
    MODEL_DISCLOSURE = (
        "EfficientNet-B0 classifier trained on the teammate-provided six-class "
        "disaster image dataset. It is a prototype image classifier, not an "
        "object detector, and predictions require visual review."
    )

    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path or os.getenv(
            "DRISHTISETU_CLASSIFIER_MODEL",
            str(Path(__file__).resolve().parents[1] / "models" / "best_disaster_model.pth")
        ))
        self._model = None
        self._transform = None
        self._torch = None

    def _load_model(self):
        if self._model is not None:
            return
        if not self.model_path.is_file():
            raise FileNotFoundError(f"Classifier model not found: {self.model_path}")

        import torch
        from torchvision import models, transforms
        from torchvision.transforms.functional import to_pil_image

        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(self.CLASSES))
        model.load_state_dict(torch.load(self.model_path, map_location="cpu", weights_only=True))
        model.eval()
        self._model = model
        self._torch = torch
        self._to_pil_image = to_pil_image
        self._transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])

    def analyze(self, request: VisionAnalyzeRequest) -> VisionAnalyzeResponse:
        self._load_model()
        try:
            image, _ = load_image(request.image_url)
        except ImageLoadError:
            raise

        with self._torch.no_grad():
            logits = self._model(self._transform(self._to_pil_image(image)).unsqueeze(0))
            probabilities = self._torch.softmax(logits, dim=1)[0]
            class_index = int(self._torch.argmax(probabilities).item())

        class_name = self.CLASSES[class_index]
        confidence = round(float(probabilities[class_index].item()), 4)
        hazard_map = {
            "landslide": HazardType.LANDSLIDE,
            "flood": HazardType.FLOOD,
            "fire": HazardType.UNKNOWN,
            "earthquake": HazardType.UNKNOWN,
            "smoke": HazardType.UNKNOWN,
            "normal": HazardType.UNKNOWN,
        }
        severity = (
            SeverityLevel.HIGH if confidence >= 0.85 else
            SeverityLevel.MODERATE if confidence >= 0.65 else
            SeverityLevel.LOW
        )
        if class_name == "normal":
            severity = SeverityLevel.LOW

        image_id = f"IMG-{hashlib.sha256(request.image_url.encode()).hexdigest()[:8].upper()}"
        return VisionAnalyzeResponse(
            image_id=image_id,
            detections=[DetectionItem(
                hazard_type=hazard_map[class_name],
                confidence=confidence,
                severity=severity,
            )],
            model_disclosure=self.MODEL_DISCLOSURE,
        )