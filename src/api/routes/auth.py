"""
Authentication Routes
====================

FastAPI routes for user authentication and authorization.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
from typing import Dict, Any
import logging

from ..models import UserLogin, UserRegister, TokenResponse, BaseResponse
from ..auth import (
    authenticate_user,
    create_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    security
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.
    
    Args:
        user_data: User login credentials
        
    Returns:
        TokenResponse: Access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info(f"Login attempt for user: {user_data.username}")
    
    # Authenticate user
    user = authenticate_user(user_data.username, user_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": user["username"]}
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data=token_data)
    
    # Prepare user info (without sensitive data)
    user_info = {
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "is_admin": user.get("is_admin", False),
        "created_at": user["created_at"].isoformat()
    }
    
    logger.info(f"User logged in successfully: {user_data.username}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info=user_info,
        message="Login successful"
    )

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister) -> TokenResponse:
    """
    Register a new user and return JWT tokens.
    
    Args:
        user_data: User registration data
        
    Returns:
        TokenResponse: Access token and user information
        
    Raises:
        HTTPException: If registration fails
    """
    logger.info(f"Registration attempt for user: {user_data.username}")
    
    try:
        # Create new user
        user = create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": user["username"]}
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data=token_data)
        
        # Prepare user info
        user_info = {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_admin": user.get("is_admin", False),
            "created_at": user["created_at"].isoformat()
        }
        
        logger.info(f"User registered successfully: {user_data.username}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info=user_info,
            message="Registration successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for user {user_data.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        credentials: HTTP authorization credentials with refresh token
        
    Returns:
        TokenResponse: New access token and user information
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        # Verify refresh token
        payload = verify_token(credentials.credentials, "refresh")
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user data
        from ..auth import get_user
        user = get_user(username)
        if not user or not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": username}
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        # Prepare user info
        user_info = {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_admin": user.get("is_admin", False),
            "created_at": user["created_at"].isoformat()
        }
        
        logger.info(f"Token refreshed successfully for user: {username}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info=user_info,
            message="Token refreshed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=BaseResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)) -> BaseResponse:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        BaseResponse: User information
    """
    logger.info(f"User info requested for: {current_user['username']}")
    
    return BaseResponse(
        message="User information retrieved successfully",
        **{"user": current_user}
    )

@router.post("/logout", response_model=BaseResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> BaseResponse:
    """
    Logout user (client-side token removal).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        BaseResponse: Logout confirmation
        
    Note:
        This endpoint primarily serves as a confirmation for client-side token removal.
        In a production environment, you might implement token blacklisting.
    """
    logger.info(f"User logged out: {current_user['username']}")
    
    return BaseResponse(
        message="Logout successful. Please remove the token from client storage."
    )

# ============================================================================
# User Management Endpoints (Admin only)
# ============================================================================

@router.get("/users", response_model=BaseResponse)
async def list_users(current_user: Dict[str, Any] = Depends(get_current_user)) -> BaseResponse:
    """
    List all users (admin only).
    
    Args:
        current_user: Current authenticated user (must be admin)
        
    Returns:
        BaseResponse: List of users
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    from ..auth import USERS_DB
    
    # Return users without sensitive data
    users = []
    for username, user_data in USERS_DB.items():
        user_info = {
            "username": user_data["username"],
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "is_active": user_data["is_active"],
            "is_admin": user_data.get("is_admin", False),
            "created_at": user_data["created_at"].isoformat()
        }
        users.append(user_info)
    
    logger.info(f"User list requested by admin: {current_user['username']}")
    
    return BaseResponse(
        message="Users retrieved successfully",
        **{"users": users, "total": len(users)}
    )

# ============================================================================
# Health Check for Auth System
# ============================================================================

@router.get("/health")
async def auth_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for authentication system.
    
    Returns:
        dict: Authentication system health status
    """
    return {
        "status": "healthy",
        "service": "Authentication System",
        "features": [
            "JWT Token Authentication",
            "Password Hashing (bcrypt)",
            "User Registration",
            "Token Refresh",
            "Admin Role Management"
        ],
        "endpoints": {
            "login": "/api/auth/login",
            "register": "/api/auth/register",
            "refresh": "/api/auth/refresh",
            "me": "/api/auth/me",
            "logout": "/api/auth/logout"
        }
    }
