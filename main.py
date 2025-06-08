from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import logging
import sys
import os
from typing import Optional

import google.generativeai as genai

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

# ✅ Translation input model for Gemini
class TranslationRequest(BaseModel):
    text: str
    target_language: str = "en"

    class Config:
        schema_extra = {
            "example": {
                "text": "Hello world!",
                "target_language": "hi" # Hindi
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

# ✅ Translation POST endpoint using Gemini API
@app.post("/translate/")
async def translate_endpoint(req: TranslationRequest):
    try:
        logger.info(f"Received translation request for target language: {req.target_language}")

        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable not set.")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Server configuration error: Gemini API Key not set.",
                    "error_type": "ConfigurationError"
                }
            )

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"Translate the following text to {req.target_language}:\n\n{req.text}"
        response = model.generate_content(prompt)
        
        # Assuming the translated text is directly in response.text
        translated_text = response.text

        logger.info(f"Successfully translated text to {req.target_language} using Gemini")
        return JSONResponse(
            content={
                "success": True,
                "translated_text": translated_text,
                "source_text": req.text,
                "target_language": req.target_language
            }
        )

    except Exception as e:
        logger.error(f"Error during Gemini translation: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Translation failed via Gemini: {str(e)}",
                "error_type": "GeminiTranslationError"
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