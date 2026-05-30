from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DependencyInfo(BaseModel):
    source: str
    target: str
    type: str = "sync"  # "sync", "async"
    description: str = ""

class ApiEndpoint(BaseModel):
    path: str
    method: str
    description: str
    inferred: bool = False  # True when not traceable to a document action verb
    request_payload: Optional[Dict[str, Any]] = None
    response_payload: Optional[Dict[str, Any]] = None

class MicroserviceSchema(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    database: str
    database_reasoning: str
    boundary_justification: str = ""
    inferred: bool = False          # True when < 2 FR-IDs justify this service
    justified_fr_ids: List[str] = []  # FR-IDs that directly justify this boundary
    apis: List[ApiEndpoint] = []
    scaling_recommendations: List[str] = []
    metadata: Optional[Dict[str, Any]] = {}

class MetricScores(BaseModel):
    scalability: int = Field(..., ge=0, le=100)
    coupling: int = Field(..., ge=0, le=100)
    maintainability: int = Field(..., ge=0, le=100)
    fault_isolation: int = Field(..., ge=0, le=100)
    cohesion: int = Field(default=70, ge=0, le=100)

class MetricFactor(BaseModel):
    """Individual factor contributing to a metric score"""
    name: str
    value: Any  # Could be int, float, string, dict, etc.
    impact: str  # "+15 points", "-10 penalty", "Base factor"
    explanation: str  # Human-readable reasoning
    statistical_basis: str  # Research citation or industry benchmark

class MetricBreakdown(BaseModel):
    """Complete statistical breakdown of how a metric was calculated"""
    metric_name: str  # "Coupling", "Scalability", etc.
    final_score: int  # 0-100
    rating: str  # "Excellent", "Good", "Moderate", "Needs Improvement"
    formula: str  # Mathematical formula used
    factors: List[MetricFactor] = []
    recommendation: str  # Actionable advice
    statistical_context: str  # Research citations, industry benchmarks
    raw_data: Dict[str, Any] = Field(default_factory=dict)  # Raw calculation data

class AnalysisResult(BaseModel):
    project_id: str
    raw_filename: str
    raw_content_preview: str
    microservices: List[MicroserviceSchema] = []
    dependencies: List[DependencyInfo] = []
    metrics: MetricScores
    metrics_breakdown: Optional[Dict[str, MetricBreakdown]] = None  # NEW: Statistical breakdowns
    raw_feedback: Optional[str] = ""
    analysis_metadata: Optional[Dict[str, Any]] = {}
    
    # Aliases for backward compatibility
    @property
    def filename(self):
        return self.raw_filename
    
    @property
    def content_preview(self):
        return self.raw_content_preview
