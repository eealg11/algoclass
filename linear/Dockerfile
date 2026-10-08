# 파이썬 경량화 공식 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치 (캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY main.py .

# Gunicorn을 사용하여 프로덕션 WSGI 서버 실행 (PORT 환경변수 지원)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
