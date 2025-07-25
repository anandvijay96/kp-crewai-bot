# Phase 1: Foundation & Core Setup

**Duration**: 3-5 days  
**Status**: Ready to start  
**Prerequisites**: Python 3.10+, Google Cloud Account

## Overview
This phase establishes the foundation for our CrewAI-based SEO automation system. We'll set up the project structure, configure Vertex AI integration with cost optimization, and create the core utilities needed for all subsequent phases.

## Objectives
- [x] Set up CrewAI project structure
- [x] Configure Vertex AI with cost optimization
- [x] Implement basic database layer
- [x] Create core utilities and configuration
- [x] Establish logging and monitoring

---

## Step 1: Project Structure Setup

### 1.1 Create Directory Structure
```bash
# Create main project structure
mkdir -p {
  src/seo_automation/{agents,tasks,tools,utils,config},
  tests/{unit,integration},
  data/{input,output,logs},
  docs/phases,
  scripts
}
```

### 1.2 Initialize Python Environment
```bash
# Install uv if not already installed (as per your rule to use uv instead of pip)
# For Windows PowerShell:
irm https://astral.sh/uv/install.ps1 | iex

# Create virtual environment
uv venv
# Activate it (Windows)
.venv\Scripts\activate

# Install basic dependencies
uv add crewai[tools]==0.70.1
uv add langchain-google-vertexai==2.0.4
uv add google-cloud-aiplatform==1.70.0
uv add pydantic-settings==2.6.1
uv add python-dotenv==1.0.1
uv add structlog==24.4.0
uv add rich==13.9.2
uv add typer==0.13.1
```

### 1.3 Core Configuration Files

**pyproject.toml**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "seo-automation"
version = "0.1.0"
description = "KloudPortal SEO Blog Commenting Automation with CrewAI"
authors = [{name = "KloudPortal Team", email = "team@kloudportal.com"}]
requires-python = ">=3.10,<3.13"
dependencies = [
    "crewai[tools]==0.70.1",
    "langchain-google-vertexai==2.0.4",
    "google-cloud-aiplatform==1.70.0",
    "pydantic-settings==2.6.1",
    "python-dotenv==1.0.1",
    "structlog==24.4.0",
    "rich==13.9.2",
    "typer==0.13.1",
    "playwright==1.48.0",
    "beautifulsoup4==4.12.3",
    "psycopg2-binary==2.9.9",
    "sqlalchemy==2.0.36",
    "pandas==2.2.3",
    "openpyxl==3.1.5"
]

[project.optional-dependencies]
dev = [
    "pytest==8.3.3",
    "pytest-asyncio==0.24.0",
    "black==24.10.0",
    "ruff==0.7.4",
    "mypy==1.13.0"
]

[tool.ruff]
target-version = "py310"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "ARG", "SIM"]
ignore = ["E501", "W503", "E203"]

[tool.black]
line-length = 88
target-version = ['py310']
```

---

## Step 2: Environment Configuration

### 2.1 Environment Variables Setup

**.env.example**
```bash
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=./credentials/vertex-ai-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1

# CrewAI Configuration (not used directly but required)
OPENAI_API_KEY=dummy_key_not_used_but_required
OPENAI_API_BASE=https://us-central1-aiplatform.googleapis.com

# Database Configuration (for future phases)
DATABASE_URL=postgresql://user:password@localhost:5432/seo_automation

# Cost Management
DAILY_BUDGET_USD=15.0
COST_ALERT_THRESHOLD=0.8

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 2.2 Configuration Management

**src/seo_automation/config/settings.py**
```python
"""
Application configuration management
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Google Cloud Settings
    google_cloud_project: str = Field(..., description="Google Cloud Project ID")
    vertex_ai_location: str = Field(default="us-central1", description="Vertex AI region")
    google_application_credentials: str = Field(
        default="./credentials/vertex-ai-key.json",
        description="Path to service account key"
    )
    
    # Cost Management
    daily_budget_usd: float = Field(default=15.0, description="Daily budget in USD")
    cost_alert_threshold: float = Field(default=0.8, description="Alert when 80% of budget used")
    
    # Application Settings
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")
    
    # Database (for future phases)
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    
    # CrewAI Compatibility (required but not used)
    openai_api_key: str = Field(default="dummy_key_not_used_but_required")
    openai_api_base: str = Field(default="https://us-central1-aiplatform.googleapis.com")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
```

---

## Step 3: Vertex AI Integration with Cost Optimization

### 3.1 Vertex AI Manager

