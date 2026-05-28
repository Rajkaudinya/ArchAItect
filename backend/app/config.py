import os

if os.getenv("USE_PYDANTIC_SETTINGS"):
    from pydantic_settings import BaseSettings
else:
    BaseSettings = object

class Settings:
    PROJECT_NAME: str = "ArchAItect Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-key-for-archaitect-development-123456")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # In-memory database bypass for immediate local running
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

settings = Settings()

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)
