import os
import json
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from app.config import settings
from app.services.parser import DocumentParser
from app.services.analyzer_v2 import get_analyzer
from app.services.exporter import ArchitectureExporter
from app.models.analysis import AnalysisResult

logger = logging.getLogger(__name__)
router = APIRouter()

def get_analyses_file(project_id: str) -> str:
    return os.path.join(settings.DATA_DIR, f"analysis_{project_id}.json")

def get_text_file(project_id: str) -> str:
    return os.path.join(settings.DATA_DIR, f"text_{project_id}.txt")

class ClarificationAnswer(BaseModel):
    question: str
    answer: str

class ClarifyRequest(BaseModel):
    answers: List[ClarificationAnswer]

@router.post("/upload", response_model=AnalysisResult)
async def upload_requirement_document(
    project_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and analyze a requirements document using advanced NLP.
    Supports: .txt, .md, .pdf, .docx
    
    Production-grade endpoint with:
    - File size validation
    - Comprehensive error handling
    - Performance logging
    - Sanitized responses
    """
    try:
        # Verify file content
        contents = await file.read()
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        
        # Validate file size
        file_size = len(contents)
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({file_size} bytes) exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE} bytes)"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )
        
        logger.info(f"Processing file: {filename} ({file_size} bytes) for project: {project_id}")
        
        print(f"\n{'='*60}")
        print(f"📁 Processing file: {filename}")
        print(f"📊 Project ID: {project_id}")
        print(f"📏 File size: {file_size:,} bytes")
        print(f"{'='*60}\n")
        
        # 1. Parse File Content
        if ext == ".txt" or ext == ".md":
            parsed = DocumentParser.parse_txt(contents)
        elif ext == ".pdf":
            parsed = DocumentParser.parse_pdf(contents)
        elif ext == ".docx":
            parsed = DocumentParser.parse_docx(contents)
        else:
            # Fallback to general text decode attempts
            try:
                parsed = DocumentParser.parse_txt(contents)
            except Exception as e:
                logger.error(f"Failed to parse file {filename}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported format: {ext}. Supported formats: .txt, .md, .pdf, .docx"
                )
                
        if not parsed.get("success", False) and "text" not in parsed:
            error_msg = parsed.get("error", "Error parsing file")
            logger.error(f"File parsing failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
            
        requirement_text = parsed["text"]
        sections = parsed.get("sections", {})
        
        if not requirement_text or len(requirement_text.strip()) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document content is too short. Please provide a comprehensive requirements document (minimum 100 characters)."
            )
        
        logger.info(f"Parsed document: {parsed.get('word_count', 0)} words, {len(sections)} sections")
        print(f"✅ Parsed document: {parsed.get('word_count', 0)} words, {len(sections)} sections\n")
    
        # 2. Extract Domains & Boundaries & APIs using Advanced NLP
        analyzer = get_analyzer()
        result = analyzer.analyze_requirements(
            requirement_text, 
            project_id, 
            filename,
            sections=sections
        )
        
        # 3. Cache results and raw text to project
        ans_file = get_analyses_file(project_id)
        with open(ans_file, "w", encoding="utf-8") as f:
            f.write(result.json())
        # Store raw text for re-analysis on clarification submission
        with open(get_text_file(project_id), "w", encoding="utf-8") as f:
            f.write(requirement_text)
        
        logger.info(f"Analysis completed successfully for project {project_id}")
        logger.info(f"Generated {len(result.microservices)} microservices with {len(result.dependencies)} dependencies")
        
        print(f"\n💾 Analysis saved to: {ans_file}")
        print(f"✅ Generated {len(result.microservices)} microservices")
        print(f"{'='*60}\n")
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/{project_id}", response_model=Optional[AnalysisResult])
def get_latest_analysis(project_id: str):
    """Retrieve the latest analysis for a project"""
    ans_file = get_analyses_file(project_id)
    if not os.path.exists(ans_file):
        # Return fallback default architecture for the demo/onboarding project
        if project_id == "project-onboarding":
            print(f"🎯 Generating default onboarding analysis...")
            default_req = (
                "# E-Commerce Platform Requirements\n\n"
                "Users can register accounts, login securely, view personalized dashboards, "
                "add products to shopping cart, and complete checkout with order placement. "
                "The order service processes orders, requests credit card charges from Stripe payment gateway, "
                "decrements stock quantities from our central inventory database, and triggers "
                "email notifications upon order completion. We need comprehensive analytical "
                "insights and transaction reports for business intelligence dashboards."
            )
            analyzer = get_analyzer()
            result = analyzer.analyze_requirements(default_req, project_id, "srs_default.txt")
            with open(ans_file, "w", encoding="utf-8") as f:
                f.write(result.json())
            return result
        raise HTTPException(status_code=404, detail="No analysis found for this project")

    with open(ans_file, "r", encoding="utf-8") as f:
        return json.load(f)

@router.put("/{project_id}", response_model=AnalysisResult)
def update_analysis(project_id: str, updated_result: AnalysisResult):
    """
    Saves customized architecture configurations updated directly on the diagram canvas by the user.
    """
    ans_file = get_analyses_file(project_id)
    with open(ans_file, "w", encoding="utf-8") as f:
        f.write(updated_result.json())
    return updated_result


# ============= Clarification Re-Analysis =============

@router.post("/{project_id}/clarify", response_model=AnalysisResult)
async def clarify_and_rebuild(project_id: str, body: ClarifyRequest):
    """
    Re-run analysis with the user's answers to clarification questions injected
    as additional context.  The original document text is loaded from cache;
    answers are appended so the LLM can produce a more accurate service breakdown.
    """
    text_file = get_text_file(project_id)
    ans_file  = get_analyses_file(project_id)

    if not os.path.exists(text_file):
        raise HTTPException(status_code=404, detail="Original document not found. Please re-upload.")

    with open(text_file, "r", encoding="utf-8") as f:
        requirement_text = f.read()

    # Load original analysis to reuse filename
    filename = "requirements.txt"
    if os.path.exists(ans_file):
        with open(ans_file, "r", encoding="utf-8") as f:
            cached = json.load(f)
        filename = cached.get("raw_filename", filename)

    answers_dicts = [{"question": a.question, "answer": a.answer} for a in body.answers]

    analyzer = get_analyzer()
    result = analyzer.analyze_requirements(
        requirement_text,
        project_id,
        filename,
        clarification_answers=answers_dicts,
    )

    # Overwrite cached analysis with the refined result
    with open(ans_file, "w", encoding="utf-8") as f:
        f.write(result.json())

    logger.info(f"Clarification re-analysis complete for project {project_id}")
    return result


# ============= Export Endpoints =============

@router.get("/{project_id}/export/markdown", response_class=PlainTextResponse)
def export_markdown(project_id: str):
    """Export architecture as Markdown documentation"""
    ans_file = get_analyses_file(project_id)
    if not os.path.exists(ans_file):
        raise HTTPException(status_code=404, detail="No analysis found for this project")
    
    with open(ans_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        analysis = AnalysisResult(**data)
    
    markdown = ArchitectureExporter.to_markdown(analysis)
    return PlainTextResponse(content=markdown, media_type="text/markdown")


@router.get("/{project_id}/export/mermaid", response_class=PlainTextResponse)
def export_mermaid(project_id: str):
    """Export architecture as Mermaid diagram code"""
    ans_file = get_analyses_file(project_id)
    if not os.path.exists(ans_file):
        raise HTTPException(status_code=404, detail="No analysis found for this project")
    
    with open(ans_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        analysis = AnalysisResult(**data)
    
    mermaid = ArchitectureExporter.to_mermaid(analysis)
    return PlainTextResponse(content=mermaid, media_type="text/plain")


@router.get("/{project_id}/export/plantuml", response_class=PlainTextResponse)
def export_plantuml(project_id: str):
    """Export architecture as PlantUML component diagram"""
    ans_file = get_analyses_file(project_id)
    if not os.path.exists(ans_file):
        raise HTTPException(status_code=404, detail="No analysis found for this project")
    
    with open(ans_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        analysis = AnalysisResult(**data)
    
    plantuml = ArchitectureExporter.to_plantuml(analysis)
    return PlainTextResponse(content=plantuml, media_type="text/plain")


@router.get("/{project_id}/export/json")
def export_json_schema(project_id: str):
    """Export architecture as structured JSON schema"""
    ans_file = get_analyses_file(project_id)
    if not os.path.exists(ans_file):
        raise HTTPException(status_code=404, detail="No analysis found for this project")
    
    with open(ans_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        analysis = AnalysisResult(**data)
    
    json_schema = ArchitectureExporter.to_json_schema(analysis)
    return JSONResponse(content=json_schema)
