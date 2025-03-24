from pydantic import BaseModel, Field
from typing import List, Tuple


class PredictionResponse(BaseModel):
    predictions: List[Tuple[str, float]]
    message: str = "Prediction completed successfully"


class ErrorResponse(BaseModel):
    message: str
    error: str


class Base64ImageRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image string")
    top_k: int = Field(default=5, description="Number of top predictions to return")


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
