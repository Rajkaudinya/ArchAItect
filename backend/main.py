"""FastAPI app — exposes the agentic pipeline over HTTP.

Endpoints:
  POST /api/extract-text   -> extract text from an uploaded file (pdf/txt/md)
  POST /api/analyze        -> stream the pipeline as Server-Sent Events (SSE)
"""
import json
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pypdf import PdfReader

from orchestrator import run_pipeline

app = FastAPI(title="ArchAItect API")

# Vite dev server runs on 5173 by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    document: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """Pull plain text out of an uploaded .pdf / .txt / .md file."""
    raw = await file.read()
    name = (file.filename or "").lower()
    try:
        if name.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(raw))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text = raw.decode("utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")
    return {"text": text.strip()}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    """Run the pipeline, streaming each step as an SSE event."""
    doc = req.document.strip()
    if len(doc) < 30:
        raise HTTPException(status_code=400, detail="Document is too short to analyze.")

    def event_stream():
        try:
            for event in run_pipeline(doc):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
