"""
Base Agent Class for SEO Automation

This module provides the foundation for all CrewAI agents in the SEO automation system.
It integrates with Phase 1 components including Vertex AI management, cost tracking,
and database operations.
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


class BaseAgent(ABC):
    """
    Abstract base class for all SEO automation agents.
    
    Provides common functionality for:
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
                 tools: List[BaseTool] = None,
                 model_name: str = "gemini-2.0-flash-exp",
                 max_execution_time: int = 300):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name for identification
            role: Agent's role description
            goal: Agent's primary goal
            backstory: Agent's background story
            tools: List of tools available to the agent
            model_name: Vertex AI model to use
            max_execution_time: Maximum execution time in seconds
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.model_name = model_name
        self.max_execution_time = max_execution_time
        
        # Initialize core components
        self.vertex_ai = VertexAIManager()
        self.logger = logging.getLogger(f"agent.{name.lower()}")
        self.db_session = db_manager.get_session()
        
        # Create CrewAI agent instance
        self._agent = None
        self._initialize_agent()
    
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
                execution.cost = result.get('cost', 0.0)
                execution.tokens_used = result.get('tokens_used', 0)
                execution.execution_time = result.get('execution_time', 0.0)
                
                self.db_session.commit()
                
        except Exception as e:
            self.logger.warning(f"Failed to log execution completion: {e}")
    
    def get_agent(self) -> Agent:
        """Get the underlying CrewAI agent instance."""
        return self._agent
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this agent."""
        if not self.db_session:
            return {'error': 'Database session not available'}
            
        try:
            executions = self.db_session.query(AgentExecution).filter_by(
                agent_name=self.name
            ).all()
            
            if not executions:
                return {'message': 'No execution history found'}
            
            successful = [e for e in executions if e.status == 'completed']
            failed = [e for e in executions if e.status == 'failed']
            
            stats = {
                'total_executions': len(executions),
                'successful_executions': len(successful),
                'failed_executions': len(failed),
                'success_rate': len(successful) / len(executions) * 100,
                'average_execution_time': sum(e.execution_time or 0 for e in executions) / len(executions),
                'total_cost': sum(e.cost or 0 for e in executions),
                'total_tokens': sum(e.tokens_used or 0 for e in executions)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get performance stats: {e}")
            return {'error': str(e)}
    
    def reset_performance_stats(self):
        """Reset performance statistics for this agent."""
        if not self.db_session:
            raise Exception("Database session not available")
            
        try:
            self.db_session.query(AgentExecution).filter_by(
                agent_name=self.name
            ).delete()
            self.db_session.commit()
            
            self.logger.info(f"Reset performance stats for {self.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to reset performance stats: {e}")
            raise
    
    def __str__(self):
        return f"{self.name} Agent (Role: {self.role})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', model='{self.model_name}')>"