**src/seo_automation/utils/vertex_ai_manager.py**
```python
"""
Vertex AI model management with cost optimization
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, date
from langchain_google_vertexai import ChatVertexAI
import structlog

from ..config.settings import settings

logger = structlog.get_logger(__name__)


class VertexAIManager:
    """Manages Vertex AI models with cost optimization."""
    
    def __init__(self):
        self.project_id = settings.google_cloud_project
        self.location = settings.vertex_ai_location
        self.daily_budget = settings.daily_budget_usd
        
        # Daily usage tracking (in-memory for now)
        self.daily_usage = 0.0
        self.usage_date = date.today()
        
        # Model pricing per 1K tokens (as of 2024)
        self.model_costs = {
            "gemini-1.5-flash-001": {"input": 0.000125, "output": 0.000375},
            "gemini-1.5-pro-001": {"input": 0.00125, "output": 0.00375}
        }
        
        logger.info(
            "vertex_ai_manager_initialized",
            project_id=self.project_id,
            location=self.location,
            daily_budget=self.daily_budget
        )
    
    def get_flash_model(self, **kwargs) -> ChatVertexAI:
        """Get cost-effective Gemini Flash model."""
        default_params = {
            "model_name": "gemini-1.5-flash-001",
            "project": self.project_id,
            "location": self.location,
            "max_output_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40
        }
        default_params.update(kwargs)
        
        return ChatVertexAI(**default_params)
    
    def get_pro_model(self, **kwargs) -> ChatVertexAI:
        """Get high-capability Gemini Pro model."""
        default_params = {
            "model_name": "gemini-1.5-pro-001",
            "project": self.project_id,
            "location": self.location,
            "max_output_tokens": 2048,
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40
        }
        default_params.update(kwargs)
        
        return ChatVertexAI(**default_params)
    
    def should_use_pro_model(self, task_complexity: str = "routine") -> bool:
        """Determine if Pro model should be used based on budget and complexity."""
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        # Check budget constraints
        if self.daily_usage > self.daily_budget * settings.cost_alert_threshold:
            logger.warning(
                "approaching_daily_budget_limit",
                current_usage=self.daily_usage,
                budget=self.daily_budget,
                threshold=settings.cost_alert_threshold
            )
            return False
        
        # Define complex tasks that benefit from Pro model
        complex_tasks = {
            "creative_writing",
            "complex_analysis", 
            "multi_step_reasoning",
            "comment_generation",
            "quality_review"
        }
        
        return task_complexity in complex_tasks
    
    def estimate_cost(
        self, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Estimate cost for a model operation."""
        if model_name not in self.model_costs:
            logger.warning("unknown_model_for_cost_estimation", model=model_name)
            return 0.0
        
        costs = self.model_costs[model_name]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        total_cost = input_cost + output_cost
        
        logger.debug(
            "cost_estimated",
            model=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )
        
        return total_cost
    
    def track_usage(
        self, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int,
        operation_type: str = "generation"
    ) -> float:
        """Track API usage and return cost."""
        cost = self.estimate_cost(model_name, input_tokens, output_tokens)
        
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        self.daily_usage += cost
        
        logger.info(
            "vertex_ai_usage_tracked",
            model=model_name,
            operation_type=operation_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            daily_usage=self.daily_usage,
            daily_budget=self.daily_budget,
            usage_percentage=(self.daily_usage / self.daily_budget) * 100
        )
        
        # Alert if approaching budget
        if self.daily_usage > self.daily_budget * settings.cost_alert_threshold:
            logger.warning(
                "daily_budget_alert",
                current_usage=self.daily_usage,
                budget=self.daily_budget,
                percentage=(self.daily_usage / self.daily_budget) * 100
            )
        
        return cost
    
    def check_daily_budget(self) -> bool:
        """Check if we're within daily budget limits."""
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        return self.daily_usage < self.daily_budget
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Generate usage report."""
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        return {
            "date": self.usage_date.isoformat(),
            "daily_budget": self.daily_budget,
            "current_usage": self.daily_usage,
            "remaining_budget": max(0, self.daily_budget - self.daily_usage),
            "usage_percentage": (self.daily_usage / self.daily_budget) * 100,
            "budget_exceeded": self.daily_usage > self.daily_budget,
            "alert_threshold_reached": self.daily_usage > (self.daily_budget * settings.cost_alert_threshold),
            "available_models": list(self.model_costs.keys())
        }


# Global instance
vertex_ai_manager = VertexAIManager()
```

---

## Step 4: Logging and Monitoring

### 4.1 Structured Logging Setup

**src/seo_automation/utils/logging.py**
```python
"""
Structured logging configuration
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict
import structlog
from rich.logging import RichHandler
from rich.console import Console

from ..config.settings import settings


def setup_logging() -> None:
    """Configure structured logging with Rich output."""
    
    # Create logs directory
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            min_level=getattr(structlog, settings.log_level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(
            file=open(log_dir / "application.log", "a", encoding="utf-8")
        ),
        cache_logger_on_first_use=False,
    )
    
    # Set up rich handler for console output
    console = Console()
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=settings.is_development
    )
    
    # Configure Python's logging for libraries
    import logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler]
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Global logger for this module
logger = get_logger(__name__)
```

