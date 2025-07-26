"""
User Service for Authentication Operations
==========================================

Handles user management, authentication, and authorization logic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from ..models.user import UserCreate, UserUpdate, UserRole, ROLE_PERMISSIONS
from ..auth.jwt_handler import JWTHandler
from ...seo_automation.utils.database import User, UserRole as DbUserRole, db_manager
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    def get_db_session() -> Session:
        """Get database session."""
        if not db_manager.connection_available:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )
        return db_manager.get_session()
    
    @staticmethod
    def create_user(user_data: UserCreate) -> Dict[str, Any]:
        """Create a new user."""
        db = UserService.get_db_session()
        
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password
            hashed_password = JWTHandler.hash_password(user_data.password)
            
            # Get default permissions for role
            default_permissions = ROLE_PERMISSIONS.get(user_data.role, [])
            
            # Map API UserRole to Database UserRole
            db_role = getattr(DbUserRole, user_data.role.value)
            
            # Create user
            db_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                role=db_role,
                permissions=[p.value for p in default_permissions],
                is_active=user_data.is_active
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Created new user: {user_data.email}")
            
            return {
                "id": db_user.id,
                "email": db_user.email,
                "full_name": db_user.full_name,
                "role": db_user.role.value,
                "permissions": db_user.permissions,
                "is_active": db_user.is_active,
                "created_at": db_user.created_at
            }
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        finally:
            db.close()
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password."""
        db = UserService.get_db_session()
        
        try:
            user = db.query(User).filter(User.email == email).first()
            
            if not user or not user.is_active:
                return None
            
            if not JWTHandler.verify_password(password, user.hashed_password):
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "permissions": user.permissions or [],
                "is_active": user.is_active,
                "last_login": user.last_login
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        db = UserService.get_db_session()
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "permissions": user.permissions or [],
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login
            }
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        db = UserService.get_db_session()
        
        try:
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "permissions": user.permissions or [],
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login
            }
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_user(user_id: int, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
        """Update user information."""
        db = UserService.get_db_session()
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields if provided
            if user_data.email is not None:
                # Check if email is already taken by another user
                existing_user = db.query(User).filter(
                    User.email == user_data.email,
                    User.id != user_id
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already taken"
                    )
                user.email = user_data.email
            
            if user_data.full_name is not None:
                user.full_name = user_data.full_name
            
            if user_data.role is not None:
                user.role = user_data.role
                # Update permissions based on new role
                if user_data.permissions is None:
                    default_permissions = ROLE_PERMISSIONS.get(user_data.role, [])
                    user.permissions = [p.value for p in default_permissions]
            
            if user_data.permissions is not None:
                user.permissions = [p.value for p in user_data.permissions]
            
            if user_data.is_active is not None:
                user.is_active = user_data.is_active
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "permissions": user.permissions or [],
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        finally:
            db.close()
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete user (soft delete by setting is_active to False)."""
        db = UserService.get_db_session()
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Deleted user: {user.email}")
            return True
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
        finally:
            db.close()
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        db = UserService.get_db_session()
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify current password
            if not JWTHandler.verify_password(current_password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Hash and set new password
            user.hashed_password = JWTHandler.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error changing password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )
        finally:
            db.close()
    
    @staticmethod
    def list_users(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List all users with pagination."""
        db = UserService.get_db_session()
        
        try:
            users = db.query(User).offset(skip).limit(limit).all()
            
            return [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "permissions": user.permissions or [],
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "last_login": user.last_login
                }
                for user in users
            ]
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list users"
            )
        finally:
            db.close()
