from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import process_pdf
import get_transcript

app = FastAPI()

# Allow CORS for all origins (for development; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For transcript endpoint
class TranscriptRequest(BaseModel):
    url: str
    language: str = "en"

@app.post("/process-pdf/")
async def process_pdf_endpoint(file: UploadFile = File(...), language: str = Form("en")):
    # Save the uploaded file
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    # Call your PDF processing logic (should return a dict)
    result = process_pdf.process(file_location, language)
    return result

@app.post("/get-transcript/")
async def get_transcript_endpoint(req: TranscriptRequest):
    # Call your transcript extraction logic (should return a dict)
    result = get_transcript.process(req.url, req.language)
    return result