---

## Step 5: Basic Database Models (Preparation for Phase 4)

### 5.1 Database Models

**src/seo_automation/utils/database.py**
```python
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
```

---

## Step 6: CLI Interface Foundation

### 6.1 Main CLI Application

**src/seo_automation/main.py**
```python
"""
Main CLI application entry point
"""
import asyncio
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .config.settings import settings
from .utils.logging import setup_logging, get_logger
from .utils.vertex_ai_manager import vertex_ai_manager

# Setup logging first
setup_logging()
logger = get_logger(__name__)

app = typer.Typer(
    name="seo-automation",
    help="KloudPortal SEO Blog Commenting Automation with CrewAI",
    rich_markup_mode="rich"
)
console = Console()


@app.command()
def setup():
    """Initial setup and configuration validation."""
    rprint("[bold blue]🚀 KloudPortal SEO Automation Setup[/bold blue]")
    
    # Check environment configuration
    rprint("\n[yellow]📋 Configuration Check[/yellow]")
    
    config_table = Table(title="Configuration Status")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Status", style="bold")
    
    # Check Google Cloud credentials
    creds_path = Path(settings.google_application_credentials)
    creds_status = "✅ Found" if creds_path.exists() else "❌ Missing"
    config_table.add_row(
        "Google Cloud Credentials",
        str(creds_path),
        creds_status
    )
    
    # Check project ID
    project_status = "✅ Set" if settings.google_cloud_project else "❌ Missing"
    config_table.add_row(
        "Google Cloud Project",
        settings.google_cloud_project or "Not set",
        project_status
    )
    
    # Check other settings
    config_table.add_row("Vertex AI Location", settings.vertex_ai_location, "✅ Set")
    config_table.add_row("Daily Budget", f"${settings.daily_budget_usd}", "✅ Set")
    config_table.add_row("Environment", settings.environment, "✅ Set")
    config_table.add_row("Log Level", settings.log_level, "✅ Set")
    
    console.print(config_table)
    
    # Test Vertex AI connection
    rprint("\n[yellow]🧪 Testing Vertex AI Connection[/yellow]")
    try:
        flash_model = vertex_ai_manager.get_flash_model()
        rprint("✅ Vertex AI Flash model initialized successfully")
        
        if vertex_ai_manager.check_daily_budget():
            rprint("✅ Daily budget check passed")
        else:
            rprint("⚠️  Daily budget exceeded")
            
    except Exception as e:
        rprint(f"❌ Vertex AI connection failed: {e}")
        logger.error("vertex_ai_connection_test_failed", error=str(e))
    
    rprint("\n[green]✨ Setup check complete![/green]")


@app.command()
def cost_report():
    """Display current cost usage report."""
    rprint("[bold blue]💰 Cost Usage Report[/bold blue]")
    
    report = vertex_ai_manager.get_usage_report()
    
    cost_table = Table(title=f"Daily Cost Report - {report['date']}")
    cost_table.add_column("Metric", style="cyan")
    cost_table.add_column("Value", style="green")
    
    cost_table.add_row("Daily Budget", f"${report['daily_budget']:.2f}")
    cost_table.add_row("Current Usage", f"${report['current_usage']:.4f}")
    cost_table.add_row("Remaining Budget", f"${report['remaining_budget']:.4f}")
    cost_table.add_row("Usage Percentage", f"{report['usage_percentage']:.1f}%")
    
    # Status indicators
    if report['budget_exceeded']:
        cost_table.add_row("Status", "❌ Budget Exceeded", style="bold red")
    elif report['alert_threshold_reached']:
        cost_table.add_row("Status", "⚠️  Approaching Limit", style="bold yellow")
    else:
        cost_table.add_row("Status", "✅ Within Budget", style="bold green")
    
    console.print(cost_table)
    
    # Available models
    rprint(f"\n[dim]Available models: {', '.join(report['available_models'])}[/dim]")


@app.command()
def test_model(
    model_type: str = typer.Option("flash", help="Model type: flash or pro"),
    prompt: str = typer.Option("Hello, this is a test", help="Test prompt")
):
    """Test Vertex AI model with a simple prompt."""
    rprint(f"[bold blue]🧪 Testing {model_type} model[/bold blue]")
    
    try:
        if model_type == "flash":
            model = vertex_ai_manager.get_flash_model()
        elif model_type == "pro":
            model = vertex_ai_manager.get_pro_model()
        else:
            rprint("❌ Invalid model type. Use 'flash' or 'pro'")
            return
        
        rprint(f"[yellow]Prompt:[/yellow] {prompt}")
        rprint("[yellow]Generating response...[/yellow]")
        
        # This is synchronous for simplicity in CLI
        response = model.invoke(prompt)
        
        rprint(f"[green]Response:[/green] {response.content}")
        
        # Estimate cost (rough approximation)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(response.content.split()) * 1.3
        
        model_name = "gemini-1.5-flash-001" if model_type == "flash" else "gemini-1.5-pro-001"
        cost = vertex_ai_manager.track_usage(
            model_name, 
            int(input_tokens), 
            int(output_tokens),
            "test"
        )
        
        rprint(f"[dim]Estimated cost: ${cost:.6f}[/dim]")
        
    except Exception as e:
        rprint(f"❌ Model test failed: {e}")
        logger.error("model_test_failed", model_type=model_type, error=str(e))


@app.command()
def info():
    """Display system information."""
    rprint("[bold blue]ℹ️  System Information[/bold blue]")
    
    info_table = Table()
    info_table.add_column("Component", style="cyan")
    info_table.add_column("Version/Status", style="green")
    
    info_table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    info_table.add_row("Environment", settings.environment)
    info_table.add_row("Project Root", str(Path.cwd()))
    info_table.add_row("Logs Directory", "data/logs")
    info_table.add_row("Google Cloud Project", settings.google_cloud_project)
    info_table.add_row("Vertex AI Location", settings.vertex_ai_location)
    
    console.print(info_table)


if __name__ == "__main__":
    app()
```

