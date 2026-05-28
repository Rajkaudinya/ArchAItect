from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, projects, analysis

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Transforms SRS/BRD requirements into scalable microservice topologies instantly.",
    version="1.0.0"
)

# Robust CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow access from Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route Registrations
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["Project Management"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["AI Architecture Engine"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ArchAItect Architecture Intelligence Engine API",
        "documentation": "/docs"
    }
