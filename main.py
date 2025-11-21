from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import Python.OCR as my
from Python.page2 import SummarizeSection
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PDF_NAME = ""


# ====================================================
# DELETE ALL FILES IN uploads/ WHEN BACKEND STARTS
# ====================================================
@app.on_event("startup")
async def clean_uploads_folder():
    folder = UPLOAD_FOLDER
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        global PDF_NAME
        PDF_NAME = file.filename
        return {"filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/process/")
async def process_file():
    global PDF_NAME
    if not PDF_NAME:
        return {"error": "No file uploaded yet"}
    try:
        my.output(PDF_NAME)
        result = SummarizeSection()

        # Ensure JSON safe format
        safe_json = json.loads(json.dumps(result, default=str))

        return JSONResponse(content=safe_json)
    except Exception as e:
        return {"error": str(e)}


# Serve static files (frontend) if static directory exists (production/Docker)
# API routes defined above will be matched first, then static files are served
if os.path.exists("static"):
    from fastapi.responses import FileResponse
    
    # Serve root with index.html
    @app.get("/")
    async def read_root():
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not built"}
    
    # Catch-all for static assets and SPA routing
    # FastAPI matches specific routes first, so /upload/ and /process/ work correctly
    @app.get("/{full_path:path}")
    async def serve_static_or_spa(full_path: str):
        # Skip API routes (with or without trailing slash)
        if full_path in ("upload", "upload/", "process", "process/") or full_path.startswith(("api/", "docs", "openapi.json", "redoc")):
            return {"error": "Not found"}
        
        # Try to serve the requested file from static directory
        file_path = os.path.join("static", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise serve index.html for SPA routing
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend not found"}
