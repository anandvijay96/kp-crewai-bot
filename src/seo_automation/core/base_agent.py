"""
BaseSEOAgent - Enhanced base agent class integrating Phase 1 tools

This module provides the foundation for all Phase 2 SEO agents with:
- Integration with Phase 1 tools (WebScraper, ContentAnalysisTool, SEOAnalyzer, BlogValidatorTool)
- Vertex AI management with cost tracking
- Database operations and logging
- Error handling and retry mechanisms
- Performance monitoring
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

from crewai import Agent
from crewai.tools import BaseTool

from ..utils.vertex_ai_manager import VertexAIManager
from ..utils.database import AgentExecution, db_manager
from ..config.settings import settings
from ..tools.web_scraper import WebScraper
from ..tools.content_analysis import ContentAnalysisTool
from ..tools.seo_analyzer import SEOAnalyzer
from ..tools.blog_validator import BlogValidatorTool


class BaseSEOAgent(ABC):
    """
    Enhanced base class for Phase 2 SEO automation agents.
    
    Provides common functionality for:
    - Phase 1 tool integration
    - Vertex AI integration with cost tracking
    - Database logging of agent executions
    - Error handling and retry logic
    - Performance monitoring
    """
    
    def __init__(self, 
                 name: str,
                 role: str, 
                 goal: str,
                 backstory: str,
                 additional_tools: List[BaseTool] = None,
                 model_name: str = "gemini-2.0-flash-exp",
                 max_execution_time: int = 300):
        """
        Initialize the enhanced SEO agent with Phase 1 tools.
        
        Args:
            name: Agent name for identification
            role: Agent's role description
            goal: Agent's primary goal
            backstory: Agent's background story
            additional_tools: Additional tools beyond Phase 1 suite
            model_name: Vertex AI model to use
            max_execution_time: Maximum execution time in seconds
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.model_name = model_name
        self.max_execution_time = max_execution_time
        
        # Initialize core components
        self.vertex_ai = VertexAIManager()
        self.logger = logging.getLogger(f"agent.{name.lower()}")
        self.db_session = db_manager.get_session()
        
        # Initialize Phase 1 tools
        self._initialize_phase1_tools()
        
        # Combine Phase 1 tools with additional tools
        self.tools = self.phase1_tools + (additional_tools or [])
        
        # Create CrewAI agent instance
        self._agent = None
        self._initialize_agent()
    
    def _initialize_phase1_tools(self):
        """
        Initialize all Phase 1 tools for this agent.
        """
        try:
            self.web_scraper = WebScraper()
            self.content_analyzer = ContentAnalysisTool()
            self.seo_analyzer = SEOAnalyzer()
            self.blog_validator = BlogValidatorTool()
            
            # Create tools list for CrewAI agent
            self.phase1_tools = [
                self.content_analyzer,
                self.blog_validator
            ]
            
            self.logger.info(f"Initialized Phase 1 tools for {self.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Phase 1 tools: {e}")
            raise
    
    def _initialize_agent(self):
        """Initialize the CrewAI agent with Vertex AI integration."""
        try:
            # Configure agent with Vertex AI LLM
            llm = self.vertex_ai.get_llm(self.model_name)
            
            self._agent = Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                tools=self.tools,
                llm=llm,
                verbose=settings.is_development,
                allow_delegation=False,
                max_execution_time=self.max_execution_time
            )
            
            self.logger.info(f"Initialized {self.name} agent with model {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name} agent: {e}")
            raise
    
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task with cost tracking and error handling.
        
        Args:
            task: Task description for the agent
            context: Additional context data
            
        Returns:
            Dict containing execution results and metadata
        """
        execution_id = None
        start_time = datetime.utcnow()
        
        try:
            # Log execution start
            execution_id = self._log_execution_start(task, context)
            
            self.logger.info(f"Executing task for {self.name}: {task[:100]}...")
            
            # Execute the actual task
            result = self._execute_task(task, context)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Prepare response
            response = {
                'agent': self.name,
                'task': task,
                'result': result,
                'execution_time': execution_time,
                'success': True
            }
            
            # Log successful execution
            self._log_execution_complete(execution_id, response)
            
            self.logger.info(f"{self.name} completed task successfully in {execution_time:.2f}s")
            return response
                
        except Exception as e:
            self.logger.error(f"{self.name} execution failed: {e}")
            
            # Log failed execution
            error_response = {
                'agent': self.name,
                'task': task,
                'error': str(e),
                'execution_time': (datetime.utcnow() - start_time).total_seconds(),
                'success': False
            }
            
            if execution_id:
                self._log_execution_complete(execution_id, error_response)
            
            raise
    
    @abstractmethod
    def _execute_task(self, task: str, context: Dict[str, Any] = None) -> Any:
        """
        Execute the specific task for this agent type.
        Must be implemented by subclasses.
        
        Args:
            task: Task description
            context: Additional context data
            
        Returns:
            Task execution result
        """
        pass
    
    def _log_execution_start(self, task: str, context: Dict[str, Any] = None) -> int:
        """Log the start of an agent execution."""
        if not self.db_session:
            return None
            
        try:
            execution = AgentExecution(
                agent_name=self.name,
                task_description=task,
                context_data=context or {},
                model_name=self.model_name,
                started_at=datetime.utcnow(),
                status='running'
            )
            
            self.db_session.add(execution)
            self.db_session.commit()
            
            return execution.id
            
        except Exception as e:
            self.logger.warning(f"Failed to log execution start: {e}")
            return None
    
    def _log_execution_complete(self, execution_id: int, result: Dict[str, Any]):
        """Log the completion of an agent execution."""
        if not execution_id or not self.db_session:
            return
            
        try:
            execution = self.db_session.get(AgentExecution, execution_id)
            if execution:
                execution.completed_at = datetime.utcnow()
                execution.status = 'completed' if result.get('success') else 'failed'
                execution.result_data = result
                execution.cost = self.vertex_ai.get_session_cost()
                
                self.db_session.commit()
                
        except Exception as e:
            self.logger.warning(f"Failed to log execution completion: {e}")
    
    # Phase 1 Tool Helper Methods
    def scrape_content(self, url: str) -> Dict[str, Any]:
        """Helper method to scrape web content using WebScraper tool."""
        try:
            html_content = self.web_scraper.fetch_page(url)
            if html_content:
                soup = self.web_scraper.parse_content(html_content)
                return {
                    'success': True,
                    'content': html_content,
                    'soup': soup
                }
            else:
                return {'success': False, 'error': 'Failed to fetch content'}
        except Exception as e:
            self.logger.error(f"Content scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Helper method to analyze content using ContentAnalysisTool."""
        try:
            return self.content_analyzer._run(content)
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_seo(self, html_content: str) -> Dict[str, Any]:
        """Helper method to analyze SEO using SEOAnalyzer."""
        try:
            return self.seo_analyzer.analyze_page(html_content)
        except Exception as e:
            self.logger.error(f"SEO analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_blog(self, blog_url: str) -> Dict[str, Any]:
        """Helper method to validate blog using BlogValidatorTool."""
        try:
            return self.blog_validator._run(blog_url)
        except Exception as e:
            self.logger.error(f"Blog validation failed: {e}")
            return {'success': False, 'error': str(e)}