---

## Testing Phase 1

### 7.1 Create Test Script

**tests/test_phase1.py**
```python
"""
Phase 1 testing script
"""
import pytest
from src.seo_automation.config.settings import settings
from src.seo_automation.utils.vertex_ai_manager import vertex_ai_manager
from src.seo_automation.utils.logging import get_logger

logger = get_logger(__name__)


def test_settings_loaded():
    """Test that settings are properly loaded."""
    assert settings.google_cloud_project is not None
    assert settings.vertex_ai_location is not None
    assert settings.daily_budget_usd > 0


def test_vertex_ai_manager_initialization():
    """Test Vertex AI manager initialization."""
    assert vertex_ai_manager.project_id is not None
    assert vertex_ai_manager.location is not None
    assert vertex_ai_manager.daily_budget > 0


def test_model_creation():
    """Test that models can be created."""
    flash_model = vertex_ai_manager.get_flash_model()
    pro_model = vertex_ai_manager.get_pro_model()
    
    assert flash_model is not None
    assert pro_model is not None


def test_cost_estimation():
    """Test cost estimation functionality."""
    cost = vertex_ai_manager.estimate_cost("gemini-1.5-flash-001", 100, 50)
    assert cost > 0
    assert isinstance(cost, float)


def test_budget_check():
    """Test budget checking functionality."""
    result = vertex_ai_manager.check_daily_budget()
    assert isinstance(result, bool)


def test_usage_report():
    """Test usage report generation."""
    report = vertex_ai_manager.get_usage_report()
    
    required_keys = [
        "date", "daily_budget", "current_usage", 
        "remaining_budget", "usage_percentage", 
        "budget_exceeded", "alert_threshold_reached"
    ]
    
    for key in required_keys:
        assert key in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Phase 1 Completion Checklist

### ✅ Setup Tasks
- [ ] Project structure created
- [ ] Virtual environment setup with uv
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Google Cloud credentials setup

### ✅ Core Components
- [ ] Settings management working
- [ ] Vertex AI manager implemented
- [ ] Cost tracking functional
- [ ] Logging system operational
- [ ] Database models defined
- [ ] CLI interface created

### ✅ Testing
- [ ] All tests pass
- [ ] CLI commands work
- [ ] Vertex AI connection successful
- [ ] Cost reporting functional

### ✅ Documentation
- [ ] Code properly documented
- [ ] Configuration examples provided
- [ ] Testing procedures documented

---

## Next Steps: Phase 2 Preparation

1. **Review Phase 1 deliverables** - Ensure all components work
2. **Test integration** - Run all CLI commands and verify functionality
3. **Cost baseline** - Establish baseline costs for simple operations
4. **Prepare for agents** - Review existing agent code from old project
5. **Start Phase 2** - Begin agent development

## Troubleshooting

### Common Issues
1. **Google Cloud Authentication**: Ensure service account key is in correct location
2. **Environment Variables**: Double-check .env file configuration
3. **Python Version**: Ensure Python 3.10+ is being used
4. **Virtual Environment**: Make sure virtual environment is activated

### Getting Help
- Check logs in `data/logs/application.log`
- Run `python -m src.seo_automation.main info` for system status
- Use `python -m src.seo_automation.main cost-report` to check usage

---

**Phase 1 Complete!** 🎉

Ready to proceed to Phase 2: Agent Development.
