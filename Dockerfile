# Python 3.12 이미지를 기반으로 함
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 시스템 및 Python 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry 가상환경 생성하지 않도록 설정
RUN poetry config virtualenvs.create false

# 프로젝트 의존성 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치 (--no-dev 대신 --only main 사용)
RUN poetry install --only main --no-interaction --no-ansi --no-root

# 소스코드 복사
COPY . .

# 포트 설정
EXPOSE 8000

# 실행 명령어
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 