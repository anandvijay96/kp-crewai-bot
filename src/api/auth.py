"""
Authentication System
====================

JWT-based authentication and authorization for the CrewAI KP Bot API.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme
security = HTTPBearer()

# Optional HTTP Bearer scheme (for endpoints that work with or without auth)
optional_security = HTTPBearer(auto_error=False)

# ============================================================================
# Password Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

# ============================================================================
# JWT Token Utilities
# ============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: The data to encode in the token
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Refresh token creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create refresh token"
        )

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        token_type: The expected token type ("access" or "refresh")
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type. Expected: {token_type}, Got: {payload.get('type')}")
            raise credentials_exception
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            logger.warning("Token missing expiration")
            raise credentials_exception
        
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise credentials_exception

# ============================================================================
# User Management (Simplified for MVP)
# ============================================================================

# In-memory user store for MVP (replace with database in production)
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@kloudportal.com",
        "full_name": "System Administrator",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True,
        "is_admin": True,
        "created_at": datetime.utcnow(),
    },
    "demo": {
        "username": "demo",
        "email": "demo@kloudportal.com",
        "full_name": "Demo User",
        "hashed_password": get_password_hash("demo123"),
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.utcnow(),
    }
}

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user by username.
    
    Args:
        username: The username to look up
        
    Returns:
        dict or None: User data if found, None otherwise
    """
    return USERS_DB.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username
        password: The plain text password
        
    Returns:
        dict or None: User data if authenticated, None otherwise
    """
    user = get_user(username)
    if not user:
        logger.warning(f"User not found: {username}")
        return None
    
    if not user.get("is_active", False):
        logger.warning(f"User is inactive: {username}")
        return None
    
    if not verify_password(password, user["hashed_password"]):
        logger.warning(f"Invalid password for user: {username}")
        return None
    
    logger.info(f"User authenticated successfully: {username}")
    return user

def create_user(username: str, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new user.
    
    Args:
        username: The username
        email: The email address
        password: The plain text password
        full_name: Optional full name
        
    Returns:
        dict: The created user data
        
    Raises:
        HTTPException: If user already exists
    """
    if username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    user_data = {
        "username": username,
        "email": email,
        "full_name": full_name or username,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.utcnow(),
    }
    
    USERS_DB[username] = user_data
    logger.info(f"User created successfully: {username}")
    
    # Return user data without password hash
    user_response = user_data.copy()
    del user_response["hashed_password"]
    return user_response

# ============================================================================
# Authentication Dependencies
# ============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        dict: Current user data
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify the access token
        payload = verify_token(credentials.credentials, "access")
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = get_user(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Return user without sensitive data
        user_data = user.copy()
        del user_data["hashed_password"]
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get the current authenticated admin user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Current admin user data
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user

# ============================================================================
# Optional Authentication (for public endpoints)
# ============================================================================

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)) -> Optional[Dict[str, Any]]:
    """
    Get the current user if authenticated, None otherwise.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        dict or None: Current user data if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
