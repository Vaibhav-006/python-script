from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import logging
import sys

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

# ✅ Transcript input model
class TranscriptRequest(BaseModel):
    url: str
    language: str = "en"

# ✅ Transcript POST endpoint for YouTube
@app.post("/get-transcript/")
async def get_transcript_endpoint(req: TranscriptRequest):
    try:
        logger.info(f"Received request for URL: {req.url}")
        
        result = get_transcript.get_transcript(req.url, req.language)
        logger.info(f"Transcript result: {result}")
        
        # Map error types to appropriate HTTP status codes
        if not result.get("success", False):
            error_message = result.get("error", "Unknown error")
            status_code = 400  # Default to bad request
            
            if "unavailable" in error_message.lower():
                status_code = 404
            elif "disabled" in error_message.lower():
                status_code = 403
            elif "not found" in error_message.lower():
                status_code = 404
                
            logger.error(f"Error processing transcript: {error_message}")
            return JSONResponse(
                status_code=status_code,
                content={"success": False, "error": error_message}
            )
            
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Server error: {str(e)}"}
        )

# ✅ PDF Upload + Processing endpoint
@app.post("/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...), language: str = Form("en")):
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    result = process_pdf.extract_text_from_pdf(file_location, language)
    return result