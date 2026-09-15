"""
FastAPI Router for Computer Vision Module (API Contract v2 compliant)
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from .schemas import VisionAnalyzeRequest, VisionAnalyzeResponse
from .service import VisionService, get_vision_service

router = APIRouter(prefix="/api/v1/vision", tags=["Computer Vision"])


@router.post(
    "/analyze",
    response_model=VisionAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze disaster image for hazard indicators",
    description="Analyzes post-event satellite patch or disaster photo for hazard classification and severity."
)
async def analyze_disaster_image(
    request: VisionAnalyzeRequest,
    service: VisionService = Depends(get_vision_service)
) -> VisionAnalyzeResponse:
    """
    Official API Contract v2 endpoint: POST /api/v1/vision/analyze
    """
    try:
        response = service.analyze(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Computer vision analysis failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check for Computer Vision module"
)
async def vision_health(
    service: VisionService = Depends(get_vision_service)
) -> Dict[str, Any]:
    return service.get_health()


@router.get(
    "/demo-samples",
    summary="List curated demo samples for presentation"
)
async def list_demo_samples(
    service: VisionService = Depends(get_vision_service)
) -> List[Dict[str, Any]]:
    return service.get_demo_samples()
