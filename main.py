from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import shutil
import os
from Python.GrobidExtractor import grobid_available, extract_primary, merge_results
import json
import uuid


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DIST_DIR = os.path.join(BASE_DIR, "dist")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PDF_NAME = ""


def get_cors_origins():
    origins = os.getenv("CLIENT_ORIGINS", "*").strip()
    if origins == "*":
        return ["*"]
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def make_upload_filename(original_filename: str) -> tuple[str, str]:
    filename = os.path.basename(original_filename or "").strip()
    if not filename:
        raise HTTPException(status_code=400, detail="Invalid file name")
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    safe_name = "".join(
        char if char.isalnum() or char in " ._-" else "_" for char in filename
    ).strip()
    return f"{uuid.uuid4().hex}_{safe_name}", filename


def resolve_uploaded_file(filename: str | None) -> str:
    selected_filename = os.path.basename(filename or PDF_NAME).strip()
    if not selected_filename:
        raise HTTPException(status_code=400, detail="No file uploaded yet")

    file_path = os.path.join(UPLOAD_FOLDER, selected_filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Uploaded file was not found")

    return selected_filename



# LIFESPAN HANDLER (Replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # === Startup: delete old uploads ===
    folder = UPLOAD_FOLDER
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

    yield  # App runs here




app = FastAPI(lifespan=lifespan)


# CORS
cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# FILE UPLOAD ROUTE
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        stored_filename, original_filename = make_upload_filename(file.filename)
        file_location = os.path.join(UPLOAD_FOLDER, stored_filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        global PDF_NAME
        PDF_NAME = stored_filename

        return {
            "filename": stored_filename,
            "originalFilename": original_filename,
            "message": "File uploaded successfully",
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# PROCESS FILE ROUTE
@app.get("/process/")
async def process_file(filename: str | None = None):
    try:
        selected_filename = resolve_uploaded_file(filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, selected_filename)

        # Primary path: GROBID (fulltext + regex recovery)
        result = None
        if grobid_available():
            try:
                result = extract_primary(pdf_path)
            except Exception as e:
                print(f"GROBID failed, falling back to OCR: {e}")
        else:
            print("GROBID not reachable, falling back to OCR")

        # Fallback path: YOLO + Tesseract + regex (scanned PDFs / GROBID down).
        # Imported lazily so torch/YOLO only load when actually needed.
        if result is None or not result["ABSTRACT"]:
            import Python.OCR as my
            from Python.MetaData import SummarizeSection
            my.output(selected_filename)
            ocr_result = SummarizeSection()
            result = merge_results(result, ocr_result) if result else ocr_result

        # Ensure JSON serializable
        safe_json = json.loads(json.dumps(result, default=str))

        return JSONResponse(content=safe_json)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    if not os.path.isdir(DIST_DIR):
        return {"message": "API is running. Build the frontend to enable the web UI."}

    requested_file = os.path.join(DIST_DIR, full_path)
    if full_path and os.path.isfile(requested_file):
        return FileResponse(requested_file)

    return FileResponse(os.path.join(DIST_DIR, "index.html"))
