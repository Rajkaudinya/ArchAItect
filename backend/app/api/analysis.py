import os
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.config import settings
from app.services.parser import DocumentParser
from app.services.analyzer import RequirementAnalyzer
from app.models.analysis import AnalysisResult

router = APIRouter()

def get_analyses_file(project_id: str) -> str:
    return os.path.join(settings.DATA_DIR, f"analysis_{project_id}.json")

@router.post("/upload", response_model=AnalysisResult)
async def upload_requirement_document(
    project_id: str = Form(...),
    file: UploadFile = File(...)
):
    # Verify file content
    contents = await file.read()
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
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
        except Exception:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")
            
    if not parsed.get("success", False) and "text" not in parsed:
        raise HTTPException(status_code=500, detail=parsed.get("error", "Error parsing file"))
        
    requirement_text = parsed["text"]
    
    # 2. Extract Domains & Boundaries & APIs
    result = RequirementAnalyzer.analyze_requirements(requirement_text, project_id, filename)
    
    # 3. Cache results to project
    ans_file = get_analyses_file(project_id)
    with open(ans_file, "w") as f:
        f.write(result.json())
        
    return result

@router.get("/{project_id}", response_model=Optional[AnalysisResult])
def get_latest_analysis(project_id: str):
    ans_file = get_analyses_file(project_id)
    if not os.path.exists(ans_file):
        # Return fallback default architecture for the demo/onboarding project
        if project_id == "project-onboarding":
            default_req = (
                "Users can login, view user dashboard, add products to cart, and checkout orders. "
                "The order service then requests credit card charges from stripe gateway, decrements stock quantities "
                "from our central inventory databases, and triggers email notifications upon completion. "
                "We need analytical insights for transaction reports."
            )
            result = RequirementAnalyzer.analyze_requirements(default_req, project_id, "srs_default.txt")
            with open(ans_file, "w") as f:
                f.write(result.json())
            return result
        raise HTTPException(status_code=404, detail="No analysis found for this project")
        
    with open(ans_file, "r") as f:
        return json.load(f)

@router.put("/{project_id}", response_model=AnalysisResult)
def update_analysis(project_id: str, updated_result: AnalysisResult):
    """
    Saves customized architecture configurations updated directly on the diagram canvas by the user.
    """
    ans_file = get_analyses_file(project_id)
    with open(ans_file, "w") as f:
        f.write(updated_result.json())
    return updated_result
