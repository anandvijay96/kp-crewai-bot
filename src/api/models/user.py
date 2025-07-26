"""
User Models for Authentication System
=====================================

Pydantic models for user authentication, registration, and management.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    """User roles with different permission levels."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserPermission(str, Enum):
    """Specific permissions for fine-grained access control."""
    # Campaign permissions
    CREATE_CAMPAIGN = "create_campaign"
    VIEW_CAMPAIGN = "view_campaign"
    EDIT_CAMPAIGN = "edit_campaign"
    DELETE_CAMPAIGN = "delete_campaign"
    
    # Agent permissions
    RUN_AGENTS = "run_agents"
    VIEW_AGENT_LOGS = "view_agent_logs"
    MANAGE_AGENTS = "manage_agents"
    
    # Blog permissions
    VIEW_BLOGS = "view_blogs"
    RESEARCH_BLOGS = "research_blogs"
    VALIDATE_BLOGS = "validate_blogs"
    
    # Comment permissions
    GENERATE_COMMENTS = "generate_comments"
    APPROVE_COMMENTS = "approve_comments"
    DELETE_COMMENTS = "delete_comments"
    
    # System permissions
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_USERS = "manage_users"
    SYSTEM_SETTINGS = "system_settings"


# Default permissions for each role
ROLE_PERMISSIONS = {
    UserRole.USER: [
        UserPermission.VIEW_CAMPAIGN,
        UserPermission.CREATE_CAMPAIGN,
        UserPermission.EDIT_CAMPAIGN,
        UserPermission.VIEW_BLOGS,
        UserPermission.RESEARCH_BLOGS,
        UserPermission.GENERATE_COMMENTS,
        UserPermission.VIEW_ANALYTICS,
        UserPermission.RUN_AGENTS,
    ],
    UserRole.MODERATOR: [
        # All user permissions plus
        UserPermission.APPROVE_COMMENTS,
        UserPermission.DELETE_COMMENTS,
        UserPermission.VIEW_AGENT_LOGS,
        UserPermission.VALIDATE_BLOGS,
    ],
    UserRole.ADMIN: [
        # All permissions
        *[p for p in UserPermission]
    ]
}


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.USER
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model with password."""
    password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "secure_password123",
                "role": "user"
            }
        }


class UserUpdate(BaseModel):
    """User update model with optional fields."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[UserPermission]] = None


class UserResponse(UserBase):
    """User response model (without password)."""
    id: int
    permissions: List[UserPermission]
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "permissions": ["view_campaign", "create_campaign"],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
                "last_login": "2024-01-02T10:30:00Z"
            }
        }


class UserLogin(BaseModel):
    """User login credentials."""
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secure_password123"
            }
        }


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordReset(BaseModel):
    """Password reset request."""
    email: EmailStr
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "old_password123",
                "new_password": "new_secure_password456"
            }
        }
