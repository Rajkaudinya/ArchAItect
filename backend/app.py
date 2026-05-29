"""
ArchAItect Backend Application Entry Point
Starts the FastAPI server with proper configuration
"""
import uvicorn
import os
from app.config import settings

def main():
    """Start the ArchAItect Core AI Engine Server"""
    print("=" * 70)
    print("[STARTUP] Starting ArchAItect Core AI Engine Server...")
    print("=" * 70)
    print(f"[SERVER] Server Address: http://{settings.HOST}:{settings.PORT}")
    print(f"[DOCS] API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"[CONFIG] Groq API Key: {'Configured' if settings.GROQ_API_KEY else 'Not Set'}")
    print(f"[DATA] Data Directory: {settings.DATA_DIR}")
    print("=" * 70)
    print()
    
    # Ensure data directory exists
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
