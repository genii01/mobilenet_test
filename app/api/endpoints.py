from fastapi import APIRouter, UploadFile, HTTPException, File
from app.models.classifier import ImageClassifier
from app.schemas.request_response import (
    PredictionResponse,
    ErrorResponse,
    Base64ImageRequest,
    HealthResponse,
)
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
classifier = ImageClassifier()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    API 헬스 체크 엔드포인트
    """
    return HealthResponse(status="healthy")


@router.post(
    "/predict/upload",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def predict_image_upload(file: UploadFile = File(...), top_k: Optional[int] = 5):
    """
    이미지 파일 업로드를 통한 예측 엔드포인트
    """
    try:
        # 이미지 확장자 검증
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file.",
            )

        # 이미지 데이터 읽기
        image_data = await file.read()

        # 예측 수행
        predictions = await classifier.predict_image(image_data, top_k)

        return PredictionResponse(predictions=predictions)

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred during prediction: {str(e)}"
        )


@router.post(
    "/predict/base64",
    response_model=PredictionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def predict_base64_image(request: Base64ImageRequest):
    """
    Base64 인코딩된 이미지를 통한 예측 엔드포인트
    """
    try:
        predictions = await classifier.predict_base64_image(
            request.image, request.top_k
        )
        return PredictionResponse(predictions=predictions)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An error occurred during prediction: {str(e)}"
        )
