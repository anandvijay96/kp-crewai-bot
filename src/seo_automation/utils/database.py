"""
Database models and utilities (basic setup for future phases)
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON, Enum, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class UserRole(enum.Enum):
    """User roles enumeration."""
    user = "user"
    admin = "admin"
    moderator = "moderator"


class User(Base):
    """User authentication table."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    permissions = Column(JSON)  # Store user-specific permissions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)


class Blog(Base):
    """Blog registry table."""
    __tablename__ = "blogs"
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    domain = Column(String, nullable=False)
    domain_authority = Column(Integer)
    category = Column(String)
    status = Column(String, default="active")
    analysis_metadata = Column(JSON)  # Store analysis results and other metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BlogPost(Base):
    """Blog posts table."""
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True)
    blog_id = Column(Integer, nullable=True)  # Foreign key to blogs (optional)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content_summary = Column(Text)
    author = Column(String)
    publication_date = Column(String)  # Store as string initially
    word_count = Column(Integer, default=0)
    has_comments = Column(Boolean, default=False)
    tags = Column(JSON)  # Store as JSON array
    comment_worthiness_score = Column(Integer, default=0)
    engagement_potential = Column(String, default='low')  # low, medium, high
    analysis_data = Column(JSON)
    analyzed_at = Column(DateTime)
    status = Column(String, default='discovered')  # discovered, analyzed, processed
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


class AgentExecution(Base):
    """Agent execution tracking table."""
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String, nullable=False)
    task_description = Column(Text, nullable=False)
    context_data = Column(JSON)
    model_name = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String, nullable=False)  # running, completed, failed
    result_data = Column(JSON)
    cost = Column(Float)
    tokens_used = Column(Integer)
    execution_time = Column(Float)  # seconds


class DatabaseManager:
    """Database connection and operations manager."""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self.connection_available = False
        
        if settings.database_url:
            try:
                self.engine = create_engine(settings.database_url)
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.session_maker = sessionmaker(bind=self.engine)
                self.connection_available = True
                logger.info(f"Database manager initialized with URL: {settings.database_url}")
            except Exception as e:
                logger.warning(f"Database connection failed: {str(e)}")
                self.engine = None
                self.session_maker = None
                self.connection_available = False
        else:
            logger.warning("No database URL configured")
    
    def create_tables(self):
        """Create all tables."""
        if self.engine:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        else:
            logger.warning("Cannot create tables - no database engine")
    
    def get_session(self):
        """Get database session."""
        if self.session_maker:
            return self.session_maker()
        return None

    def insert_blog(self, session, blog_data: Dict[str, Any]) -> Optional[Blog]:
        """Insert blog data into the database, or update if exists."""
        blog = session.query(Blog).filter_by(url=blog_data['url']).first()
        if not blog:
            blog = Blog(**blog_data)
            session.add(blog)
        else:
            for key, value in blog_data.items():
                setattr(blog, key, value)
        session.commit()
        return blog

    def insert_blog_post(self, session, post_data: Dict[str, Any]) -> Optional[BlogPost]:
        """Insert blog post data into the database, or update if exists."""
        post = session.query(BlogPost).filter_by(url=post_data['url']).first()
        if not post:
            post = BlogPost(**post_data)
            session.add(post)
        else:
            for key, value in post_data.items():
                setattr(post, key, value)
        session.commit()
        return post


# Global database manager instance
db_manager = DatabaseManager()
