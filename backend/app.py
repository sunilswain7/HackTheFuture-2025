from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from datetime import datetime
import uuid
import shutil
import os
import spacy

from nlp_utils import get_redact_entities
from extraction.text_extraction import extract_text

app = FastAPI(title="SecureRedact AI API", version="1.0.0")

nlp = spacy.load("en_core_web_sm")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job tracking
processing_jobs = {}

@app.get("/")
async def root():
    return {"message": "SecureRedact AI API - Ready for Privacy Protection"}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    job_id = str(uuid.uuid4())
    uploaded_files_info = []

    try:
        for file in files:
            # Save uploaded file to a temporary location
            temp_dir = f"temp/{job_id}"
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Extract text using actual tools
            extracted_text = extract_text(file_path, file.content_type)

            # Use spaCy helper to get redactable entities
            redact_entities = get_redact_entities(extracted_text, nlp)

            uploaded_files_info.append({
                "filename": file.filename,
                "size": os.path.getsize(file_path),
                "content_type": file.content_type,
                "extracted_text": extracted_text,
                "redact_entities": redact_entities  # <-- add detected entities here
            })

        processing_jobs[job_id] = {
            "job_id": job_id,
            "status": "uploaded",
            "created_at": datetime.now().isoformat(),
            "total_files": len(files),
            "files": uploaded_files_info
        }

        return {
            "job_id": job_id,
            "status": "uploaded",
            "files_count": len(files),
            "message": "Files uploaded, text extracted, and entities detected successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return processing_jobs[job_id]

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(processing_jobs)
    }
