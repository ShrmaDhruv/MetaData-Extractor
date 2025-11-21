# Multi-stage build for MetaData Extractor
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source files and config
COPY index.html main.jsx style.css ./
COPY .postcssrc ./
COPY components ./components
COPY utils ./utils

# Build frontend
RUN npm run build

# Stage 2: Python backend with frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Upgrade pip and install Python dependencies with increased timeout
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=600 -r requirements.txt

# Copy Python application code
COPY main.py .
COPY Python ./Python
COPY utils ./utils
COPY models ./models
COPY data ./data

# Create uploads directory
RUN mkdir -p uploads

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/dist ./static

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

