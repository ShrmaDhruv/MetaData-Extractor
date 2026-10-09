# MetaData Extractor

FastAPI + React app for extracting metadata from research-paper PDFs using OCR and document-layout detection.

## Local Development

Install Python dependencies in the project virtual environment, then run the API:

```powershell
..\.venv\Scripts\pip.exe install -r requirements.txt
..\.venv\Scripts\python.exe -m spacy download en_core_web_md
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

In another terminal, run the frontend:

```powershell
cd frontend
npm install
npm start
```

The Parcel frontend will call `http://127.0.0.1:8000` during local development. In production, it uses same-origin API URLs.

## Render Deployment

Deploy this project on Render as a Docker web service. The Docker image is required because the OCR pipeline needs the system `tesseract-ocr` package in addition to Python dependencies.

Recommended setup:

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from the repository, or create a Docker Web Service manually.
3. Use `Dockerfile` as the Dockerfile path.
4. Use `/healthz` as the health check path.
5. Choose an instance with enough memory for PyTorch, spaCy, and the YOLO layout model. Very small/free instances may run out of memory during build or inference.

Render injects the `PORT` environment variable automatically. The Docker command starts FastAPI with:

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Generated OCR files and uploads are temporary runtime data and are not copied into the Docker image.
