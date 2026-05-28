import uvicorn
import os

if __name__ == "__main__":
    print("🚀 Booting up ArchAItect Core AI Engine Server...")
    print("🌍 Swagger UI available at: http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
