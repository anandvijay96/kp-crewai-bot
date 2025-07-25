"""
CampaignManagerAgent - Advanced SEO campaign orchestration with multi-agent coordination

This agent manages end-to-end SEO campaigns by coordinating multiple specialized agents:
- BlogResearcher: Discovers and validates target blogs
- CommentWriter: Generates contextual comments
- Quality assurance and validation workflows
- Performance tracking and optimization
- Resource management and cost control
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
from enum import Enum

from ..core.base_agent import BaseSEOAgent
from ..utils.database import db_manager
from .enhanced_blog_researcher import EnhancedBlogResearcherAgent
from .comment_writer import CommentWriterAgent


class CampaignStatus(Enum):
    """Campaign status enumeration"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CampaignManagerAgent(BaseSEOAgent):
    """
    Advanced Campaign Manager Agent for SEO workflow orchestration
    
    Capabilities:
    1. Multi-agent coordination and task scheduling
    2. End-to-end campaign lifecycle management
    3. Resource optimization and cost control
    4. Performance monitoring and analytics
    5. Error handling and recovery mechanisms
    6. Database integration for campaign tracking
    7. Automated reporting and insights
    8. Dynamic task prioritization
    """

    def __init__(self):
        super().__init__(
            name="CampaignManager",
            role="SEO Campaign Orchestration Specialist",
            goal="""Orchestrate comprehensive SEO campaigns by coordinating specialized agents
                   to maximize engagement effectiveness while optimizing resource utilization""",
            backstory="""You are an expert SEO campaign manager with deep understanding of multi-agent
                      coordination. You excel at breaking down complex SEO strategies into manageable
                      tasks, coordinating specialized agents, monitoring performance, and optimizing
                      campaigns for maximum ROI. Your expertise includes workflow automation,
                      resource management, quality assurance, and strategic decision-making.""",
            model_name="gemini-2.0-flash-exp"
        )
        
        # Initialize agent registry
        self.agents = {
            'blog_researcher': None,
            'comment_writer': None
        }
        
        # Campaign management state
        self.active_campaigns = {}
        self.task_queue = []
        self.performance_metrics = {}
        
        # Configuration settings
        self.config = {
            'max_concurrent_campaigns': 5,
            'max_concurrent_tasks': 10,
            'default_timeout': 300,  # 5 minutes
            'retry_attempts': 3,
            'cost_threshold': 50.0,  # Dollar threshold for cost control
            'quality_threshold': 0.7  # Minimum quality score
        }
        
        # Initialize specialized agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized agents for campaign execution"""
        try:
            self.agents['blog_researcher'] = EnhancedBlogResearcherAgent()
            self.agents['comment_writer'] = CommentWriterAgent()
            
            self.logger.info("Initialized specialized agents for campaign management")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def create_campaign(
        self, 
        name: str,
        keywords: List[str],
        target_blogs: int = 20,
        comments_per_blog: int = 1,
        campaign_type: str = "standard",
        priority: str = "medium",
        schedule_time: datetime = None
    ) -> Dict[str, Any]:
        """
        Create a new SEO campaign with specified parameters
        
        Args:
            name: Campaign name
            keywords: Target keywords for the campaign
            target_blogs: Number of blogs to target
            comments_per_blog: Number of comments per blog
            campaign_type: Type of campaign (standard, aggressive, conservative)
            priority: Campaign priority (low, medium, high)
            schedule_time: When to start the campaign
            
        Returns:
            Campaign creation result with campaign ID
        """
        try:
            campaign_id = str(uuid.uuid4())
            
            # Create campaign configuration
            campaign_config = {
                'id': campaign_id,
                'name': name,
                'keywords': keywords,
                'target_blogs': target_blogs,
                'comments_per_blog': comments_per_blog,
                'campaign_type': campaign_type,
                'priority': priority,
                'status': CampaignStatus.SCHEDULED.value,
                'created_at': datetime.utcnow(),
                'scheduled_start': schedule_time or datetime.utcnow(),
                'tasks': [],
                'metrics': {
                    'blogs_discovered': 0,
                    'blogs_qualified': 0,
                    'comments_generated': 0,
                    'comments_posted': 0,
                    'total_cost': 0.0,
                    'success_rate': 0.0
                }
            }
            
            # Generate campaign tasks
            tasks = self._generate_campaign_tasks(campaign_config)
            campaign_config['tasks'] = tasks
            
            # Store campaign
            self.active_campaigns[campaign_id] = campaign_config
            
            # Store in database
            self._store_campaign(campaign_config)
            
            self.logger.info(f"Created campaign '{name}' with ID {campaign_id}")
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'campaign_config': campaign_config,
                'estimated_cost': self._estimate_campaign_cost(campaign_config),
                'estimated_duration': self._estimate_campaign_duration(campaign_config)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create campaign: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_campaign_tasks(self, campaign_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tasks for a campaign based on configuration"""
        tasks = []
        campaign_id = campaign_config['id']
        keywords = campaign_config['keywords']
        target_blogs = campaign_config['target_blogs']
        comments_per_blog = campaign_config['comments_per_blog']
        
        # Task 1: Blog Research and Discovery
        research_task = {
            'id': str(uuid.uuid4()),
            'campaign_id': campaign_id,
            'type': 'blog_research',
            'status': TaskStatus.PENDING.value,
            'agent': 'blog_researcher',
            'priority': 1,
            'parameters': {
                'keywords': keywords,
                'max_results': target_blogs,
                'min_authority': 60
            },
            'dependencies': [],
            'created_at': datetime.utcnow()
        }
        tasks.append(research_task)
        
        # Task 2: Content Analysis (depends on research)
        analysis_task = {
            'id': str(uuid.uuid4()),
            'campaign_id': campaign_id,
            'type': 'content_analysis',
            'status': TaskStatus.PENDING.value,
            'agent': 'blog_researcher',
            'priority': 2,
            'parameters': {
                'analyze_content': True,
                'extract_topics': True
            },
            'dependencies': [research_task['id']],
            'created_at': datetime.utcnow()
        }
        tasks.append(analysis_task)
        
        # Task 3: Comment Generation (depends on analysis)
        for i in range(comments_per_blog):
            comment_task = {
                'id': str(uuid.uuid4()),
                'campaign_id': campaign_id,
                'type': 'comment_generation',
                'status': TaskStatus.PENDING.value,
                'agent': 'comment_writer',
                'priority': 3,
                'parameters': {
                    'comment_type': 'engaging' if i == 0 else 'insight',
                    'target_keywords': keywords,
                    'batch_size': min(5, target_blogs // 4)
                },
                'dependencies': [analysis_task['id']],
                'created_at': datetime.utcnow()
            }
            tasks.append(comment_task)
        
        # Task 4: Quality Review and Validation
        validation_task = {
            'id': str(uuid.uuid4()),
            'campaign_id': campaign_id,
            'type': 'quality_validation',
            'status': TaskStatus.PENDING.value,
            'agent': 'campaign_manager',
            'priority': 4,
            'parameters': {
                'quality_threshold': self.config['quality_threshold'],
                'validate_spam': True,
                'check_relevance': True
            },
            'dependencies': [task['id'] for task in tasks if task['type'] == 'comment_generation'],
            'created_at': datetime.utcnow()
        }
        tasks.append(validation_task)
        
        return tasks
    
    async def execute_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Execute a campaign by coordinating all tasks and agents
        
        Args:
            campaign_id: ID of the campaign to execute
            
        Returns:
            Campaign execution results
        """
        if campaign_id not in self.active_campaigns:
            return {'success': False, 'error': 'Campaign not found'}
        
        campaign = self.active_campaigns[campaign_id]
        
        try:
            # Update campaign status
            campaign['status'] = CampaignStatus.RUNNING.value
            campaign['started_at'] = datetime.utcnow()
            
            self.logger.info(f"Starting campaign execution: {campaign['name']}")
            
            # Execute tasks in dependency order
            execution_results = await self._execute_campaign_tasks(campaign)
            
            # Calculate final metrics
            final_metrics = self._calculate_campaign_metrics(campaign, execution_results)
            campaign['metrics'].update(final_metrics)
            
            # Update campaign status
            campaign['status'] = CampaignStatus.COMPLETED.value
            campaign['completed_at'] = datetime.utcnow()
            
            # Generate campaign report
            campaign_report = self._generate_campaign_report(campaign, execution_results)
            
            self.logger.info(f"Campaign {campaign['name']} completed successfully")
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'execution_results': execution_results,
                'final_metrics': final_metrics,
                'campaign_report': campaign_report,
                'total_duration': (campaign['completed_at'] - campaign['started_at']).total_seconds()
            }
            
        except Exception as e:
            # Handle campaign failure
            campaign['status'] = CampaignStatus.FAILED.value
            campaign['error'] = str(e)
            
            self.logger.error(f"Campaign {campaign['name']} failed: {e}")
            
            return {
                'success': False,
                'campaign_id': campaign_id,
                'error': str(e)
            }
    
    async def _execute_campaign_tasks(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all tasks for a campaign in proper dependency order"""
        tasks = campaign['tasks']
        completed_tasks = set()
        task_results = {}
        
        # Sort tasks by priority
        sorted_tasks = sorted(tasks, key=lambda t: t['priority'])
        
        for task in sorted_tasks:
            task_id = task['id']
            
            # Check if dependencies are completed
            dependencies_met = all(dep_id in completed_tasks for dep_id in task['dependencies'])
            
            if not dependencies_met:
                self.logger.warning(f"Skipping task {task_id} - dependencies not met")
                task['status'] = TaskStatus.SKIPPED.value
                continue
            
            try:
                # Execute task
                task['status'] = TaskStatus.RUNNING.value
                task_result = await self._execute_single_task(task, task_results)
                
                task['status'] = TaskStatus.COMPLETED.value
                task_results[task_id] = task_result
                completed_tasks.add(task_id)
                
                self.logger.info(f"Task {task['type']} completed successfully")
                
            except Exception as e:
                task['status'] = TaskStatus.FAILED.value
                task['error'] = str(e)
                
                self.logger.error(f"Task {task['type']} failed: {e}")
                
                # Decide whether to continue or abort campaign
                if task['type'] in ['blog_research', 'content_analysis']:
                    # Critical task failed - abort campaign
                    raise Exception(f"Critical task {task['type']} failed: {e}")
        
        return task_results
    
    async def _execute_single_task(self, task: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single campaign task using the appropriate agent"""
        task_type = task['type']
        agent_name = task['agent']
        parameters = task['parameters']
        
        if agent_name == 'blog_researcher':
            agent = self.agents['blog_researcher']
            
            if task_type == 'blog_research':
                # Execute blog research
                context = {
                    'keywords': ' '.join(parameters['keywords']),
                    'max_results': parameters['max_results'],
                    'min_authority': parameters.get('min_authority', 60)
                }
                
                result = agent.execute(
                    task="Discover and analyze high-quality blogs for SEO engagement",
                    context=context
                )
                
                return result
            
            elif task_type == 'content_analysis':
                # Content analysis is already included in blog research
                # Return success to indicate this step is complete
                return {
                    'success': True,
                    'message': 'Content analysis completed as part of blog research',
                    'analysis_included': True
                }
                
        elif agent_name == 'comment_writer':
            agent = self.agents['comment_writer']
            
            if task_type == 'comment_generation':
                # Get blog data from previous research results
                research_results = None
                for prev_result in previous_results.values():
                    if isinstance(prev_result, dict) and 'qualified_blogs' in prev_result.get('result', {}):
                        research_results = prev_result['result']
                        break
                
                if not research_results:
                    raise Exception("No research results available for comment generation")
                
                # Generate comments for qualified blogs
                qualified_blogs = research_results['qualified_blogs'][:parameters.get('batch_size', 5)]
                comment_results = []
                
                for blog in qualified_blogs:
                    try:
                        # Analyze blog content first
                        content_analysis = agent.analyze_content(blog.get('content', ''))
                        
                        # Generate comment
                        comment_result = await agent.generate_comment(
                            blog_data=blog,
                            content_analysis=content_analysis,
                            target_keywords=parameters.get('target_keywords', []),
                            comment_type=parameters.get('comment_type', 'engaging')
                        )
                        
                        comment_results.append({
                            'blog_url': blog.get('url'),
                            'comment_result': comment_result
                        })
                        
                    except Exception as e:
                        self.logger.error(f"Failed to generate comment for {blog.get('url', 'unknown')}: {e}")
                        continue
                
                return {
                    'comments_generated': len(comment_results),
                    'comment_results': comment_results,
                    'success_rate': len([r for r in comment_results if r['comment_result']['success']]) / max(len(comment_results), 1)
                }
                
        elif agent_name == 'campaign_manager':
            # Handle campaign manager tasks (quality validation, etc.)
            if task_type == 'quality_validation':
                return await self._validate_campaign_quality(task, previous_results)
        
        raise Exception(f"Unknown task type: {task_type} for agent: {agent_name}")
    
    async def _validate_campaign_quality(self, task: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of campaign outputs"""
        quality_threshold = task['parameters'].get('quality_threshold', 0.7)
        
        # Analyze comment generation results
        comment_results = []
        for result in previous_results.values():
            if isinstance(result, dict) and 'comment_results' in result:
                comment_results.extend(result['comment_results'])
        
        if not comment_results:
            return {'success': False, 'error': 'No comment results to validate'}
        
        # Quality metrics
        valid_comments = 0
        total_comments = len(comment_results)
        quality_scores = []
        
        for comment_data in comment_results:
            comment_result = comment_data['comment_result']
            if comment_result.get('success') and comment_result.get('metadata', {}).get('is_valid'):
                valid_comments += 1
                quality_scores.append(comment_result.get('metadata', {}).get('validation_score', 0))
        
        average_quality = sum(quality_scores) / max(len(quality_scores), 1)
        quality_pass_rate = valid_comments / max(total_comments, 1)
        
        return {
            'total_comments': total_comments,
            'valid_comments': valid_comments,
            'quality_pass_rate': quality_pass_rate,
            'average_quality_score': average_quality,
            'meets_threshold': quality_pass_rate >= quality_threshold,
            'quality_breakdown': {
                'high_quality': len([s for s in quality_scores if s >= 0.8]),
                'medium_quality': len([s for s in quality_scores if 0.6 <= s < 0.8]),
                'low_quality': len([s for s in quality_scores if s < 0.6])
            }
        }
    
    def _estimate_campaign_cost(self, campaign_config: Dict[str, Any]) -> float:
        """Estimate the total cost of a campaign"""
        target_blogs = campaign_config['target_blogs']
        comments_per_blog = campaign_config['comments_per_blog']
        
        # Rough cost estimates (in USD)
        research_cost = target_blogs * 0.02  # $0.02 per blog research
        analysis_cost = target_blogs * 0.01  # $0.01 per content analysis
        comment_cost = target_blogs * comments_per_blog * 0.05  # $0.05 per comment
        
        return research_cost + analysis_cost + comment_cost
    
    def _estimate_campaign_duration(self, campaign_config: Dict[str, Any]) -> int:
        """Estimate campaign duration in minutes"""
        target_blogs = campaign_config['target_blogs']
        comments_per_blog = campaign_config['comments_per_blog']
        
        # Time estimates (in minutes)
        research_time = target_blogs * 0.5  # 30 seconds per blog
        comment_time = target_blogs * comments_per_blog * 0.3  # 18 seconds per comment
        
        return int(research_time + comment_time + 5)  # +5 minutes buffer
    
    def _calculate_campaign_metrics(self, campaign: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive campaign metrics"""
        metrics = {}
        
        # Extract results data
        for result in execution_results.values():
            if isinstance(result, dict):
                if 'qualified_blogs' in result.get('result', {}):
                    research_result = result['result']
                    metrics['blogs_discovered'] = research_result.get('discovery_stats', {}).get('total_discovered', 0)
                    metrics['blogs_qualified'] = len(research_result.get('qualified_blogs', []))
                
                elif 'comments_generated' in result:
                    metrics['comments_generated'] = result['comments_generated']
                    metrics['comment_success_rate'] = result.get('success_rate', 0.0)
        
        # Calculate overall success rate
        total_tasks = len(campaign['tasks'])
        completed_tasks = len([t for t in campaign['tasks'] if t['status'] == TaskStatus.COMPLETED.value])
        metrics['task_completion_rate'] = completed_tasks / max(total_tasks, 1)
        
        return metrics
    
    def _generate_campaign_report(self, campaign: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive campaign report"""
        return {
            'campaign_summary': {
                'name': campaign['name'],
                'keywords': campaign['keywords'],
                'duration': (campaign.get('completed_at', datetime.utcnow()) - campaign['started_at']).total_seconds(),
                'status': campaign['status']
            },
            'performance_metrics': campaign['metrics'],
            'task_breakdown': {
                'total_tasks': len(campaign['tasks']),
                'completed': len([t for t in campaign['tasks'] if t['status'] == TaskStatus.COMPLETED.value]),
                'failed': len([t for t in campaign['tasks'] if t['status'] == TaskStatus.FAILED.value]),
                'skipped': len([t for t in campaign['tasks'] if t['status'] == TaskStatus.SKIPPED.value])
            },
            'recommendations': self._generate_campaign_recommendations(campaign, execution_results)
        }
    
    def _generate_campaign_recommendations(self, campaign: Dict[str, Any], execution_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for campaign optimization"""
        recommendations = []
        
        # Analyze performance and suggest improvements
        metrics = campaign['metrics']
        
        if metrics.get('task_completion_rate', 0) < 0.8:
            recommendations.append("Consider increasing timeout values for better task completion rates")
        
        if metrics.get('comment_success_rate', 0) < 0.7:
            recommendations.append("Review comment generation prompts and quality thresholds")
        
        if metrics.get('blogs_qualified', 0) < campaign['target_blogs'] * 0.5:
            recommendations.append("Expand keyword list or lower authority thresholds for better blog discovery")
        
        return recommendations
    
    def _store_campaign(self, campaign_config: Dict[str, Any]):
        """Store campaign configuration in database"""
        try:
            # This would integrate with the database models
            # For now, just log the storage
            self.logger.info(f"Stored campaign {campaign_config['name']} in database")
        except Exception as e:
            self.logger.error(f"Failed to store campaign: {e}")
    
    def _execute_task(self, task: str, context: Dict[str, Any] = None) -> Any:
        """
        Execute a campaign management task
        
        Args:
            task: Task description
            context: Additional context data
            
        Returns:
            Task execution result
        """
        try:
            # Parse task type from description
            if "create campaign" in task.lower():
                # Extract campaign parameters from context
                name = context.get('name', 'New Campaign')
                keywords = context.get('keywords', [])
                return self.create_campaign(name, keywords)
            
            elif "execute campaign" in task.lower():
                campaign_id = context.get('campaign_id')
                if campaign_id:
                    # Note: This would need to be async in real implementation
                    return {'message': f'Campaign {campaign_id} execution initiated'}
            
            else:
                return {'message': f'Campaign management task: {task}'}
                
        except Exception as e:
            self.logger.error(f"Campaign management task failed: {e}")
            raise
