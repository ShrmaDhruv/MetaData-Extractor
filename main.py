from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

        # FORCE PURE JSON SAFE FORMAT
        safe_json = json.loads(json.dumps(result, default=str))

        return JSONResponse(content=safe_json)
    except Exception as e:
        return {"error": str(e)}

