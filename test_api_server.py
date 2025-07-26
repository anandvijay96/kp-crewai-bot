#!/usr/bin/env python3
"""
Test API Server for Authentication Testing
==========================================

Standalone FastAPI server to test frontend-backend integration.
"""

import sys
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import uvicorn

# Import our authentication components
try:
    from src.api.auth.jwt_handler import JWTHandler
    from src.seo_automation.utils.database import db_manager
    print("✅ Successfully imported auth components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="KP Bot Auth Test API",
    description="Test API for frontend-backend authentication integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "user"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class RefreshRequest(BaseModel):
    refresh_token: str

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Mock user database (for testing purposes)
mock_users = {
    "test@example.com": {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "password_hash": JWTHandler.hash_password("password123"),
        "role": "user",
        "permissions": ["view_campaign", "create_comment"],
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    },
    "admin@example.com": {
        "id": 2,
        "email": "admin@example.com",
        "full_name": "Admin User",
        "password_hash": JWTHandler.hash_password("admin123"),
        "role": "admin",
        "permissions": ["view_campaign", "create_comment", "manage_users", "delete_campaign"],
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        payload = JWTHandler.verify_token(token, "access")
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # Find user in mock database
        user = None
        for mock_email, mock_user in mock_users.items():
            if mock_email == email and str(mock_user["id"]) == user_id:
                user = mock_user
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "KP Bot Auth Test API",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/login", response_model=ApiResponse)
async def login(request: LoginRequest):
    """User login endpoint."""
    try:
        logger.info(f"Login attempt for: {request.email}")
        
        # Find user
        user = mock_users.get(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not JWTHandler.verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        token_data = {
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "permissions": user["permissions"]
        }
        
        access_token = JWTHandler.create_access_token(token_data)
        refresh_token = JWTHandler.create_refresh_token({"sub": str(user["id"])})
        
        # Update last login
        mock_users[request.email]["last_login"] = datetime.now().isoformat()
        
        # Prepare user data (without password hash)
        user_data = {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "permissions": user["permissions"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "last_login": user["last_login"]
        }
        
        logger.info(f"Login successful for: {request.email}")
        
        return ApiResponse(
            success=True,
            message="Login successful",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 1800,  # 30 minutes
                "user": user_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/auth/register", response_model=ApiResponse)
async def register(request: RegisterRequest):
    """User registration endpoint."""
    try:
        logger.info(f"Registration attempt for: {request.email}")
        
        # Check if user already exists
        if request.email in mock_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = JWTHandler.hash_password(request.password)
        
        # Create new user
        new_user_id = len(mock_users) + 1
        new_user = {
            "id": new_user_id,
            "email": request.email,
            "full_name": request.full_name,
            "password_hash": password_hash,
            "role": request.role,
            "permissions": ["view_campaign", "create_comment"] if request.role == "user" else ["view_campaign", "create_comment", "manage_users"],
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        # Add to mock database
        mock_users[request.email] = new_user
        
        logger.info(f"Registration successful for: {request.email}")
        
        return ApiResponse(
            success=True,
            message="User registered successfully",
            data={
                "user_id": new_user_id,
                "email": request.email
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/auth/refresh", response_model=ApiResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token endpoint."""
    try:
        logger.info("Token refresh attempt")
        
        # Verify refresh token
        payload = JWTHandler.verify_token(request.refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        
        # Find user
        user = None
        for email, mock_user in mock_users.items():
            if str(mock_user["id"]) == user_id:
                user = mock_user
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "permissions": user["permissions"]
        }
        
        new_access_token = JWTHandler.create_access_token(token_data)
        
        logger.info(f"Token refresh successful for user ID: {user_id}")
        
        return ApiResponse(
            success=True,
            message="Token refreshed successfully",
            data={
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": 1800
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.get("/api/auth/me", response_model=ApiResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    try:
        user_data = {
            "id": current_user["id"],
            "email": current_user["email"],
            "full_name": current_user["full_name"],
            "role": current_user["role"],
            "permissions": current_user["permissions"],
            "is_active": current_user["is_active"],
            "created_at": current_user["created_at"],
            "last_login": current_user["last_login"]
        }
        
        return ApiResponse(
            success=True,
            message="User information retrieved successfully",
            data=user_data
        )
        
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/auth/validate", response_model=ApiResponse)
async def validate_token(current_user: dict = Depends(get_current_user)):
    """Validate current token."""
    return ApiResponse(
        success=True,
        message="Token is valid",
        data={"valid": True, "user_id": current_user["id"]}
    )

@app.post("/api/auth/logout", response_model=ApiResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout endpoint."""
    # In a real implementation, you might blacklist the token
    # For this test, we just return success
    logger.info(f"Logout for user: {current_user['email']}")
    return ApiResponse(
        success=True,
        message="Logout successful"
    )

@app.get("/api/test/protected")
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    """Test protected endpoint."""
    return {
        "message": "This is a protected endpoint",
        "user": current_user["email"],
        "role": current_user["role"],
        "permissions": current_user["permissions"]
    }

if __name__ == "__main__":
    print("🚀 Starting KP Bot Auth Test API Server...")
    print("📍 API will be available at: http://127.0.0.1:8000")
    print("📖 API docs at: http://127.0.0.1:8000/docs")
    print("🧪 Test users:")
    print("   - test@example.com / password123 (user)")
    print("   - admin@example.com / admin123 (admin)")
    
    uvicorn.run(
        "test_api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
