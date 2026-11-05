# ==============================================================
# Google Cloud Run 배포를 위한 다목적 경량 Dockerfile (Heap & Counting Sort)
# ==============================================================

FROM python:3.11-slim

# 표준 출력/에러 버퍼링 방지 (로그 즉시 출력)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# 작업 디렉터리 생성 및 설정
WORKDIR /app

# 패키지 목록 복사 및 설치 (캐시 레이어 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Cloud Run 기본 포트 8080 노출
EXPOSE 8080

# Cloud Run 컨테이너 기동 명령어 (환경변수 PORT를 주입받아 바인딩, 기본값 8080)
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

