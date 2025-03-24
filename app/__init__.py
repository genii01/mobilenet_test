from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api.endpoints import router
import os

app = FastAPI(
    title="MobileNet Image Classifier API",
    description="API for image classification using MobileNet v2",
    version="1.0.0",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static 디렉토리가 있을 경우에만 정적 파일 마운트
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# 루트 경로 핸들러
@app.get("/")
async def root():
    """
    루트 경로를 API 문서로 리다이렉트
    """
    return RedirectResponse(url="/docs")


# 라우터 등록
app.include_router(router, prefix="/api/v1")
