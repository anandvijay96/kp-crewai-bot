"""
Comment Service
===============

Service layer for comment generation and management with database integration.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.comment import Comment, CommentStatus, CommentGeneration
from ..models.user import User
from ...seo_automation.utils.database import db_manager

logger = logging.getLogger(__name__)

class CommentService:
    """Service for managing comment generation and quality assessment."""
    
    @staticmethod
    def generate_comments(
        generation_params: Dict[str, Any], 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Generate comments using AI agent.
        
        Args:
            generation_params: Comment generation parameters
            user_id: ID of the user requesting generation
            
        Returns:
            Dict containing generated comments and metadata
        """
        try:
            # Import agent dynamically to handle import errors gracefully
            from ...seo_automation.agents.comment_writer_agent import CommentWriterAgent
            
            logger.info(f"Starting comment generation for user {user_id}")
            
            # Initialize agent
            agent = CommentWriterAgent()
            
            # Execute comment generation
            start_time = datetime.utcnow()
            agent_result = agent.generate_comments(generation_params)
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Create generation session record
            with db_manager.get_session() as session:
                generation_session = CommentGeneration(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    blog_url=generation_params.get('blog_url', ''),
                    style=generation_params.get('style', 'engaging'),
                    tone=generation_params.get('tone', 'professional'),
                    parameters=generation_params,
                    status='completed',
                    execution_time=execution_time,
                    cost=agent_result.get('cost', 0.0),
                    created_at=start_time,
                    completed_at=end_time
                )
                
                session.add(generation_session)
                session.commit()
                session.refresh(generation_session)
                
                # Store generated comments
                generated_comments = []
                if agent_result and 'comments' in agent_result:
                    for comment_data in agent_result['comments']:
                        comment = Comment(
                            id=str(uuid.uuid4()),
                            generation_id=generation_session.id,
                            blog_url=generation_params.get('blog_url', ''),
                            content=comment_data.get('content', ''),
                            style=comment_data.get('style', generation_params.get('style', 'engaging')),
                            tone=comment_data.get('tone', generation_params.get('tone', 'professional')),
                            quality_score=comment_data.get('quality_score', 0.0),
                            relevance_score=comment_data.get('relevance_score', 0.0),
                            engagement_score=comment_data.get('engagement_score', 0.0),
                            word_count=len(comment_data.get('content', '').split()),
                            status=CommentStatus.GENERATED,
                            generated_at=datetime.utcnow()
                        )
                        
                        session.add(comment)
                        generated_comments.append(CommentService._comment_to_dict(comment))
                
                session.commit()
                
                result = {
                    'generation_session_id': generation_session.id,
                    'comments': generated_comments,
                    'total_generated': len(generated_comments),
                    'high_quality': len([c for c in generated_comments if c['quality_score'] >= 0.8]),
                    'blog_url': generation_params.get('blog_url', ''),
                    'style': generation_params.get('style', 'engaging'),
                    'tone': generation_params.get('tone', 'professional'),
                    'execution_time': execution_time,
                    'cost': agent_result.get('cost', 0.0),
                    'parameters': generation_params
                }
                
                logger.info(f"Comment generation completed: {len(generated_comments)} comments generated")
                return result
                
        except ImportError as e:
            logger.warning(f"Comment generation agent not available: {e}")
            return CommentService._create_mock_generation_result(generation_params, user_id)
        except Exception as e:
            logger.error(f"Comment generation failed: {e}")
            raise

    @staticmethod
    def get_generation_history(
        user_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get comment generation history for a user.
        
        Args:
            user_id: User ID
            page: Page number
            page_size: Items per page
            
        Returns:
            Dict containing generation sessions and pagination
        """
        try:
            with db_manager.get_session() as session:
                query = session.query(CommentGeneration).filter(
                    CommentGeneration.user_id == user_id
                )
                
                total = query.count()
                
                sessions = query.order_by(CommentGeneration.created_at.desc()).offset(
                    (page - 1) * page_size
                ).limit(page_size).all()
                
                session_list = [
                    CommentService._generation_session_to_dict(session_obj)
                    for session_obj in sessions
                ]
                
                return {
                    'generation_sessions': session_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'pages': (total + page_size - 1) // page_size
                }
                
        except Exception as e:
            logger.error(f"Failed to get generation history: {e}")
            raise

    @staticmethod
    def get_generated_comments(
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        blog_url_filter: Optional[str] = None,
        min_quality: Optional[float] = None,
        status_filter: Optional[CommentStatus] = None
    ) -> Dict[str, Any]:
        """
        Get generated comments for a user with filtering.
        
        Args:
            user_id: User ID
            page: Page number
            page_size: Items per page
            blog_url_filter: Optional blog URL filter
            min_quality: Minimum quality score
            status_filter: Comment status filter
            
        Returns:
            Dict containing comments and pagination info
        """
        try:
            with db_manager.get_session() as session:
                # Join with CommentGeneration to filter by user
                query = session.query(Comment).join(CommentGeneration).filter(
                    CommentGeneration.user_id == user_id
                )
                
                if blog_url_filter:
                    query = query.filter(Comment.blog_url.ilike(f'%{blog_url_filter}%'))
                
                if min_quality:
                    query = query.filter(Comment.quality_score >= min_quality)
                
                if status_filter:
                    query = query.filter(Comment.status == status_filter)
                
                total = query.count()
                
                comments = query.order_by(Comment.generated_at.desc()).offset(
                    (page - 1) * page_size
                ).limit(page_size).all()
                
                comment_list = [
                    CommentService._comment_to_dict(comment)
                    for comment in comments
                ]
                
                return {
                    'comments': comment_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'pages': (total + page_size - 1) // page_size
                }
                
        except Exception as e:
            logger.error(f"Failed to get generated comments: {e}")
            raise

    @staticmethod
    def get_comment_details(comment_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific comment.
        
        Args:
            comment_id: Comment identifier
            user_id: User ID for ownership check
            
        Returns:
            Comment details or None if not found
        """
        try:
            with db_manager.get_session() as session:
                comment = session.query(Comment).join(CommentGeneration).filter(
                    and_(
                        Comment.id == comment_id,
                        CommentGeneration.user_id == user_id
                    )
                ).first()
                
                if not comment:
                    return None
                
                return CommentService._comment_to_dict(comment, include_full_details=True)
                
        except Exception as e:
            logger.error(f"Failed to get comment details: {e}")
            raise

    @staticmethod
    def review_comment(
        comment_id: str, 
        user_id: int, 
        review_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Review and update comment quality scores.
        
        Args:
            comment_id: Comment identifier
            user_id: User ID for ownership check
            review_data: Review data including scores and feedback
            
        Returns:
            Updated comment data
        """
        try:
            with db_manager.get_session() as session:
                comment = session.query(Comment).join(CommentGeneration).filter(
                    and_(
                        Comment.id == comment_id,
                        CommentGeneration.user_id == user_id
                    )
                ).first()
                
                if not comment:
                    raise ValueError("Comment not found")
                
                # Update quality scores and status
                if 'quality_score' in review_data:
                    comment.quality_score = review_data['quality_score']
                
                if 'relevance_score' in review_data:
                    comment.relevance_score = review_data['relevance_score']
                
                if 'engagement_score' in review_data:
                    comment.engagement_score = review_data['engagement_score']
                
                if 'feedback' in review_data:
                    comment.feedback = review_data['feedback']
                
                # Update status based on review
                if review_data.get('approved', False):
                    comment.status = CommentStatus.APPROVED
                elif review_data.get('rejected', False):
                    comment.status = CommentStatus.REJECTED
                else:
                    comment.status = CommentStatus.REVIEWED
                
                comment.reviewed_at = datetime.utcnow()
                
                session.commit()
                session.refresh(comment)
                
                logger.info(f"Comment reviewed successfully: {comment_id}")
                
                return CommentService._comment_to_dict(comment)
                
        except Exception as e:
            logger.error(f"Failed to review comment {comment_id}: {e}")
            raise

    @staticmethod
    def get_comment_analytics(user_id: int) -> Dict[str, Any]:
        """
        Get analytics for user's comment generation activities.
        
        Args:
            user_id: User ID
            
        Returns:
            Comment analytics data
        """
        try:
            with db_manager.get_session() as session:
                # Get generation sessions
                sessions = session.query(CommentGeneration).filter(
                    CommentGeneration.user_id == user_id
                ).all()
                
                # Get generated comments
                comments = session.query(Comment).join(CommentGeneration).filter(
                    CommentGeneration.user_id == user_id
                ).all()
                
                # Calculate analytics
                total_sessions = len(sessions)
                total_comments = len(comments)
                total_cost = sum(s.cost for s in sessions if s.cost)
                avg_execution_time = sum(s.execution_time for s in sessions if s.execution_time) / max(total_sessions, 1)
                
                # Quality distribution
                quality_scores = [c.quality_score for c in comments if c.quality_score]
                high_quality = len([q for q in quality_scores if q >= 0.8])
                medium_quality = len([q for q in quality_scores if 0.6 <= q < 0.8])
                low_quality = len([q for q in quality_scores if q < 0.6])
                
                # Status distribution
                status_counts = {}
                for comment in comments:
                    status = comment.status.value if comment.status else 'unknown'
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Style analysis
                style_counts = {}
                for comment in comments:
                    style = comment.style or 'unknown'
                    style_counts[style] = style_counts.get(style, 0) + 1
                
                analytics = {
                    'overview': {
                        'total_generation_sessions': total_sessions,
                        'total_comments_generated': total_comments,
                        'total_cost': total_cost,
                        'average_execution_time': avg_execution_time,
                        'average_comments_per_session': total_comments / max(total_sessions, 1)
                    },
                    'quality_distribution': {
                        'high_quality': high_quality,
                        'medium_quality': medium_quality,
                        'low_quality': low_quality,
                        'average_quality': sum(quality_scores) / max(len(quality_scores), 1)
                    },
                    'status_distribution': status_counts,
                    'style_distribution': style_counts,
                    'recent_activity': [
                        CommentService._generation_session_to_dict(s)
                        for s in sorted(sessions, key=lambda x: x.created_at, reverse=True)[:5]
                    ]
                }
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get comment analytics: {e}")
            raise

    @staticmethod
    def _create_mock_generation_result(generation_params: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create mock generation result when agent is not available."""
        mock_comments = [
            {
                'id': str(uuid.uuid4()),
                'content': 'Great insights on SEO best practices! I particularly found the section on technical SEO optimization very helpful. Have you considered discussing the impact of Core Web Vitals on ranking factors?',
                'style': generation_params.get('style', 'engaging'),
                'tone': generation_params.get('tone', 'professional'),
                'quality_score': 0.87,
                'relevance_score': 0.91,
                'engagement_score': 0.84,
                'word_count': 35,
                'status': 'generated',
                'generated_at': datetime.utcnow().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'content': 'This article provides excellent actionable advice for SEO practitioners. The data-driven approach you\'ve taken really helps validate the strategies. Would love to see a follow-up on local SEO implementation.',
                'style': generation_params.get('style', 'engaging'),
                'tone': generation_params.get('tone', 'professional'),
                'quality_score': 0.89,
                'relevance_score': 0.93,
                'engagement_score': 0.86,
                'word_count': 37,
                'status': 'generated',
                'generated_at': datetime.utcnow().isoformat()
            }
        ]
        
        return {
            'generation_session_id': str(uuid.uuid4()),
            'comments': mock_comments,
            'total_generated': len(mock_comments),
            'high_quality': len(mock_comments),
            'blog_url': generation_params.get('blog_url', ''),
            'style': generation_params.get('style', 'engaging'),
            'tone': generation_params.get('tone', 'professional'),
            'execution_time': 1.8,
            'cost': 0.12,
            'parameters': generation_params,
            'note': 'Mock data - comment generation agent not available'
        }

    @staticmethod
    def _comment_to_dict(comment: Comment, include_full_details: bool = False) -> Dict[str, Any]:
        """Convert Comment model to dictionary."""
        data = {
            'id': comment.id,
            'blog_url': comment.blog_url,
            'content': comment.content,
            'style': comment.style,
            'tone': comment.tone,
            'quality_score': comment.quality_score,
            'relevance_score': comment.relevance_score,
            'engagement_score': comment.engagement_score,
            'word_count': comment.word_count,
            'status': comment.status.value if comment.status else 'generated',
            'generated_at': comment.generated_at.isoformat() if comment.generated_at else None
        }
        
        if include_full_details:
            data.update({
                'feedback': comment.feedback,
                'reviewed_at': comment.reviewed_at.isoformat() if comment.reviewed_at else None,
                'generation_id': comment.generation_id
            })
        
        return data

    @staticmethod
    def _generation_session_to_dict(session: CommentGeneration) -> Dict[str, Any]:
        """Convert CommentGeneration model to dictionary."""
        return {
            'id': session.id,
            'blog_url': session.blog_url,
            'style': session.style,
            'tone': session.tone,
            'parameters': session.parameters,
            'status': session.status,
            'execution_time': session.execution_time,
            'cost': session.cost,
            'created_at': session.created_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        }
