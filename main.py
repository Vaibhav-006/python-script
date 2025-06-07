from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

import process_pdf  # Your custom module
import get_transcript  # Your custom module (must contain get_transcript function)

import re

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
        return get_transcript.get_transcript(req.url, req.language)
    except TranscriptsDisabled:
        return JSONResponse(status_code=403, content={"error": "Transcript is disabled for this video"})
    except NoTranscriptFound:
        return JSONResponse(status_code=404, content={"error": "No transcript found for this video"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ Optional GET-based transcript route (not needed if POST works fine)
@app.get("/api/transcript")
async def get_transcript_get(url: str, language: str = "en"):
    try:
        return get_transcript.get_transcript(url, language)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ✅ PDF Upload + Processing endpoint
@app.post("/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...), language: str = Form("en")):
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    result = process_pdf.extract_text_from_pdf(file_location, language)
    return result