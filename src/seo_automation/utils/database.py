"""
Database models and utilities (basic setup for future phases)
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

from ..config.settings import settings

logger = structlog.get_logger(__name__)

Base = declarative_base()


class Blog(Base):
    """Blog registry table."""
    __tablename__ = "blogs"
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    domain = Column(String, nullable=False)
    domain_authority = Column(Integer)
    category = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BlogPost(Base):
    """Blog posts table."""
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True)
    blog_id = Column(Integer, nullable=False)  # Foreign key to blogs
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content_summary = Column(Text)
    author = Column(String)
    publish_date = Column(DateTime)
    analysis_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    """Generated comments table."""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False)  # Foreign key to blog_posts
    content = Column(Text, nullable=False)
    quality_score = Column(Float)
    status = Column(String, default="pending")
    generated_by = Column(String)  # Agent that generated it
    cost = Column(Float)  # Vertex AI cost
    created_at = Column(DateTime, default=datetime.utcnow)


class CostTracking(Base):
    """Vertex AI cost tracking table."""
    __tablename__ = "cost_tracking"
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    operation_type = Column(String, nullable=False)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Database connection and operations manager."""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        
        if settings.database_url:
            self.engine = create_engine(settings.database_url)
            self.session_maker = sessionmaker(bind=self.engine)
            logger.info("database_manager_initialized", url=settings.database_url)
        else:
            logger.warning("no_database_url_configured")
    
    def create_tables(self):
        """Create all tables."""
        if self.engine:
            Base.metadata.create_all(self.engine)
            logger.info("database_tables_created")
        else:
            logger.warning("cannot_create_tables_no_engine")
    
    def get_session(self):
        """Get database session."""
        if self.session_maker:
            return self.session_maker()
        return None


# Global database manager instance
db_manager = DatabaseManager()
