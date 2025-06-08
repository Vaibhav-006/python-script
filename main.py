from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import logging
import sys
from typing import Optional

import process_pdf  # Your custom module
import get_transcript  # Your custom module (must contain get_transcript function)

import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# ✅ CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root route for health check
@app.get("/")
def read_root():
    return {"message": "Your app is live!"}

# ✅ Transcript input model with validation
class TranscriptRequest(BaseModel):
    url: str
    language: str = "en"

    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "language": "en"
            }
        }

# ✅ Transcript POST endpoint for YouTube
@app.post("/get-transcript/")
async def get_transcript_endpoint(req: TranscriptRequest):
    try:
        logger.info(f"Received request for URL: {req.url}")
        
        try:
            result = get_transcript.get_transcript(req.url, req.language)
            logger.info(f"Successfully retrieved transcript for video")
            return JSONResponse(content=result)
            
        except get_transcript.TranscriptError as e:
            logger.error(f"Transcript error: {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": e.message,
                    "error_type": e.__class__.__name__
                }
            )
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "An unexpected error occurred",
                "error_type": "UnexpectedError"
            }
        )

# ✅ PDF Upload + Processing endpoint
@app.post("/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...), language: str = Form("en")):
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        result = process_pdf.extract_text_from_pdf(file_location, language)
        return result
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Error processing PDF file",
                "error_type": "PDFProcessingError"
            }
        )