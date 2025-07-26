"""
Authentication Routes - Updated Implementation
==============================================

FastAPI routes for user authentication using JWT and UserService.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from ..models.api_models import ApiResponse
from ..models.user import (
    UserLogin, UserCreate, UserResponse, Token, TokenRefresh, 
    PasswordReset, PasswordChange
)
from ..auth.jwt_handler import JWTHandler, get_current_user, get_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES
from ..services.user_service import UserService
from typing import Dict, Any, List

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=ApiResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        user = UserService.create_user(user_data)
        return ApiResponse(
            success=True,
            message="User registered successfully",
            data={
                "user": user,
                "message": "Please login with your credentials"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=ApiResponse)
async def login(credentials: UserLogin):
    """User login with email and password."""
    user = UserService.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
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
    
    return ApiResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "permissions": user["permissions"]
            }
        }
    )

@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = JWTHandler.verify_token(token_data.refresh_token, "refresh")
        user_id = int(payload.get("sub"))
        
        # Get current user data
        user = UserService.get_user_by_id(user_id)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "permissions": user["permissions"]
        }
        
        access_token = JWTHandler.create_access_token(token_data)
        
        return ApiResponse(
            success=True,
            message="Token refreshed successfully",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    user = UserService.get_user_by_id(current_user["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return ApiResponse(
        success=True,
        message="User information retrieved",
        data={"user": user}
    )

@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password."""
    success = UserService.change_password(
        current_user["user_id"],
        password_data.current_password,
        password_data.new_password
    )
    
    return ApiResponse(
        success=success,
        message="Password changed successfully" if success else "Failed to change password"
    )

@router.post("/logout", response_model=ApiResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """User logout (client should discard token)."""
    # In a JWT system, logout is typically handled client-side by discarding the token
    # For more security, you could implement a token blacklist system
    return ApiResponse(
        success=True,
        message="Logged out successfully",
        data={"message": "Please discard your access token"}
    )

# Admin-only endpoints
@router.get("/users", response_model=ApiResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """List all users (admin only)."""
    users = UserService.list_users(skip=skip, limit=limit)
    
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(users)} users",
        data={
            "users": users,
            "total": len(users),
            "skip": skip,
            "limit": limit
        }
    )

@router.get("/users/{user_id}", response_model=ApiResponse)
async def get_user(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Get user by ID (admin only)."""
    user = UserService.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return ApiResponse(
        success=True,
        message="User retrieved successfully",
        data={"user": user}
    )

@router.delete("/users/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_admin_user)
):
    """Delete user (admin only)."""
    # Prevent self-deletion
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = UserService.delete_user(user_id)
    
    return ApiResponse(
        success=success,
        message="User deleted successfully" if success else "Failed to delete user"
    )

@router.get("/health")
async def auth_health_check():
    """Health check endpoint for authentication system."""
    return {
        "status": "healthy",
        "service": "JWT Authentication System",
        "features": [
            "JWT Token Authentication",
            "Password Hashing (bcrypt)",
            "User Registration",
            "Token Refresh",
            "Role-based Access Control",
            "Permission-based Authorization",
            "Database Integration"
        ],
        "endpoints": {
            "register": "/api/auth/register",
            "login": "/api/auth/login",
            "refresh": "/api/auth/refresh",
            "me": "/api/auth/me",
            "logout": "/api/auth/logout",
            "users": "/api/auth/users (admin)",
            "change-password": "/api/auth/change-password"
        }
    }
