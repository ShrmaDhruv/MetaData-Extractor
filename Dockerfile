FROM node:20-bookworm-slim AS frontend

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/index.html ./
COPY frontend/src ./src
RUN npm run build


FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    YOLO_CONFIG_DIR=/app/data/yolo_config \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
        tesseract-ocr \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-render.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install --index-url https://download.pytorch.org/whl/cpu \
        torch==2.5.1 \
        torchvision==0.20.1 \
    && pip install -r requirements-render.txt \
    && python -m spacy download en_core_web_md

COPY main.py ./
COPY Python ./Python
COPY models ./models
COPY --from=frontend /app/dist ./dist

RUN mkdir -p uploads data/extracted_figures data/yolo_config

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
