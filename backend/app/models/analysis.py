from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DependencyInfo(BaseModel):
    source: str
    target: str
    type: str = "sync" # "sync", "async"
    description: str = ""

class ApiEndpoint(BaseModel):
    path: str
    method: str
    description: str
    request_payload: Optional[Dict[str, Any]] = None
    response_payload: Optional[Dict[str, Any]] = None

class MicroserviceSchema(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    database: str
    database_reasoning: str
    apis: List[ApiEndpoint] = []
    scaling_recommendations: List[str] = []

class MetricScores(BaseModel):
    scalability: int = Field(..., ge=0, le=100)
    coupling: int = Field(..., ge=0, le=100)
    maintainability: int = Field(..., ge=0, le=100)
    fault_isolation: int = Field(..., ge=0, le=100)

class AnalysisResult(BaseModel):
    project_id: str
    raw_filename: str
    raw_content_preview: str
    microservices: List[MicroserviceSchema] = []
    dependencies: List[DependencyInfo] = []
    metrics: MetricScores
    raw_feedback: Optional[str] = ""
