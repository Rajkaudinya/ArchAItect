from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = ""

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectInDB(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime
    version: int = 1

    class Config:
        from_attributes = True
