
# KloudPortal SEO Blog Commenting Automation – Implementation Guide

This comprehensive implementation guide provides step-by-step instructions for building the hybrid n8n + CrewAI platform with Vertex AI integration. Use this as your development blueprint for Windsurf IDE or Gemini CLI.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Project Structure](#project-structure)
3. [n8n Configuration](#n8n-configuration)
4. [CrewAI Implementation](#crewai-implementation)
5. [Vertex AI Integration](#vertex-ai-integration)
6. [Database Setup](#database-setup)
7. [Core Implementation Files](#core-implementation-files)
8. [Testing \& Validation](#testing--validation)
9. [Deployment Scripts](#deployment-scripts)

## Environment Setup

### Prerequisites Installation

```bash
# System Requirements Check
node --version  # Should be >= 18.x
python --version  # Should be >= 3.10, < 3.13
docker --version
git --version

# Install uv package manager (faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# Windows PowerShell: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install CrewAI CLI
uv tool install crewai

# Verify installation
crewai --version
```


### Google Cloud Setup

```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
source ~/.bashrc

# Authenticate and configure
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

# Create service account for Vertex AI
gcloud iam service-accounts create seo-automation-sa \
    --display-name="SEO Automation Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:seo-automation-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:seo-automation-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Create and download service account key
gcloud iam service-accounts keys create credentials/vertex-ai-key.json \
    --iam-account=seo-automation-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```


### n8n Setup Options

**Option 1: Docker Setup (Recommended)**

```bash
# Create n8n data directory
mkdir -p ~/.n8n-data

# Create docker-compose.yml for n8n
cat > docker-compose.n8n.yml << 'EOF'
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - ~/.n8n-data:/home/node/.n8n
      - ./credentials:/home/node/.n8n/credentials
EOF

# Start n8n
docker-compose -f docker-compose.n8n.yml up -d

# Access n8n at http://localhost:5678
echo "n8n is running at http://localhost:5678"
echo "Username: admin, Password: admin123"
```

**Option 2: npm Installation**

```bash
# Global installation
npm install n8n -g

# Start n8n
n8n start --tunnel
```


## Project Structure

### Create Main Project Directory

```bash
# Create project structure
mkdir -p seo-automation/{n8n-workflows,crewai-agents,database,scripts,docs,config}
cd seo-automation

# Initialize directory structure
mkdir -p {
  crewai-agents/{src/seo_automation/{tools,config,agents,tasks},tests},
  n8n-workflows/{blog-discovery,content-analysis,comment-generation,monitoring},
  database/{migrations,schemas,seeds},
  scripts/{deployment,monitoring,cost-tracking},
  config/{environment,templates},
  credentials,
  logs
}

# Create initial files
touch {
  .env,
  .env.example,
  .gitignore,
  README.md,
  requirements.txt,
  docker-compose.yml
}
```


### Project Tree Structure

```
seo-automation/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── docker-compose.yml
├── credentials/
│   └── vertex-ai-key.json
├── config/
│   ├── environment/
│   └── templates/
├── n8n-workflows/
│   ├── blog-discovery/
│   ├── content-analysis/
│   ├── comment-generation/
│   └── monitoring/
├── crewai-agents/
│   ├── pyproject.toml
│   ├── src/
│   │   └── seo_automation/
│   │       ├── main.py
│   │       ├── crew.py
│   │       ├── agents/
│   │       ├── tasks/
│   │       ├── tools/
│   │       └── config/
│   └── tests/
├── database/
│   ├── migrations/
│   ├── schemas/
│   └── seeds/
└── scripts/
    ├── deployment/
    ├── monitoring/
    └── cost-tracking/
```


## Core Implementation Files

### 1. Environment Configuration

**.env.example**

```bash
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=./credentials/vertex-ai-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1

# CrewAI Configuration
OPENAI_API_BASE=https://us-central1-aiplatform.googleapis.com
OPENAI_API_KEY=dummy_key_not_used_but_required

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/seo_automation
REDIS_URL=redis://localhost:6379/0

# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook
N8N_API_KEY=your_n8n_api_key

# Cost Management
DAILY_BUDGET_USD=15.0
COST_ALERT_THRESHOLD=0.8

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
```

**.gitignore**

```gitignore
# Environment files
.env
.env.local

# Credentials
credentials/
*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# n8n data
.n8n/
n8n-data/

# OS
.DS_Store
Thumbs.db
```


### 2. Requirements and Dependencies

**requirements.txt**

```txt
# CrewAI and AI frameworks
crewai[tools]==0.70.1
langchain-google-vertexai==2.0.4
google-cloud-aiplatform==1.70.0

# Web scraping and automation
playwright==1.48.0
beautifulsoup4==4.12.3
requests==2.32.3
selenium==4.26.1

# Database and caching
psycopg2-binary==2.9.9
redis==5.1.1
sqlalchemy==2.0.36
alembic==1.13.3

# API and web framework
fastapi==0.115.4
uvicorn[standard]==0.32.0
pydantic==2.9.2

# Utilities
python-dotenv==1.0.1
pydantic-settings==2.6.1
tenacity==9.0.0
rich==13.9.2
typer==0.13.1

# Monitoring and logging
prometheus-client==0.21.0
structlog==24.4.0

# Testing
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

**crewai-agents/pyproject.toml**

```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "seo-automation"
version = "0.1.0"
description = "KloudPortal SEO Blog Commenting Automation"
authors = ["KloudPortal Team <team@kloudportal.com>"]

[tool.poetry.dependencies]
python = ">=3.10,<3.13"
crewai = {extras = ["tools"], version = "^0.70.1"}
langchain-google-vertexai = "^2.0.4"
google-cloud-aiplatform = "^1.70.0"
playwright = "^1.48.0"
beautifulsoup4 = "^4.12.3"
requests = "^2.32.3"
psycopg2-binary = "^2.9.9"
redis = "^5.1.1"
sqlalchemy = "^2.0.36"
fastapi = "^0.115.4"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
python-dotenv = "^1.0.1"
pydantic-settings = "^2.6.1"
tenacity = "^9.0.0"
rich = "^13.9.2"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.3"
pytest-asyncio = "^0.24.0"
black = "^24.10.0"
ruff = "^0.7.4"
mypy = "^1.13.0"

[tool.ruff]
target-version = "py310"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "ARG", "SIM"]
ignore = ["E501", "W503", "E203"]

[tool.black]
line-length = 88
target-version = ['py310']

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```


### 3. CrewAI Agent Implementation

**crewai-agents/src/seo_automation/main.py**

```python
#!/usr/bin/env python3
"""
KloudPortal SEO Automation - Main Entry Point
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from crew import SEOAutomationCrew
from utils.cost_monitor import CostMonitor
from utils.database import DatabaseManager
from utils.logger import get_logger

# Load environment variables
load_dotenv()

app = typer.Typer(rich_markup_mode="rich")
console = Console()
logger = get_logger(__name__)


@app.command()
def discover_blogs(
    limit: int = typer.Option(10, help="Number of blogs to discover"),
    category: str = typer.Option("marketing", help="Blog category to search"),
    min_da: int = typer.Option(50, help="Minimum Domain Authority")
):
    """Discover new authoritative blogs for commenting."""
    console.print(f"[bold blue]Discovering {limit} blogs in {category} category...[/bold blue]")
    
    crew = SEOAutomationCrew()
    
    inputs = {
        "category": category,
        "limit": limit,
        "min_domain_authority": min_da
    }
    
    result = crew.blog_discovery_crew().kickoff(inputs=inputs)
    
    console.print("[bold green]Blog discovery completed![/bold green]")
    console.print(result)


@app.command()
def analyze_content(
    blog_url: str = typer.Argument(help="Blog URL to analyze"),
    post_limit: int = typer.Option(5, help="Number of recent posts to analyze")
):
    """Analyze blog content for commenting opportunities."""
    console.print(f"[bold blue]Analyzing content from: {blog_url}[/bold blue]")
    
    crew = SEOAutomationCrew()
    
    inputs = {
        "blog_url": blog_url,
        "post_limit": post_limit
    }
    
    result = crew.content_analysis_crew().kickoff(inputs=inputs)
    
    console.print("[bold green]Content analysis completed![/bold green]")
    console.print(result)


@app.command()
def generate_comments(
    post_url: str = typer.Argument(help="Blog post URL"),
    style: str = typer.Option("professional", help="Comment style: professional, casual, technical")
):
    """Generate comments for a specific blog post."""
    console.print(f"[bold blue]Generating comments for: {post_url}[/bold blue]")
    
    crew = SEOAutomationCrew()
    
    inputs = {
        "post_url": post_url,
        "comment_style": style,
        "company_context": "KloudPortal - Cloud migration and DevOps automation platform"
    }
    
    result = crew.comment_generation_crew().kickoff(inputs=inputs)
    
    console.print("[bold green]Comment generation completed![/bold green]")
    console.print(result)


@app.command()
def full_pipeline(
    category: str = typer.Option("marketing", help="Blog category"),
    daily_limit: int = typer.Option(20, help="Daily comment limit")
):
    """Run the full blog commenting pipeline."""
    console.print("[bold blue]Starting full SEO automation pipeline...[/bold blue]")
    
    cost_monitor = CostMonitor()
    
    # Check daily budget
    if not asyncio.run(cost_monitor.check_daily_budget()):
        console.print("[bold red]Daily budget exceeded! Stopping execution.[/bold red]")
        return
    
    crew = SEOAutomationCrew()
    
    inputs = {
        "category": category,
        "daily_limit": daily_limit,
        "min_domain_authority": 50
    }
    
    result = crew.full_automation_crew().kickoff(inputs=inputs)
    
    console.print("[bold green]Full pipeline completed![/bold green]")
    console.print(result)


@app.command()
def cost_report():
    """Generate cost usage report."""
    cost_monitor = CostMonitor()
    report = asyncio.run(cost_monitor.generate_daily_report())
    
    table = Table(title="Daily Cost Report")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in report.items():
        table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(table)


@app.command()
def setup_database():
    """Initialize database tables."""
    console.print("[bold blue]Setting up database...[/bold blue]")
    
    db_manager = DatabaseManager()
    asyncio.run(db_manager.create_tables())
    
    console.print("[bold green]Database setup completed![/bold green]")


if __name__ == "__main__":
    app()
```

**crewai-agents/src/seo_automation/crew.py**

```python
"""
SEO Automation CrewAI Implementation
"""
import os
from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process
from langchain_google_vertexai import ChatVertexAI

from agents.blog_researcher import BlogResearcherAgent
from agents.content_analyzer import ContentAnalyzerAgent
from agents.comment_writer import CommentWriterAgent
from agents.quality_reviewer import QualityReviewerAgent
from tasks.discovery_tasks import DiscoveryTasks
from tasks.analysis_tasks import AnalysisTasks
from tasks.generation_tasks import GenerationTasks
from utils.vertex_ai_manager import VertexAIManager


class SEOAutomationCrew:
    """Main crew orchestrator for SEO automation tasks."""
    
    def __init__(self):
        self.vertex_ai = VertexAIManager()
        self._setup_agents()
        self._setup_tasks()
    
    def _setup_agents(self):
        """Initialize all agents with Vertex AI models."""
        # Get cost-optimized models
        flash_model = self.vertex_ai.get_flash_model()
        pro_model = self.vertex_ai.get_pro_model()
        
        # Initialize agents
        self.blog_researcher = BlogResearcherAgent(llm=flash_model)
        self.content_analyzer = ContentAnalyzerAgent(llm=flash_model)
        self.comment_writer = CommentWriterAgent(llm=pro_model)  # Use Pro for creativity
        self.quality_reviewer = QualityReviewerAgent(llm=flash_model)
    
    def _setup_tasks(self):
        """Initialize task managers."""
        self.discovery_tasks = DiscoveryTasks()
        self.analysis_tasks = AnalysisTasks()
        self.generation_tasks = GenerationTasks()
    
    def blog_discovery_crew(self) -> Crew:
        """Create crew for blog discovery tasks."""
        tasks = [
            self.discovery_tasks.search_authoritative_blogs(agent=self.blog_researcher),
            self.discovery_tasks.validate_blog_authority(agent=self.blog_researcher),
            self.discovery_tasks.extract_commenting_guidelines(agent=self.content_analyzer)
        ]
        
        return Crew(
            agents=[self.blog_researcher, self.content_analyzer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def content_analysis_crew(self) -> Crew:
        """Create crew for content analysis tasks."""
        tasks = [
            self.analysis_tasks.scrape_blog_content(agent=self.content_analyzer),
            self.analysis_tasks.analyze_post_context(agent=self.content_analyzer),
            self.analysis_tasks.identify_commenting_opportunities(agent=self.content_analyzer)
        ]
        
        return Crew(
            agents=[self.content_analyzer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def comment_generation_crew(self) -> Crew:
        """Create crew for comment generation and review."""
        tasks = [
            self.generation_tasks.generate_comment_draft(agent=self.comment_writer),
            self.generation_tasks.review_comment_quality(agent=self.quality_reviewer),
            self.generation_tasks.optimize_cta_placement(agent=self.comment_writer)
        ]
        
        return Crew(
            agents=[self.comment_writer, self.quality_reviewer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def full_automation_crew(self) -> Crew:
        """Create comprehensive crew for full automation pipeline."""
        tasks = [
            # Discovery phase
            self.discovery_tasks.search_authoritative_blogs(agent=self.blog_researcher),
            self.discovery_tasks.validate_blog_authority(agent=self.blog_researcher),
            
            # Analysis phase
            self.analysis_tasks.scrape_blog_content(agent=self.content_analyzer),
            self.analysis_tasks.analyze_post_context(agent=self.content_analyzer),
            self.analysis_tasks.identify_commenting_opportunities(agent=self.content_analyzer),
            
            # Generation phase
            self.generation_tasks.generate_comment_draft(agent=self.comment_writer),
            self.generation_tasks.review_comment_quality(agent=self.quality_reviewer),
            self.generation_tasks.optimize_cta_placement(agent=self.comment_writer)
        ]
        
        return Crew(
            agents=[
                self.blog_researcher,
                self.content_analyzer,
                self.comment_writer,
                self.quality_reviewer
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            max_execution_time=3600  # 1 hour timeout
        )
```


### 4. Agent Implementations

**crewai-agents/src/seo_automation/agents/blog_researcher.py**

```python
"""
Blog Researcher Agent - Specializes in discovering authoritative blogs
"""
from crewai import Agent
from langchain_google_vertexai import ChatVertexAI
from tools.web_search_tool import WebSearchTool
from tools.domain_authority_tool import DomainAuthorityTool


class BlogResearcherAgent:
    """Agent responsible for discovering and validating authoritative blogs."""
    
    @staticmethod
    def create_agent(llm: ChatVertexAI) -> Agent:
        return Agent(
            role='Blog Discovery Specialist',
            goal='''
                Discover high-authority marketing and technology blogs with Domain Authority > 50
                that have active commenting communities and align with KloudPortal's services.
                Focus on blogs in cloud computing, DevOps, digital transformation, and enterprise software.
            ''',
            backstory='''
                You are an expert digital marketing researcher with 10+ years of experience
                in identifying high-value blog networks. You have deep knowledge of the
                SaaS and cloud computing ecosystem, understanding which blogs drive
                meaningful traffic and engagement. Your expertise includes:
                
                - Identifying authoritative voices in enterprise technology
                - Understanding commenting cultures across different platforms
                - Recognizing opportunities for valuable thought leadership contributions
                - Evaluating blog quality beyond just metrics
            ''',
            tools=[
                WebSearchTool(),
                DomainAuthorityTool()
            ],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_execution_time=300
        )


def BlogResearcherAgent(llm: ChatVertexAI) -> Agent:
    """Factory function to create Blog Researcher Agent."""
    return BlogResearcherAgent.create_agent(llm)
```

**crewai-agents/src/seo_automation/agents/content_analyzer.py**

```python
"""
Content Analyzer Agent - Specializes in understanding blog content and context
"""
from crewai import Agent
from langchain_google_vertexai import ChatVertexAI
from tools.content_scraper_tool import ContentScraperTool
from tools.nlp_analysis_tool import NLPAnalysisTool
from tools.keyword_extractor_tool import KeywordExtractorTool


class ContentAnalyzerAgent:
    """Agent responsible for analyzing blog content and identifying opportunities."""
    
    @staticmethod
    def create_agent(llm: ChatVertexAI) -> Agent:
        return Agent(
            role='Content Analysis Expert',
            goal='''
                Analyze blog posts to deeply understand context, themes, and audience intent.
                Identify the best commenting opportunities that provide genuine value while
                supporting KloudPortal's SEO and brand awareness objectives.
            ''',
            backstory='''
                You are a seasoned content strategist and NLP specialist who excels at
                understanding the nuances of technical blog content. Your expertise includes:
                
                - Identifying key themes and subtopics in technical articles
                - Understanding author intent and audience pain points
                - Recognizing opportunities for meaningful value-add contributions
                - Analyzing commenting patterns and community engagement styles
                - Extracting actionable insights from complex technical content
                
                You have a deep understanding of cloud computing, DevOps, and enterprise
                software topics, allowing you to identify where KloudPortal's expertise
                can add genuine value to discussions.
            ''',
            tools=[
                ContentScraperTool(),
                NLPAnalysisTool(),
                KeywordExtractorTool()
            ],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_execution_time=300
        )


def ContentAnalyzerAgent(llm: ChatVertexAI) -> Agent:
    """Factory function to create Content Analyzer Agent."""
    return ContentAnalyzerAgent.create_agent(llm)
```

**crewai-agents/src/seo_automation/agents/comment_writer.py**

```python
"""
Comment Writer Agent - Specializes in generating high-quality, contextual comments
"""
from crewai import Agent
from langchain_google_vertexai import ChatVertexAI
from tools.comment_generator_tool import CommentGeneratorTool
from tools.cta_optimizer_tool import CTAOptimizerTool


class CommentWriterAgent:
    """Agent responsible for generating high-quality, contextual comments."""
    
    @staticmethod
    def create_agent(llm: ChatVertexAI) -> Agent:
        return Agent(
            role='Technical Comment Specialist',
            goal='''
                Generate thoughtful, valuable comments that demonstrate KloudPortal's
                expertise while providing genuine value to the blog's audience.
                Each comment should feel natural, reference specific points from the article,
                and include a subtle but relevant mention of how KloudPortal can help.
            ''',
            backstory='''
                You are a technical content writer and thought leader with deep expertise
                in cloud computing, DevOps, and enterprise software solutions. Your background includes:
                
                - 8+ years writing for technical audiences in enterprise software
                - Deep understanding of cloud migration challenges and solutions
                - Experience with DevOps automation and CI/CD pipeline optimization
                - Proven track record of creating engaging, value-driven content
                - Expertise in balancing promotional content with genuine helpfulness
                
                You understand that the best comments spark meaningful discussions while
                positioning KloudPortal as a knowledgeable and helpful industry participant.
                You never sound salesy or spam-like - instead, you contribute genuine insights
                that happen to showcase KloudPortal's capabilities.
            ''',
            tools=[
                CommentGeneratorTool(),
                CTAOptimizerTool()
            ],
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_execution_time=180
        )


def CommentWriterAgent(llm: ChatVertexAI) -> Agent:
    """Factory function to create Comment Writer Agent."""
    return CommentWriterAgent.create_agent(llm)
```


### 5. Vertex AI Integration

**crewai-agents/src/seo_automation/utils/vertex_ai_manager.py**

```python
"""
Vertex AI Model Management and Cost Optimization
"""
import os
import asyncio
from typing import Dict, Any, Optional
from langchain_google_vertexai import ChatVertexAI
import structlog

logger = structlog.get_logger()


class VertexAIManager:
    """Manages Vertex AI model selection and cost optimization."""
    
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.daily_budget = float(os.getenv("DAILY_BUDGET_USD", "15.0"))
        self.current_usage = 0.0
        
        # Model pricing (per 1K tokens)
        self.model_costs = {
            "gemini-1.5-flash-001": {"input": 0.000125, "output": 0.000375},
            "gemini-1.5-pro-001": {"input": 0.00125, "output": 0.00375}
        }
    
    def get_flash_model(self) -> ChatVertexAI:
        """Get cost-effective Gemini Flash model for routine tasks."""
        return ChatVertexAI(
            model_name="gemini-1.5-flash-001",
            project=self.project_id,
            location=self.location,
            max_output_tokens=1024,
            temperature=0.7,
            top_p=0.8,
            top_k=40
        )
    
    def get_pro_model(self) -> ChatVertexAI:
        """Get high-capability Gemini Pro model for complex tasks."""
        return ChatVertexAI(
            model_name="gemini-1.5-pro-001",
            project=self.project_id,
            location=self.location,
            max_output_tokens=2048,
            temperature=0.8,
            top_p=0.9,
            top_k=40
        )
    
    def should_use_pro_model(self, task_complexity: str, estimated_tokens: int = 1000) -> bool:
        """Determine if Pro model should be used based on budget and complexity."""
        if self.current_usage > self.daily_budget * 0.8:
            logger.warning("Approaching daily budget limit, using Flash model only")
            return False
        
        complex_tasks = [
            "creative_writing",
            "complex_analysis",
            "multi_step_reasoning",
            "comment_generation"
        ]
        
        return task_complexity in complex_tasks
    
    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a model operation."""
        if model_name not in self.model_costs:
            return 0.0
        
        costs = self.model_costs[model_name]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def track_usage(self, model_name: str, input_tokens: int, output_tokens: int):
        """Track API usage for cost monitoring."""
        cost = self.estimate_cost(model_name, input_tokens, output_tokens)
        self.current_usage += cost
        
        logger.info(
            "vertex_ai_usage_tracked",
            model=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            daily_usage=self.current_usage
        )
    
    async def check_daily_budget(self) -> bool:
        """Check if we're within daily budget limits."""
        return self.current_usage < self.daily_budget
    
    async def get_usage_report(self) -> Dict[str, Any]:
        """Generate usage report for monitoring."""
        return {
            "daily_budget": self.daily_budget,
            "current_usage": self.current_usage,
            "remaining_budget": self.daily_budget - self.current_usage,
            "usage_percentage": (self.current_usage / self.daily_budget) * 100,
            "models_used": list(self.model_costs.keys())
        }


class CostOptimizedVertexAI:
    """Wrapper for cost-optimized Vertex AI usage."""
    
    def __init__(self, manager: VertexAIManager):
        self.manager = manager
    
    async def generate_with_fallback(
        self,
        prompt: str,
        task_complexity: str = "routine",
        max_tokens: int = 1024
    ) -> str:
        """Generate content with automatic model selection and fallback."""
        
        # Check budget first
        if not await self.manager.check_daily_budget():
            raise Exception("Daily budget exceeded")
        
        # Select model based on complexity and budget
        if self.manager.should_use_pro_model(task_complexity):
            model = self.manager.get_pro_model()
            model_name = "gemini-1.5-pro-001"
        else:
            model = self.manager.get_flash_model()
            model_name = "gemini-1.5-flash-001"
        
        try:
            # Generate response
            response = await model.ainvoke(prompt)
            
            # Track usage (approximate token counting)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response.content.split()) * 1.3
            
            self.manager.track_usage(model_name, int(input_tokens), int(output_tokens))
            
            return response.content
            
        except Exception as e:
            logger.error("vertex_ai_generation_failed", error=str(e), model=model_name)
            
            # Fallback to Flash model if Pro fails
            if model_name == "gemini-1.5-pro-001":
                logger.info("Falling back to Flash model")
                flash_model = self.manager.get_flash_model()
                response = await flash_model.ainvoke(prompt)
                
                input_tokens = len(prompt.split()) * 1.3
                output_tokens = len(response.content.split()) * 1.3
                
                self.manager.track_usage("gemini-1.5-flash-001", int(input_tokens), int(output_tokens))
                
                return response.content
            
            raise e
```


### 6. Database Implementation

**database/schemas/create_tables.sql**

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Blog registry with enhanced metadata
CREATE TABLE blogs (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    domain_authority INT,
    page_authority INT,
    category TEXT,
    platform_type TEXT,
    auth_required BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'active',
    discovery_agent_id TEXT,
    commenting_guidelines JSONB,
    submission_success_rate DECIMAL(3,2) DEFAULT 0.0,
    last_crawled TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Blog posts
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    blog_id INT REFERENCES blogs(id) ON DELETE CASCADE,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content_summary TEXT,
    full_content TEXT,
    keywords TEXT[],
    publish_date DATE,
    author TEXT,
    comment_count INT DEFAULT 0,
    last_checked TIMESTAMPTZ DEFAULT NOW(),
    comment_status TEXT DEFAULT 'open',
    analysis_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent execution tracking
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    execution_id UUID DEFAULT uuid_generate_v4(),
    crew_name TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    task_name TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    vertex_ai_usage JSONB,
    execution_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Enhanced comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES blog_posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    cta_used TEXT,
    template_id INT,
    submission_status TEXT DEFAULT 'pending',
    approval_status TEXT DEFAULT 'pending_review',
    generating_agent_id TEXT,
    review_agent_id TEXT,
    quality_score DECIMAL(3,2),
    submission_attempts INT DEFAULT 0,
    vertex_ai_generation_cost DECIMAL(8,6),
    performance_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ
);

-- Vertex AI cost tracking
CREATE TABLE vertex_ai_usage (
    id SERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    input_tokens INT,
    output_tokens INT,
    estimated_cost DECIMAL(10,6),
    agent_execution_id INT REFERENCES agent_executions(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comment templates for A/B testing
CREATE TABLE comment_templates (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    template_content TEXT NOT NULL,
    cta_type TEXT,
    success_rate DECIMAL(3,2) DEFAULT 0.0,
    usage_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance tracking
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    comment_id INT REFERENCES comments(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL, -- 'click', 'impression', 'conversion'
    metric_value DECIMAL(10,2),
    tracked_at TIMESTAMPTZ DEFAULT NOW(),
    source TEXT
);

-- Indexes for performance
CREATE INDEX idx_blogs_domain ON blogs(domain);
CREATE INDEX idx_blogs_status ON blogs(status);
CREATE INDEX idx_blogs_da ON blogs(domain_authority);
CREATE INDEX idx_blog_posts_blog_id ON blog_posts(blog_id);
CREATE INDEX idx_blog_posts_publish_date ON blog_posts(publish_date);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_status ON comments(submission_status);
CREATE INDEX idx_comments_created_at ON comments(created_at);
CREATE INDEX idx_agent_executions_crew ON agent_executions(crew_name);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_vertex_ai_usage_created_at ON vertex_ai_usage(created_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for blogs table
CREATE TRIGGER update_blogs_updated_at 
    BEFORE UPDATE ON blogs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

**crewai-agents/src/seo_automation/utils/database.py**

```python
"""
Database utilities and connection management
"""
import os
import asyncio
from typing import Dict, List, Any, Optional
import asyncpg
import structlog
from contextlib import asynccontextmanager

logger = structlog.get_logger()


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
    
    async def create_pool(self):
        """Create database connection pool."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            logger.info("Database connection pool created")
    
    async def close_pool(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool."""
        if not self.pool:
            await self.create_pool()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def create_tables(self):
        """Create database tables from schema file."""
        schema_file = os.path.join(
            os.path.dirname(__file__), 
            "../../database/schemas/create_tables.sql"
        )
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        async with self.get_connection() as conn:
            await conn.execute(schema_sql)
            logger.info("Database tables created successfully")
    
    async def insert_blog(self, blog_data: Dict[str, Any]) -> int:
        """Insert new blog record."""
        query = """
            INSERT INTO blogs (url, domain, domain_authority, page_authority, 
                             category, platform_type, discovery_agent_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                blog_data['url'],
                blog_data['domain'],
                blog_data.get('domain_authority'),
                blog_data.get('page_authority'),
                blog_data.get('category'),
                blog_data.get('platform_type'),
                blog_data.get('discovery_agent_id')
            )
            return row['id']
    
    async def insert_blog_post(self, post_data: Dict[str, Any]) -> int:
        """Insert new blog post record."""
        query = """
            INSERT INTO blog_posts (blog_id, url, title, content_summary, 
                                  keywords, publish_date, author, analysis_data)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                post_data['blog_id'],
                post_data['url'],
                post_data['title'],
                post_data.get('content_summary'),
                post_data.get('keywords', []),
                post_data.get('publish_date'),
                post_data.get('author'),
                post_data.get('analysis_data', {})
            )
            return row['id']
    
    async def insert_comment(self, comment_data: Dict[str, Any]) -> int:
        """Insert new comment record."""
        query = """
            INSERT INTO comments (post_id, content, cta_used, generating_agent_id,
                                quality_score, vertex_ai_generation_cost)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                comment_data['post_id'],
                comment_data['content'],
                comment_data.get('cta_used'),
                comment_data.get('generating_agent_id'),
                comment_data.get('quality_score'),
                comment_data.get('vertex_ai_generation_cost')
            )
            return row['id']
    
    async def track_agent_execution(self, execution_data: Dict[str, Any]) -> int:
        """Track agent execution for monitoring."""
        query = """
            INSERT INTO agent_executions (crew_name, agent_name, task_name,
                                        input_data, status)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                query,
                execution_data['crew_name'],
                execution_data['agent_name'],
                execution_data['task_name'],
                execution_data.get('input_data', {}),
                execution_data.get('status', 'running')
            )
            return row['id']
    
    async def update_agent_execution(self, execution_id: int, update_data: Dict[str, Any]):
        """Update agent execution status and results."""
        query = """
            UPDATE agent_executions 
            SET status = $2, output_data = $3, execution_time_ms = $4,
                completed_at = NOW()
            WHERE id = $1
        """
        
        async with self.get_connection() as conn:
            await conn.execute(
                query,
                execution_id,
                update_data.get('status'),
                update_data.get('output_data', {}),
                update_data.get('execution_time_ms')
            )
    
    async def track_vertex_ai_usage(self, usage_data: Dict[str, Any]):
        """Track Vertex AI API usage for cost monitoring."""
        query = """
            INSERT INTO vertex_ai_usage (model_name, operation_type, input_tokens,
                                       output_tokens, estimated_cost, agent_execution_id)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        async with self.get_connection() as conn:
            await conn.execute(
                query,
                usage_data['model_name'],
                usage_data['operation_type'],
                usage_data['input_tokens'],
                usage_data['output_tokens'],
                usage_data['estimated_cost'],
                usage_data.get('agent_execution_id')
            )
    
    async def get_daily_cost_usage(self) -> float:
        """Get total daily cost usage."""
        query = """
            SELECT COALESCE(SUM(estimated_cost), 0) as total_cost
            FROM vertex_ai_usage
            WHERE created_at >= CURRENT_DATE
        """
        
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query)
            return float(row['total_cost'])
    
    async def get_pending_comments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending comments for review."""
        query = """
            SELECT c.*, bp.title as post_title, bp.url as post_url
            FROM comments c
            JOIN blog_posts bp ON c.post_id = bp.id
            WHERE c.approval_status = 'pending_review'
            ORDER BY c.created_at ASC
            LIMIT $1
        """
        
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, limit)
            return [dict(row) for row in rows]
```


### 7. n8n Workflow Templates

**n8n-workflows/blog-discovery/master-discovery-workflow.json**

```json
{
  "name": "Blog Discovery Master Workflow",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "hoursInterval": 6
            }
          ]
        }
      },
      "name": "Schedule Every 6 Hours",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [
        240,
        300
      ]
    },
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "blog-discovery-webhook",
        "responseMode": "onReceived",
        "options": {}
      },
      "name": "Blog Discovery Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [
        460,
        300
      ],
      "webhookId": "blog-discovery-trigger"
    },
    {
      "parameters": {
        "requestMethod": "POST",
        "url": "http://localhost:8001/api/crews/blog-discovery/start",
        "jsonParameters": true,
        "parameterData": {
          "category": "{{ $json.category || 'marketing' }}",
          "limit": "{{ $json.limit || 10 }}",
          "min_domain_authority": "{{ $json.min_da || 50 }}"
        },
        "options": {
          "timeout": 300000
        }
      },
      "name": "Trigger Blog Discovery Crew",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [
        680,
        300
      ]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.status }}",
              "operation": "equal",
              "value2": "success"
            }
          ]
        }
      },
      "name": "Check Success",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        900,
        300
      ]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "INSERT INTO blogs (url, domain, domain_authority, category, discovery_agent_id, status) VALUES ({{ $json.blogs }})",
        "options": {}
      },
      "name": "Store Discovered Blogs",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 1,
      "position": [
        1120,
        200
      ]
    },
    {
      "parameters": {
        "requestMethod": "POST",
        "url": "http://localhost:8001/api/crews/content-analysis/start",
        "jsonParameters": true,
        "parameterData": {
          "blog_urls": "={{ $json.blogs.map(blog => blog.url) }}"
        }
      },
      "name": "Trigger Content Analysis",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [
        1340,
        200
      ]
    },
    {
      "parameters": {
        "message": "Blog discovery failed: {{ $json.error }}",
        "options": {
          "includePreviousMessages": true
        }
      },
      "name": "Log Error",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 1,
      "position": [
        1120,
        400
      ]
    }
  ],
  "connections": {
    "Schedule Every 6 Hours": {
      "main": [
        [
          {
            "node": "Trigger Blog Discovery Crew",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Blog Discovery Webhook": {
      "main": [
        [
          {
            "node": "Trigger Blog Discovery Crew",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Trigger Blog Discovery Crew": {
      "main": [
        [
          {
            "node": "Check Success",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Success": {
      "main": [
        [
          {
            "node": "Store Discovered Blogs",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Log Error",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Store Discovered Blogs": {
      "main": [
        [
          {
            "node": "Trigger Content Analysis",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {},
  "id": "blog-discovery-master"
}
```


### 8. Docker Compose Setup

**docker-compose.yml**

```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    container_name: seo-postgres
    environment:
      POSTGRES_DB: seo_automation
      POSTGRES_USER: seo_user
      POSTGRES_PASSWORD: seo_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schemas:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U seo_user -d seo_automation"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis for caching
  redis:
    image: redis:7-alpine
    container_name: seo-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # n8n workflow automation
  n8n:
    image: n8nio/n8n:latest
    container_name: seo-n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=America/New_York
      - N8N_LOG_LEVEL=info
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n-workflows:/home/node/.n8n/workflows
      - ./credentials:/home/node/.n8n/credentials
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # CrewAI API Server
  crewai-api:
    build:
      context: ./crewai-agents
      dockerfile: Dockerfile
    container_name: seo-crewai-api
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/vertex-ai-key.json
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION}
      - DATABASE_URL=postgresql://seo_user:seo_password@postgres:5432/seo_automation
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./credentials:/app/credentials
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: seo-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: seo-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  postgres_data:
  redis_data:
  n8n_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    name: seo-automation-network
```


### 9. Deployment Scripts

**scripts/deployment/setup.sh**

```bash
#!/bin/bash

# KloudPortal SEO Automation - Setup Script
set -e

echo "🚀 Setting up KloudPortal SEO Automation Platform"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if required commands exist
    commands=("docker" "docker-compose" "python3" "node" "npm" "gcloud")
    
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd is not installed or not in PATH"
            exit 1
        fi
    done
    
    # Check Python version
    python_version=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
    if [[ $(echo "$python_version >= 3.10" | bc -l) -eq 0 ]]; then
        print_error "Python 3.10+ is required, found $python_version"
        exit 1
    fi
    
    # Check Node version
    node_version=$(node --version | grep -oE '[0-9]+')
    if [[ $node_version -lt 18 ]]; then
        print_error "Node.js 18+ is required, found version $node_version"
        exit 1
    fi
    
    print_status "✅ All prerequisites met"
}

# Setup Google Cloud authentication
setup_gcloud() {
    print_status "Setting up Google Cloud authentication..."
    
    if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
        print_error "GOOGLE_CLOUD_PROJECT environment variable not set"
        exit 1
    fi
    
    # Check if already authenticated
    if gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q "@"; then
        print_status "✅ Already authenticated with Google Cloud"
    else
        print_warning "Please authenticate with Google Cloud"
        gcloud auth login
    fi
    
    # Set project
    gcloud config set project $GOOGLE_CLOUD_PROJECT
    
    # Enable required APIs
    print_status "Enabling required Google Cloud APIs..."
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable storage.googleapis.com
    
    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe seo-automation-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com &> /dev/null; then
        print_status "Creating service account..."
        gcloud iam service-accounts create seo-automation-sa \
            --display-name="SEO Automation Service Account"
        
        # Grant permissions
        gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
            --member="serviceAccount:seo-automation-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
            --role="roles/aiplatform.user"
    fi
    
    # Create credentials directory and download key
    mkdir -p credentials
    if [ ! -f "credentials/vertex-ai-key.json" ]; then
        print_status "Downloading service account key..."
        gcloud iam service-accounts keys create credentials/vertex-ai-key.json \
            --iam-account=seo-automation-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com
    fi
    
    print_status "✅ Google Cloud setup complete"
}

# Setup Python environment
setup_python() {
    print_status "Setting up Python environment..."
    
    # Install uv if not present
    if ! command -v uv &> /dev/null; then
        print_status "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc
    fi
    
    # Install CrewAI CLI
    if ! command -v crewai &> /dev/null; then
        print_status "Installing CrewAI CLI..."
        uv tool install crewai
    fi
    
    # Create virtual environment and install dependencies
    cd crewai-agents
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    print_status "Installing Python dependencies..."
    pip install -r ../requirements.txt
    
    cd ..
    print_status "✅ Python environment setup complete"
}

# Setup Docker services
setup_docker() {
    print_status "Setting up Docker services..."
    
    # Create necessary directories
    mkdir -p {logs,config/prometheus,config/grafana/{dashboards,datasources}}
    
    # Create Prometheus config
    cat > config/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'crewai-api'
    static_configs:
      - targets: ['crewai-api:8001']
    metrics_path: '/metrics'
EOF
    
    # Start Docker services
    print_status "Starting Docker services..."
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    print_status "Waiting for database to be ready..."
    until docker-compose exec postgres pg_isready -U seo_user -d seo_automation; do
        sleep 2
    done
    
    print_status "✅ Docker services running"
}

# Initialize database
setup_database() {
    print_status "Initializing database..."
    
    # Run database migrations
    cd crewai-agents
    source venv/bin/activate
    python -c "
import asyncio
from src.seo_automation.utils.database import DatabaseManager

async def setup_db():
    db = DatabaseManager()
    await db.create_tables()
    print('Database tables created successfully')

asyncio.run(setup_db())
"
    cd ..
    
    print_status "✅ Database initialized"
}

# Start n8n
setup_n8n() {
    print_status "Starting n8n..."
    
    docker-compose up -d n8n
    
    # Wait for n8n to be ready
    print_status "Waiting for n8n to be ready..."
    until curl -f http://localhost:5678/healthz &> /dev/null; do
        sleep 2
    done
    
    print_status "✅ n8n is running at http://localhost:5678"
    print_status "   Username: admin"
    print_status "   Password: admin123"
}

# Start CrewAI API
setup_crewai_api() {
    print_status "Building and starting CrewAI API..."
    
    # Create Dockerfile for CrewAI API
    cat > crewai-agents/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Start the API server
CMD ["python", "-m", "src.seo_automation.main", "serve", "--host", "0.0.0.0", "--port", "8001"]
EOF
    
    docker-compose up -d crewai-api
    
    print_status "✅ CrewAI API starting up..."
}

# Main setup function
main() {
    print_status "🚀 Starting KloudPortal SEO Automation setup..."
    
    check_prerequisites
    setup_gcloud
    setup_python
    setup_docker
    setup_database
    setup_n8n
    setup_crewai_api
    
    print_status "🎉 Setup complete!"
    print_status ""
    print_status "Services running:"
    print_status "  • n8n Dashboard: http://localhost:5678 (admin/admin123)"
    print_status "  • CrewAI API: http://localhost:8001"
    print_status "  • Grafana: http://localhost:3000 (admin/admin123)"
    print_status "  • Prometheus: http://localhost:9090"
    print_status ""
    print_status "Next steps:"
    print_status "  1. Import n8n workflows from ./n8n-workflows/"
    print_status "  2. Test the blog discovery crew: python -m crewai-agents.src.seo_automation.main discover-blogs"
    print_status "  3. Monitor costs at: http://localhost:8001/cost-report"
    print_status ""
    print_status "📖 Check the documentation for detailed usage instructions."
}

# Run main function
main "$@"
```

**scripts/deployment/start.sh**

```bash
#!/bin/bash

# Start all services
echo "🚀 Starting KloudPortal SEO Automation Platform..."

# Start Docker services
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."

# Check PostgreSQL
until docker-compose exec postgres pg_isready -U seo_user -d seo_automation; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Check Redis
until docker-compose exec redis redis-cli ping; do
    echo "Waiting for Redis..."
    sleep 2
done

# Check n8n
until curl -f http://localhost:5678/healthz &> /dev/null; do
    echo "Waiting for n8n..."
    sleep 2
done

echo "✅ All services are ready!"
echo ""
echo "🌐 Access Points:"
echo "  • n8n Dashboard: http://localhost:5678"
echo "  • CrewAI API: http://localhost:8001"
echo "  • Grafana: http://localhost:3000"
echo "  • Prometheus: http://localhost:9090"
echo ""
echo "📊 Monitor logs with: docker-compose logs -f"
```


### 10. Testing Framework

**scripts/testing/test_setup.py**

```python
#!/usr/bin/env python3
"""
Test setup and validation script
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "crewai-agents" / "src"))

from seo_automation.crew import SEOAutomationCrew
from seo_automation.utils.vertex_ai_manager import VertexAIManager
from seo_automation.utils.database import DatabaseManager


async def test_vertex_ai():
    """Test Vertex AI connectivity."""
    print("🧪 Testing Vertex AI connectivity...")
    
    try:
        manager = VertexAIManager()
        flash_model = manager.get_flash_model()
        
        response = await flash_model.ainvoke("Hello, this is a test. Please respond with 'Connection successful'.")
        
        if "successful" in response.content.lower():
            print("✅ Vertex AI connection successful")
            return True
        else:
            print(f"❌ Unexpected response: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Vertex AI connection failed: {e}")
        return False


async def test_database():
    """Test database connectivity."""
    print("🧪 Testing database connectivity...")
    
    try:
        db = DatabaseManager()
        await db.create_pool()
        
        async with db.get_connection() as conn:
            result = await conn.fetchval("SELECT 1")
            
        if result == 1:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_crewai_agents():
    """Test CrewAI agent initialization."""
    print("🧪 Testing CrewAI agents...")
    
    try:
        crew_manager = SEOAutomationCrew()
        
        # Test blog discovery crew
        blog_crew = crew_manager.blog_discovery_crew()
        
        if len(blog_crew.agents) > 0:
            print("✅ CrewAI agents initialized successfully")
            return True
        else:
            print("❌ No agents found in crew")
            return False
            
    except Exception as e:
        print(f"❌ CrewAI agent initialization failed: {e}")
        return False


async def test_full_pipeline():
    """Test a simple end-to-end pipeline."""
    print("🧪 Testing end-to-end pipeline...")
    
    try:
        crew_manager = SEOAutomationCrew()
        
        # Test inputs
        test_inputs = {
            "category": "marketing",
            "limit": 2,
            "min_domain_authority": 30
        }
        
        # Run blog discovery
        discovery_crew = crew_manager.blog_discovery_crew()
        result = discovery_crew.kickoff(inputs=test_inputs)
        
        if result and "error" not in str(result).lower():
            print("✅ End-to-end pipeline test successful")
            return True
        else:
            print(f"❌ Pipeline test failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Running KloudPortal SEO Automation Tests")
    print("=" * 50)
    
    tests = [
        ("Vertex AI", test_vertex_ai),
        ("Database", test_database),
        ("CrewAI Agents", test_crewai_agents),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
        
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```


## Quick Start Commands

Once you have this implementation guide, here are the commands to get started:

```bash
# 1. Clone and setup the project structure
mkdir seo-automation && cd seo-automation

# 2. Copy the implementation files from this guide

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your Google Cloud project details

# 4. Run the setup script
chmod +x scripts/deployment/setup.sh
./scripts/deployment/setup.sh

# 5. Test the setup
python scripts/testing/test_setup.py

# 6. Start the platform
./scripts/deployment/start.sh

# 7. Run your first blog discovery
cd crewai-agents
source venv/bin/activate
python -m src.seo_automation.main discover-blogs --limit 5 --category marketing

# 8. Monitor costs
python -m src.seo_automation.main cost-report
```

This implementation guide provides everything you need to build the hybrid n8n + CrewAI platform using Windsurf IDE or Gemini CLI. The modular structure allows you to implement and test each component independently while building toward the complete automation system.

---

## 🚀 **PHASE 6: BUN-POWERED REAL-TIME WEB SCRAPING - NEW IMPLEMENTATION APPROACH**

### **Revolutionary Architecture Decision: JavaScript/Bun Microservice**
**Decision Date**: July 30, 2025  
**Based On**: [JavaScript Automation Research](Automate%20Web%20Workflows%20Like%20a%20Boss%20with%20JavaScript.md)  
**Architecture**: Hybrid Python Backend + Bun Scraping Microservice  

### **Why Bun Over Node.js for Scraping?**
**Performance Advantages**:
- **3x Faster Startup** (50ms vs 200ms) - Critical for microservices
- **50% Less Memory** (15MB vs 30MB base) - Better resource efficiency
- **Built-in TypeScript** - No compilation step needed
- **Native Performance Monitoring** - Better debugging and optimization
- **Faster Package Installation** - Improved development experience

### **Project Status Update (July 2025)**
- ✅ **Phases 1-5 Complete**: Infrastructure, agents, frontend UI, backend integration
- ✅ **Frontend**: Modern React TypeScript application with authentication
- ✅ **Backend**: FastAPI with JWT auth, WebSocket support, agent framework
- ❌ **Critical Gap**: All data is mock/fake - needs real-time scraping integration
- 🔄 **NEW APPROACH**: Bun-powered JavaScript scraping microservice

### **Phase 6 Objectives: Transform Mock to Real Data with JavaScript Excellence**
Replace all mock data with real-time web scraping using Bun + modern JavaScript tools:

#### **Week 1-2: Bun Scraping Microservice Infrastructure**
- **Bun Runtime Setup** (FREE)
  - Lightning-fast TypeScript execution without compilation
  - Native fetch API for HTTP requests
  - Built-in WebSocket support for real-time updates
  - Integrated performance monitoring

- **Puppeteer/Playwright Integration** (FREE)
  - Full browser automation with JavaScript injection
  - SEOquake extension integration for DA/PA scores
  - Dynamic content handling (React, Vue, Angular sites)
  - Anti-detection with stealth plugins
  - Session rotation and cookie management

- **Search Engine Integration** (FREE APIs)
  - Google Custom Search API (100 queries/day FREE)
  - Bing Search API (3000 queries/month FREE) 
  - DuckDuckGo scraping (unlimited FREE)
  - SERP result parsing with DOM manipulation

#### **Week 3-4: Python-Bun Integration & UI Updates**
- **Microservice Communication**
  - HTTP API endpoints between Python backend and Bun service
  - Real-time WebSocket updates for scraping progress
  - JSON-based data exchange protocols
  - Error handling and fallback mechanisms

- **Dashboard Real Data Integration**
  - Replace mock `activeCampaigns: 12` → Real database count
  - Replace mock `blogsDiscovered: 2847` → Actual scraped count  
  - Replace mock `commentsGenerated: 1234` → Real generation stats
  - Replace mock `successRate: 87.5%` → Calculated metrics

### **New Architecture: Hybrid Microservice Approach**
```
CrewAI KP Bot - Enhanced Architecture:
├── Python Backend (FastAPI)        # AI agents, database, auth
│   ├── Agent Framework
│   ├── Database Management  
│   ├── JWT Authentication
│   └── WebSocket Manager
├── Bun Scraping Service            # Real-time data collection
│   ├── Browser Automation
│   ├── Authority Scoring
│   ├── Content Extraction
│   └── Rate Limiting
├── React Frontend                  # UI with real-time updates
└── Communication Bridge            # HTTP + WebSocket integration
```

### **Implementation Files for Phase 6 - Bun Microservice**
```
scraping-service/                   # New Bun microservice
├── package.json                    # Bun dependencies
├── tsconfig.json                   # TypeScript configuration
├── src/
│   ├── main.ts                     # Bun server entry point
│   ├── services/
│   │   ├── blogScraper.ts          # Main scraping orchestrator
│   │   ├── searchEngines.ts        # Google/Bing/DuckDuckGo
│   │   ├── authorityScorer.ts      # DA/PA with SEOquake
│   │   ├── contentAnalyzer.ts      # Content extraction
│   │   ├── rateLimiter.ts          # Request throttling
│   │   └── dataValidator.ts        # Result validation
│   ├── api/
│   │   ├── routes.ts               # HTTP API endpoints
│   │   └── websocket.ts            # Real-time updates
│   ├── utils/
│   │   ├── browser.ts              # Puppeteer management
│   │   └── stealth.ts              # Anti-detection
│   └── types/
│       └── scraping.ts             # TypeScript interfaces
├── Dockerfile                      # Container configuration
└── bun.lockb                       # Bun lock file

src/api/routes/                     # Updated Python endpoints
├── scraping_integration.py        # Bun service communication
├── dashboard_real.py               # Real statistics endpoints
└── scraping_status.py              # Progress tracking APIs

frontend/src/services/              # Updated frontend services
├── realTimeApi.ts                  # WebSocket integration
├── scrapingService.ts              # Bun service communication
└── dashboardService.ts             # Real data fetching
```

### **Success Criteria for Phase 6 - Bun Implementation**
- [ ] Bun scraping microservice running with <500ms response times
- [ ] Dashboard shows real blog counts (not 2847 mock)
- [ ] Blog research returns live scraped results with JavaScript DOM access
- [ ] Authority scores from SEOquake integration working via browser automation
- [ ] Database contains actual scraped blog data with enhanced metadata
- [ ] Search functionality queries real search engines with rate limiting
- [ ] No mock data remaining in any API responses
- [ ] Python-Bun communication working via HTTP/WebSocket
- [ ] Real-time scraping progress updates in frontend

### **Cost Analysis - FREE Strategy + Bun Performance Benefits**
```
Bun Runtime: $0 (Open source)
Browser Automation (Puppeteer/Playwright): $0
SEOquake Integration: $0
Search APIs (Free Tiers): $0
Authority Checkers: $0
Additional Vertex AI Usage: ~$20/month
Cloud Hosting (Bun microservice): ~$5/month (minimal resources needed)
Total Monthly Cost: ~$25/month
Google Cloud $300 Credits: 12 months operation ✅

Performance ROI:
- 3x faster startup = 3x more efficient scraping cycles
- 50% less memory = 2x more concurrent scraping tasks
- Native TypeScript = Faster development and debugging
```

### **Timeline: 4 Weeks to Production-Ready Real Data with Bun**
- **Week 1**: Bun setup + Puppeteer integration + SEOquake
- **Week 2**: Search engine APIs + authority scoring + stealth features
- **Week 3**: Python-Bun integration + database + WebSocket updates  
- **Week 4**: Frontend integration + testing + performance optimization

**Result**: Complete transformation from mock data prototype to production-ready real-time SEO automation platform powered by cutting-edge JavaScript technology.

### **Why This Approach Will Succeed**
1. **Superior Browser Automation**: Native JavaScript execution in browsers
2. **Modern Web Compatibility**: Perfect for React/Vue/Angular blog platforms
3. **Performance Excellence**: Bun's speed advantages compound over time
4. **Developer Experience**: TypeScript without compilation overhead
5. **Scalability**: Microservice architecture allows independent scaling
6. **Future-Proof**: JavaScript ecosystem leadership in web automation

---

### **Phase 7-8 Roadmap (Post Phase 6 Bun Implementation)**
- **Phase 7 (Weeks 5-8)**: Complete UI implementation (Comments, Analytics, Settings pages) with real scraped data
- **Phase 8 (Weeks 9-12)**: Advanced features (ML insights, JavaScript-powered automation enhancements, collaboration, monitoring)

### **Long-term JavaScript/Bun Advantages**
- **Extensibility**: Easy to add new scraping targets with JavaScript familiarity
- **Community**: Massive ecosystem of web automation tools and libraries
- **Innovation**: Cutting-edge browser automation techniques (stealth, captcha solving)
- **Performance**: Continuous improvements from Bun's active development
- **Debugging**: Superior web debugging tools compared to Python scraping

<div style="text-align: center">⁂</div>

[^1]: PRD.md

