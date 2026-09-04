# Not validated against a live Docker daemon in this build's environment
# (none was available) -- review before relying on it in production. See
# the README's Deployment section for the same caveat.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-asm \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY ai/ ./ai/
COPY backend/ ./backend/
COPY data/ ./data/

RUN mkdir -p storage/uploads storage/processed storage/verified storage/reports

WORKDIR /app/backend
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
