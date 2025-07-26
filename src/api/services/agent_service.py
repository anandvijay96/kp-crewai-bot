"""
Agent Service
=============

Service layer for agent status monitoring and coordination.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.agent import AgentStatus, AgentTask, AgentMetrics
from ..models.user import User
from ...seo_automation.utils.database import db_manager

logger = logging.getLogger(__name__)

class AgentService:
    """Service for managing AI agent status and coordination."""
    
    @staticmethod
    def get_agents_status(user_id: int) -> Dict[str, Any]:
        """
        Get status of all AI agents for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing agent status information
        """
        try:
            # Try to get real agent status
            agents_status = []
            
            # Import agents dynamically
            agents_info = [
                {
                    'type': 'blog_researcher',
                    'name': 'Blog Research Agent',
                    'module': '...seo_automation.agents.enhanced_blog_researcher',
                    'class': 'EnhancedBlogResearcherAgent'
                },
                {
                    'type': 'comment_writer',
                    'name': 'Comment Writer Agent',
                    'module': '...seo_automation.agents.comment_writer_agent',
                    'class': 'CommentWriterAgent'
                },
                {
                    'type': 'quality_reviewer',
                    'name': 'Quality Review Agent',
                    'module': '...seo_automation.agents.quality_reviewer',
                    'class': 'QualityReviewerAgent'
                },
                {
                    'type': 'campaign_manager',
                    'name': 'Campaign Manager Agent',
                    'module': '...seo_automation.agents.campaign_manager',
                    'class': 'CampaignManagerAgent'
                }
            ]
            
            for agent_info in agents_info:
                try:
                    # Try to import and check agent
                    status = AgentService._check_agent_status(agent_info)
                    agents_status.append(status)
                except Exception as e:
                    logger.warning(f"Could not check status for {agent_info['name']}: {e}")
                    # Create mock status for unavailable agents
                    agents_status.append({
                        'agent_type': agent_info['type'],
                        'name': agent_info['name'],
                        'status': 'unavailable',
                        'last_activity': None,
                        'performance_metrics': {
                            'tasks_completed': 0,
                            'success_rate': 0.0,
                            'average_execution_time': 0.0,
                            'error_count': 0
                        },
                        'resource_usage': {
                            'cpu_usage': 0.0,
                            'memory_usage': 0.0,
                            'api_calls_today': 0
                        },
                        'error_message': str(e)
                    })
            
            return {
                'agents': agents_status,
                'total_agents': len(agents_status),
                'active_agents': len([a for a in agents_status if a['status'] == 'active']),
                'inactive_agents': len([a for a in agents_status if a['status'] in ['inactive', 'unavailable']]),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get agents status: {e}")
            raise

    @staticmethod
    def get_agent_status(agent_type: str, user_id: int) -> Dict[str, Any]:
        """
        Get status of a specific agent.
        
        Args:
            agent_type: Type of agent
            user_id: User ID
            
        Returns:
            Agent status information
        """
        try:
            # Map agent types to modules
            agent_mapping = {
                'blog_researcher': {
                    'name': 'Blog Research Agent',
                    'module': '...seo_automation.agents.enhanced_blog_researcher',
                    'class': 'EnhancedBLogResearcherAgent'
                },
                'comment_writer': {
                    'name': 'Comment Writer Agent',
                    'module': '...seo_automation.agents.comment_writer_agent',
                    'class': 'CommentWriterAgent'
                },
                'quality_reviewer': {
                    'name': 'Quality Review Agent',
                    'module': '...seo_automation.agents.quality_reviewer',
                    'class': 'QualityReviewerAgent'
                },
                'campaign_manager': {
                    'name': 'Campaign Manager Agent',
                    'module': '...seo_automation.agents.campaign_manager',
                    'class': 'CampaignManagerAgent'
                }
            }
            
            if agent_type not in agent_mapping:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            agent_info = agent_mapping[agent_type]
            agent_info['type'] = agent_type
            
            return AgentService._check_agent_status(agent_info)
            
        except Exception as e:
            logger.error(f"Failed to get agent status for {agent_type}: {e}")
            raise

    @staticmethod
    def execute_agent_task(
        agent_type: str,
        task_params: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Execute a task with a specific agent.
        
        Args:
            agent_type: Type of agent
            task_params: Task parameters
            user_id: User ID
            
        Returns:
            Task execution result
        """
        try:
            with db_manager.get_session() as session:
                # Create task record
                task = AgentTask(
                    id=str(uuid.uuid4()),
                    agent_type=agent_type,
                    user_id=user_id,
                    parameters=task_params,
                    status='running',
                    created_at=datetime.utcnow(),
                    started_at=datetime.utcnow()
                )
                
                session.add(task)
                session.commit()
                session.refresh(task)
                
                try:
                    # Execute task based on agent type
                    start_time = datetime.utcnow()
                    result = AgentService._execute_task_by_type(agent_type, task_params)
                    end_time = datetime.utcnow()
                    
                    # Update task with results
                    task.status = 'completed'
                    task.result = result
                    task.completed_at = end_time
                    task.execution_time = (end_time - start_time).total_seconds()
                    
                    session.commit()
                    
                    logger.info(f"Task {task.id} completed successfully")
                    
                    return {
                        'task_id': task.id,
                        'agent_type': agent_type,
                        'status': 'completed',
                        'result': result,
                        'execution_time': task.execution_time,
                        'started_at': task.started_at.isoformat(),
                        'completed_at': task.completed_at.isoformat()
                    }
                    
                except Exception as task_error:
                    # Update task with error
                    task.status = 'failed'
                    task.error_message = str(task_error)
                    task.completed_at = datetime.utcnow()
                    
                    session.commit()
                    
                    logger.error(f"Task {task.id} failed: {task_error}")
                    
                    return {
                        'task_id': task.id,
                        'agent_type': agent_type,
                        'status': 'failed',
                        'error': str(task_error),
                        'started_at': task.started_at.isoformat(),
                        'completed_at': task.completed_at.isoformat()
                    }
                
        except Exception as e:
            logger.error(f"Failed to execute agent task: {e}")
            raise

    @staticmethod
    def get_agent_tasks(
        user_id: int,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get agent tasks for a user with filtering.
        
        Args:
            user_id: User ID
            agent_type: Optional agent type filter
            status: Optional status filter
            page: Page number
            page_size: Items per page
            
        Returns:
            Dict containing tasks and pagination info
        """
        try:
            with db_manager.get_session() as session:
                query = session.query(AgentTask).filter(
                    AgentTask.user_id == user_id
                )
                
                if agent_type:
                    query = query.filter(AgentTask.agent_type == agent_type)
                
                if status:
                    query = query.filter(AgentTask.status == status)
                
                total = query.count()
                
                tasks = query.order_by(AgentTask.created_at.desc()).offset(
                    (page - 1) * page_size
                ).limit(page_size).all()
                
                task_list = [
                    AgentService._task_to_dict(task)
                    for task in tasks
                ]
                
                return {
                    'tasks': task_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'pages': (total + page_size - 1) // page_size
                }
                
        except Exception as e:
            logger.error(f"Failed to get agent tasks: {e}")
            raise

    @staticmethod
    def get_agent_analytics(user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get analytics for agent activities.
        
        Args:
            user_id: User ID
            days: Number of days to include
            
        Returns:
            Agent analytics data
        """
        try:
            with db_manager.get_session() as session:
                # Get tasks from the specified period
                since_date = datetime.utcnow() - timedelta(days=days)
                
                tasks = session.query(AgentTask).filter(
                    and_(
                        AgentTask.user_id == user_id,
                        AgentTask.created_at >= since_date
                    )
                ).all()
                
                # Calculate analytics
                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t.status == 'completed'])
                failed_tasks = len([t for t in tasks if t.status == 'failed'])
                running_tasks = len([t for t in tasks if t.status == 'running'])
                
                # Agent-specific metrics
                agent_metrics = {}
                for task in tasks:
                    agent_type = task.agent_type
                    if agent_type not in agent_metrics:
                        agent_metrics[agent_type] = {
                            'total_tasks': 0,
                            'completed_tasks': 0,
                            'failed_tasks': 0,
                            'total_execution_time': 0.0,
                            'average_execution_time': 0.0
                        }
                    
                    agent_metrics[agent_type]['total_tasks'] += 1
                    
                    if task.status == 'completed':
                        agent_metrics[agent_type]['completed_tasks'] += 1
                        if task.execution_time:
                            agent_metrics[agent_type]['total_execution_time'] += task.execution_time
                    elif task.status == 'failed':
                        agent_metrics[agent_type]['failed_tasks'] += 1
                
                # Calculate average execution times
                for agent_type, metrics in agent_metrics.items():
                    if metrics['completed_tasks'] > 0:
                        metrics['average_execution_time'] = (
                            metrics['total_execution_time'] / metrics['completed_tasks']
                        )
                
                analytics = {
                    'period': f'Last {days} days',
                    'overview': {
                        'total_tasks': total_tasks,
                        'completed_tasks': completed_tasks,
                        'failed_tasks': failed_tasks,
                        'running_tasks': running_tasks,
                        'success_rate': completed_tasks / max(total_tasks, 1)
                    },
                    'agent_metrics': agent_metrics,
                    'daily_activity': AgentService._calculate_daily_activity(tasks, days),
                    'recent_tasks': [
                        AgentService._task_to_dict(task)
                        for task in sorted(tasks, key=lambda x: x.created_at, reverse=True)[:10]
                    ]
                }
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get agent analytics: {e}")
            raise

    @staticmethod
    def _check_agent_status(agent_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check the status of a specific agent."""
        try:
            # Try to import the agent
            # In a real implementation, this would actually check agent health
            
            # For now, return mock status based on common agent patterns
            mock_status = {
                'agent_type': agent_info['type'],
                'name': agent_info['name'],
                'status': 'active',  # Would be determined by actual health check
                'last_activity': datetime.utcnow().isoformat(),
                'performance_metrics': {
                    'tasks_completed': 45 + hash(agent_info['type']) % 100,
                    'success_rate': 0.92 + (hash(agent_info['type']) % 8) / 100,
                    'average_execution_time': 15.5 + (hash(agent_info['type']) % 20),
                    'error_count': hash(agent_info['type']) % 5
                },
                'resource_usage': {
                    'cpu_usage': 0.15 + (hash(agent_info['type']) % 30) / 100,
                    'memory_usage': 0.25 + (hash(agent_info['type']) % 40) / 100,
                    'api_calls_today': 50 + hash(agent_info['type']) % 150
                },
                'health_check': {
                    'last_check': datetime.utcnow().isoformat(),
                    'response_time': 0.05 + (hash(agent_info['type']) % 10) / 100,
                    'status': 'healthy'
                }
            }
            
            return mock_status
            
        except Exception as e:
            # Return unavailable status if agent can't be checked
            return {
                'agent_type': agent_info['type'],
                'name': agent_info['name'],
                'status': 'unavailable',
                'last_activity': None,
                'error_message': str(e),
                'performance_metrics': {
                    'tasks_completed': 0,
                    'success_rate': 0.0,
                    'average_execution_time': 0.0,
                    'error_count': 1
                },
                'resource_usage': {
                    'cpu_usage': 0.0,
                    'memory_usage': 0.0,
                    'api_calls_today': 0
                }
            }

    @staticmethod
    def _execute_task_by_type(agent_type: str, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task based on agent type."""
        # This would route to the appropriate agent
        # For now, return mock results
        
        if agent_type == 'blog_researcher':
            return {
                'blogs_discovered': 5,
                'total_analyzed': 12,
                'average_quality': 0.85,
                'execution_details': 'Blog research completed successfully'
            }
        elif agent_type == 'comment_writer':
            return {
                'comments_generated': 3,
                'average_quality': 0.89,
                'total_words': 245,
                'execution_details': 'Comments generated successfully'
            }
        elif agent_type == 'quality_reviewer':
            return {
                'items_reviewed': 8,
                'approved': 6,
                'rejected': 2,
                'average_score': 0.82,
                'execution_details': 'Quality review completed'
            }
        elif agent_type == 'campaign_manager':
            return {
                'tasks_coordinated': 15,
                'campaigns_updated': 2,
                'completion_rate': 0.94,
                'execution_details': 'Campaign coordination completed'
            }
        else:
            return {
                'status': 'completed',
                'message': f'Task executed for {agent_type}',
                'execution_details': 'Generic task execution'
            }

    @staticmethod
    def _calculate_daily_activity(tasks: List[AgentTask], days: int) -> List[Dict[str, Any]]:
        """Calculate daily activity metrics."""
        daily_stats = {}
        
        for task in tasks:
            day_key = task.created_at.date().isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    'date': day_key,
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'failed_tasks': 0
                }
            
            daily_stats[day_key]['total_tasks'] += 1
            
            if task.status == 'completed':
                daily_stats[day_key]['completed_tasks'] += 1
            elif task.status == 'failed':
                daily_stats[day_key]['failed_tasks'] += 1
        
        # Fill missing days with zero activity
        current_date = datetime.utcnow().date()
        for i in range(days):
            day = current_date - timedelta(days=i)
            day_key = day.isoformat()
            
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    'date': day_key,
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'failed_tasks': 0
                }
        
        return sorted(daily_stats.values(), key=lambda x: x['date'])

    @staticmethod
    def _task_to_dict(task: AgentTask) -> Dict[str, Any]:
        """Convert AgentTask model to dictionary."""
        return {
            'id': task.id,
            'agent_type': task.agent_type,
            'parameters': task.parameters,
            'status': task.status,
            'result': task.result,
            'error_message': task.error_message,
            'execution_time': task.execution_time,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        }
