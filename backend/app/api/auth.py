from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()

class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=TokenResponse)
def register(user: UserRegister):
    if not user.email or "@" not in user.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
    return {
        "access_token": "mock-jwt-token-xyz-12345678",
        "token_type": "bearer",
        "user": {
            "name": user.name,
            "email": user.email,
            "role": "Solution Architect"
        }
    }

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    if credentials.email == "demo@archaitect.ai" and credentials.password == "password":
        return {
            "access_token": "demo-jwt-token-active",
            "token_type": "bearer",
            "user": {
                "name": "Demo Architect",
                "email": "demo@archaitect.ai",
                "role": "Solution Architect"
            }
        }
    # Bypass/always login for basic developer boilerplate convenience!
    return {
        "access_token": "bypass-jwt-token-active",
        "token_type": "bearer",
        "user": {
            "name": credentials.email.split("@")[0].capitalize(),
            "email": credentials.email,
            "role": "Backend Engineer"
        }
    }
