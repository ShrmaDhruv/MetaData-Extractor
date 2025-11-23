from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import shutil
import os
import Python.OCR as my
from Python.MetaData import SummarizeSection
import json


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PDF_NAME = ""



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

    # === Shutdown (optional) ===
    # Add shutdown code here if needed


app = FastAPI(lifespan=lifespan)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# FILE UPLOAD ROUTE
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


# PROCESS FILE ROUTE
@app.get("/process/")
async def process_file():
    global PDF_NAME

    if not PDF_NAME:
        return {"error": "No file uploaded yet"}

    try:
        my.output(PDF_NAME)
        result = SummarizeSection()

        # Ensure JSON serializable
        safe_json = json.loads(json.dumps(result, default=str))

        return JSONResponse(content=safe_json)

    except Exception as e:
        return {"error": str(e)}
