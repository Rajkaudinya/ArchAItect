import os
from dotenv import load_dotenv

# The shared .env lives at the repository root, one level above backend/.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path=ENV_FILE, override=False)

if os.getenv("USE_PYDANTIC_SETTINGS"):
    from pydantic_settings import BaseSettings
else:
    BaseSettings = object

class Settings:
    PROJECT_NAME: str = "ArchAItect Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-key-for-archaitect-development-123456")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEY_3: str = os.getenv("GROQ_API_KEY_3", "")
    COMPETITOR_GROQ_MODEL: str = os.getenv("COMPETITOR_GROQ_MODEL", "groq/compound-mini")
    COMPETITOR_GROQ_VERSION: str = os.getenv("COMPETITOR_GROQ_VERSION", "2025-07-23")
    COMPETITOR_GROQ_MAX_RETRY_SECONDS: int = int(os.getenv("COMPETITOR_GROQ_MAX_RETRY_SECONDS", "8"))
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Performance Settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB default
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))  # 30 seconds
    
    # Rate Limiting (requests per minute)
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "False").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # In-memory database bypass for immediate local running
    DATA_DIR: str = os.path.join(BACKEND_DIR, "data")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "")

settings = Settings()

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)
