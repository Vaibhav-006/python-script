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
        result = get_transcript.get_transcript(req.url, req.language)
        if not result.get("success", False):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": result.get("error", "Unknown error")}
            )
        return JSONResponse(content=result)
    except Exception as e:
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