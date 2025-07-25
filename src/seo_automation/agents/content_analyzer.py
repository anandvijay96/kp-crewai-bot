"""
ContentAnalyzer Agent for SEO Automation

This agent analyzes blog post content to understand context and identify 
engagement opportunities for comment placement.
"""

from typing import Any, Dict, List, Optional
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent
from ..utils.database import BlogPost, db_manager


class ContentExtractionTool(BaseTool):
    """Tool for extracting and parsing blog post content."""
    
    name: str = "content_extraction_tool"
    description: str = "Extracts and parses blog post content, metadata, and structure"
    
    def _run(self, url: str) -> Dict[str, Any]:
        """Extract content from a blog post URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            title_selectors = ['h1', 'title', '.post-title', '.entry-title', '.article-title']
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    break
                    
            # Extract main content
            content = ""
            content_selectors = [
                '.post-content', '.entry-content', '.article-content',
                '.content', 'main', 'article', '.post-body'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text().strip()
                    break
            
            # If no content found, try to get all paragraph text
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])
            
            # Extract metadata
            meta_description = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_description = meta_tag.get('content', '')
            
            # Extract author
            author = ""
            author_selectors = ['.author', '.post-author', '.entry-author', '[rel="author"]']
            for selector in author_selectors:
                element = soup.select_one(selector)
                if element:
                    author = element.get_text().strip()
                    break
            
            # Extract publication date
            pub_date = ""
            date_selectors = ['.post-date', '.entry-date', '.published', 'time']
            for selector in date_selectors:
                element = soup.select_one(selector)
                if element:
                    pub_date = element.get_text().strip()
                    break
            
            # Check for comments section
            has_comments = bool(soup.find(class_=re.compile(r'comment', re.I))) or \
                          bool(soup.find(id=re.compile(r'comment', re.I)))
            
            # Extract tags/categories
            tags = []
            tag_selectors = ['.tags', '.post-tags', '.entry-tags', '.categories']
            for selector in tag_selectors:
                elements = soup.select(f'{selector} a')
                for element in elements:
                    tags.append(element.get_text().strip())
            
            return {
                'url': url,
                'title': title or 'No title found',
                'content': content[:5000],  # Limit content length
                'meta_description': meta_description,
                'author': author,
                'publication_date': pub_date,
                'has_comments': has_comments,
                'tags': tags[:10],  # Limit tags
                'word_count': len(content.split()),
                'extracted_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Content extraction failed for {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'extracted_at': datetime.utcnow().isoformat()
            }


class TopicAnalysisTool(BaseTool):
    """Tool for analyzing content topics and themes."""
    
    name: str = "topic_analysis_tool"
    description: str = "Analyzes content to identify main topics, themes, and keywords"
    
    def _run(self, content: str) -> Dict[str, Any]:
        """Analyze content topics and extract key themes."""
        try:
            if not content:
                return {'error': 'No content provided for analysis'}
            
            # Simple keyword extraction (can be enhanced with NLP libraries)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
            
            # Common stop words to filter out
            stop_words = {
                'the', 'and', 'are', 'for', 'not', 'but', 'can', 'you', 'all',
                'any', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'has',
                'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two',
                'who', 'boy', 'did', 'get', 'him', 'man', 'oil', 'sit', 'too',
                'use', 'way', 'will', 'that', 'this', 'have', 'with', 'they',
                'from', 'been', 'more', 'than', 'what', 'when', 'your', 'them'
            }
            
            # Filter out stop words and count frequency
            filtered_words = [word for word in words if word not in stop_words]
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            
            # Identify tech-related terms
            tech_terms = [
                'cloud', 'devops', 'kubernetes', 'docker', 'aws', 'azure', 'gcp',
                'microservices', 'api', 'database', 'security', 'automation',
                'deployment', 'monitoring', 'infrastructure', 'server', 'application',
                'software', 'development', 'programming', 'technology', 'platform'
            ]
            
            found_tech_terms = [term for term in tech_terms if term in content.lower()]
            
            # Basic sentiment analysis (simple approach)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'best', 'love', 'perfect']
            negative_words = ['bad', 'terrible', 'awful', 'worst', 'hate', 'horrible', 'poor']
            
            positive_count = sum(1 for word in positive_words if word in content.lower())
            negative_count = sum(1 for word in negative_words if word in content.lower())
            
            sentiment = 'neutral'
            if positive_count > negative_count:
                sentiment = 'positive'
            elif negative_count > positive_count:
                sentiment = 'negative'
            
            # Identify discussion points (questions, controversial statements)
            questions = re.findall(r'[^.!?]*\?[^.!?]*', content)
            
            return {
                'top_keywords': [{'word': word, 'frequency': freq} for word, freq in top_keywords],
                'tech_terms_found': found_tech_terms,
                'sentiment': sentiment,
                'sentiment_scores': {
                    'positive': positive_count,
                    'negative': negative_count
                },
                'questions_found': len(questions),
                'discussion_points': questions[:5],  # First 5 questions
                'word_count': len(filtered_words),
                'readability_score': self._calculate_readability(content),
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Topic analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_readability(self, content: str) -> float:
        """Simple readability score calculation."""
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        # Simple readability score (lower is more readable)
        readability = avg_sentence_length / 20.0
        return min(readability, 1.0)


class CommentOpportunityTool(BaseTool):
    """Tool for identifying comment opportunities in content."""
    
    name: str = "comment_opportunity_tool"
    description: str = "Identifies potential comment opportunities and engagement points"
    
    def _run(self, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for comment opportunities."""
        try:
            opportunities = []
            
            # Check for questions
            if content_analysis.get('questions_found', 0) > 0:
                opportunities.append({
                    'type': 'question_response',
                    'priority': 'high',
                    'description': 'Blog post contains questions that can be answered',
                    'count': content_analysis.get('questions_found', 0)
                })
            
            # Check for tech terms (relevant to KloudPortal)
            tech_terms = content_analysis.get('tech_terms_found', [])
            if tech_terms:
                opportunities.append({
                    'type': 'technical_insight',
                    'priority': 'high',
                    'description': f'Blog discusses relevant tech topics: {", ".join(tech_terms[:3])}',
                    'terms': tech_terms
                })
            
            # Check sentiment for engagement potential
            sentiment = content_analysis.get('sentiment', 'neutral')
            if sentiment == 'positive':
                opportunities.append({
                    'type': 'positive_reinforcement',
                    'priority': 'medium',
                    'description': 'Positive sentiment allows for supportive comments'
                })
            elif sentiment == 'negative':
                opportunities.append({
                    'type': 'solution_offering',
                    'priority': 'high',
                    'description': 'Negative sentiment creates opportunity to offer solutions'
                })
            
            # Check readability for engagement potential
            readability = content_analysis.get('readability_score', 0.5)
            if readability < 0.5:  # More readable content
                opportunities.append({
                    'type': 'accessible_discussion',
                    'priority': 'medium',
                    'description': 'Content is accessible, good for general discussion'
                })
            
            # Calculate overall comment worthiness score
            score = 0
            if content_analysis.get('questions_found', 0) > 0:
                score += 30
            if tech_terms:
                score += 25
            if sentiment == 'positive':
                score += 15
            elif sentiment == 'negative':
                score += 20
            if readability < 0.5:
                score += 10
            
            # Additional scoring factors
            word_count = content_analysis.get('word_count', 0)
            if word_count > 500:  # Substantial content
                score += 10
            
            return {
                'opportunities': opportunities,
                'comment_worthiness_score': min(score, 100),
                'recommendation': self._get_recommendation(score),
                'engagement_potential': 'high' if score >= 60 else 'medium' if score >= 30 else 'low',
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Comment opportunity analysis failed: {e}")
            return {'error': str(e)}
    
    def _get_recommendation(self, score: int) -> str:
        """Get recommendation based on comment worthiness score."""
        if score >= 70:
            return "Highly recommended for commenting - excellent engagement potential"
        elif score >= 50:
            return "Good commenting opportunity - proceed with quality comment"
        elif score >= 30:
            return "Moderate opportunity - consider if resources allow"
        else:
            return "Low priority - focus on higher-scoring opportunities"


class ContentAnalyzer(BaseAgent):
    """
    ContentAnalyzer Agent for analyzing blog post content and identifying
    engagement opportunities.
    """
    
    def __init__(self):
        tools = [
            ContentExtractionTool(),
            TopicAnalysisTool(),
            CommentOpportunityTool()
        ]
        
        super().__init__(
            name="ContentAnalyzer",
            role="Blog Content Analysis Specialist",
            goal="Analyze blog post content to understand context, extract key topics, and identify valuable engagement opportunities for strategic commenting",
            backstory="""You are an expert content analyst specializing in blog post evaluation 
            for SEO and engagement purposes. You excel at extracting meaningful insights from 
            web content, identifying discussion opportunities, and assessing the potential value 
            of commenting on specific posts. Your analysis helps determine the best blogs and 
            posts for KloudPortal's thought leadership and community engagement efforts.""",
            tools=tools
        )
    
    def _execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute content analysis task."""
        try:
            url = context.get('url') if context else None
            if not url:
                # Try to extract URL from task description
                import re
                url_match = re.search(r'https?://[^\s]+', task)
                if url_match:
                    url = url_match.group()
            
            if not url:
                raise ValueError("No URL provided for content analysis")
            
            self.logger.info(f"Starting content analysis for URL: {url}")
            
            # Step 1: Extract content
            content_tool = ContentExtractionTool()
            content_data = content_tool._run(url)
            
            if 'error' in content_data:
                raise Exception(f"Content extraction failed: {content_data['error']}")
            
            self.logger.info(f"Extracted content: {len(content_data.get('content', ''))} characters")
            
            # Step 2: Analyze topics and themes
            topic_tool = TopicAnalysisTool()
            topic_analysis = topic_tool._run(content_data.get('content', ''))
            
            if 'error' in topic_analysis:
                self.logger.warning(f"Topic analysis failed: {topic_analysis['error']}")
                topic_analysis = {}
            
            # Step 3: Identify comment opportunities
            opportunity_tool = CommentOpportunityTool()
            opportunities = opportunity_tool._run(topic_analysis)
            
            if 'error' in opportunities:
                self.logger.warning(f"Opportunity analysis failed: {opportunities['error']}")
                opportunities = {'opportunities': [], 'comment_worthiness_score': 0}
            
            # Step 4: Store analysis in database
            analysis_result = {
                'url': url,
                'content_data': content_data,
                'topic_analysis': topic_analysis,
                'opportunities': opportunities,
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
            self._store_analysis(analysis_result)
            
            # Prepare summary for response
            summary = {
                'url': url,
                'title': content_data.get('title', 'Unknown'),
                'word_count': content_data.get('word_count', 0),
                'has_comments': content_data.get('has_comments', False),
                'top_keywords': [kw['word'] for kw in topic_analysis.get('top_keywords', [])[:5]],
                'tech_terms': topic_analysis.get('tech_terms_found', []),
                'sentiment': topic_analysis.get('sentiment', 'neutral'),
                'questions_found': topic_analysis.get('questions_found', 0),
                'comment_worthiness_score': opportunities.get('comment_worthiness_score', 0),
                'engagement_potential': opportunities.get('engagement_potential', 'low'),
                'recommendation': opportunities.get('recommendation', 'No recommendation available'),
                'opportunities_count': len(opportunities.get('opportunities', []))
            }
            
            self.logger.info(f"Content analysis completed. Score: {summary['comment_worthiness_score']}/100")
            
            return {
                'analysis_summary': summary,
                'full_analysis': analysis_result,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            raise
    
    def _store_analysis(self, analysis_result: Dict[str, Any]):
        """Store content analysis results in database."""
        try:
            session = db_manager.get_session()
            
            # Create or update blog post record
            blog_post = BlogPost(
                url=analysis_result['url'],
                title=analysis_result['content_data'].get('title'),
                content_summary=analysis_result['content_data'].get('meta_description', '')[:500],
                author=analysis_result['content_data'].get('author'),
                publication_date=analysis_result['content_data'].get('publication_date'),
                word_count=analysis_result['content_data'].get('word_count', 0),
                has_comments=analysis_result['content_data'].get('has_comments', False),
                tags=analysis_result['content_data'].get('tags', []),
                comment_worthiness_score=analysis_result['opportunities'].get('comment_worthiness_score', 0),
                engagement_potential=analysis_result['opportunities'].get('engagement_potential', 'low'),
                analysis_data=analysis_result,
                analyzed_at=datetime.utcnow(),
                status='analyzed'
            )
            
            session.add(blog_post)
            session.commit()
            
            self.logger.info(f"Stored analysis for {analysis_result['url']}")
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis: {e}")
            # Don't raise exception here as analysis was successful
    
    def analyze_multiple_posts(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple blog posts and return results."""
        results = []
        
        for url in urls:
            try:
                result = self.execute(
                    f"Analyze blog post content for engagement opportunities: {url}",
                    context={'url': url}
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to analyze {url}: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all content analyses performed."""
        try:
            session = db_manager.get_session()
            
            blog_posts = session.query(BlogPost).filter_by(status='analyzed').all()
            
            if not blog_posts:
                return {'message': 'No analyzed blog posts found'}
            
            # Calculate statistics
            total_posts = len(blog_posts)
            avg_score = sum(post.comment_worthiness_score or 0 for post in blog_posts) / total_posts
            high_potential = sum(1 for post in blog_posts if (post.comment_worthiness_score or 0) >= 70)
            
            engagement_distribution = {}
            for post in blog_posts:
                potential = post.engagement_potential or 'unknown'
                engagement_distribution[potential] = engagement_distribution.get(potential, 0) + 1
            
            return {
                'total_analyzed_posts': total_posts,
                'average_worthiness_score': round(avg_score, 2),
                'high_potential_posts': high_potential,
                'engagement_distribution': engagement_distribution,
                'recent_analyses': [
                    {
                        'url': post.url,
                        'title': post.title,
                        'score': post.comment_worthiness_score,
                        'potential': post.engagement_potential
                    }
                    for post in sorted(blog_posts, key=lambda x: x.analyzed_at, reverse=True)[:5]
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis summary: {e}")
            return {'error': str(e)}
