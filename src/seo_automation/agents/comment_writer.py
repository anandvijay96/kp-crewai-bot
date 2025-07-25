"""
CommentWriter Agent - Generates contextual and engaging blog comments

This agent specializes in creating high-quality comments that:
- Are contextual and relevant to the blog content
- Add genuine value to the discussion
- Include strategic keyword integration
- Maintain brand voice and safety standards
- Optimize for engagement and SEO impact
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from crewai import Agent
from ..utils.database import DatabaseManager
from .base_agent import BaseAgent


class CommentWriter(BaseAgent):
    """
    Specialized agent for generating high-quality blog comments
    
    Capabilities:
    - Contextual comment generation based on content analysis
    - Strategic keyword integration
    - Brand voice consistency
    - Engagement optimization
    - Comment length and tone adaptation
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the CommentWriter agent"""
        super().__init__(config)
        self.agent_type = "comment_writer"
        self.logger = logging.getLogger(f"{__name__}.CommentWriter")
        
        # Comment generation parameters
        self.max_comment_length = config.get('max_comment_length', 500) if config else 500
        self.min_comment_length = config.get('min_comment_length', 50) if config else 50
        self.keyword_density_target = config.get('keyword_density_target', 0.02) if config else 0.02
        
        # Brand voice settings
        self.brand_voice = config.get('brand_voice', 'professional_friendly') if config else 'professional_friendly'
        self.company_name = config.get('company_name', 'KnowladgePoint') if config else 'KnowladgePoint'
        self.expertise_areas = config.get('expertise_areas', [
            'SEO', 'Digital Marketing', 'Content Strategy', 'Technical SEO', 'Analytics'
        ]) if config else ['SEO', 'Digital Marketing', 'Content Strategy', 'Technical SEO', 'Analytics']
        
        self.agent = self._create_crewai_agent()
    
    def _create_crewai_agent(self) -> Agent:
        """Create and configure the CrewAI agent"""
        return Agent(
            role="Expert Comment Writer",
            goal=f"""Generate high-quality, contextual blog comments that add genuine value 
                     while strategically promoting {self.company_name}'s expertise in digital marketing and SEO""",
            backstory=f"""You are a senior digital marketing strategist at {self.company_name} with deep expertise 
                        in SEO, content marketing, and online engagement. You excel at crafting comments that 
                        genuinely contribute to discussions while subtly showcasing your company's knowledge and 
                        building authentic relationships with potential clients.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3,
            memory=True
        )
    
    async def generate_comment(
        self, 
        blog_data: Dict[str, Any], 
        content_analysis: Dict[str, Any],
        target_keywords: List[str] = None,
        comment_type: str = "engaging"
    ) -> Dict[str, Any]:
        """
        Generate a contextual comment for a blog post
        
        Args:
            blog_data: Blog information (title, content, author, etc.)
            content_analysis: Analysis results from ContentAnalyzer
            target_keywords: Keywords to strategically include
            comment_type: Type of comment (engaging, question, insight, etc.)
            
        Returns:
            Dict containing the generated comment and metadata
        """
        task_start_time = datetime.now()
        
        try:
            # Extract key information
            blog_title = blog_data.get('title', '')
            blog_content = blog_data.get('content', '')
            blog_url = blog_data.get('url', '')
            
            # Get analysis insights
            relevance_score = content_analysis.get('relevance_score', 0)
            key_topics = content_analysis.get('key_topics', [])
            comment_opportunities = content_analysis.get('comment_opportunities', [])
            
            # Prepare comment generation prompt
            comment_prompt = self._build_comment_prompt(
                blog_title, blog_content, key_topics, 
                comment_opportunities, target_keywords, comment_type
            )
            
            # Generate comment using CrewAI agent
            comment_result = await self.execute_task(
                agent=self.agent,
                task_description=comment_prompt,
                expected_output="A well-crafted comment that adds value to the discussion"
            )
            
            if not comment_result.get('success'):
                raise Exception(f"Comment generation failed: {comment_result.get('error')}")
            
            generated_comment = comment_result['result']
            
            # Post-process and validate comment
            processed_comment = self._process_comment(generated_comment, target_keywords)
            validation_result = self._validate_comment(processed_comment, blog_content)
            
            # Calculate metrics
            keyword_density = self._calculate_keyword_density(processed_comment, target_keywords or [])
            
            result = {
                'success': True,
                'comment': processed_comment,
                'metadata': {
                    'comment_type': comment_type,
                    'length': len(processed_comment),
                    'keyword_density': keyword_density,
                    'relevance_score': relevance_score,
                    'validation_score': validation_result['score'],
                    'validation_issues': validation_result['issues'],
                    'target_keywords': target_keywords or [],
                    'key_topics_addressed': key_topics[:3],
                    'generation_time': (datetime.now() - task_start_time).total_seconds()
                }
            }
            
            # Log to database
            await self._log_comment_generation(blog_url, result)
            
            return result
            
        except Exception as e:
            error_msg = f"Comment generation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return {
                'success': False,
                'error': error_msg,
                'comment': None,
                'metadata': {
                    'generation_time': (datetime.now() - task_start_time).total_seconds()
                }
            }
    
    def _build_comment_prompt(
        self, 
        title: str, 
        content: str, 
        key_topics: List[str],
        opportunities: List[Dict],
        keywords: List[str],
        comment_type: str
    ) -> str:
        """Build a comprehensive prompt for comment generation"""
        
        # Truncate content for prompt efficiency
        content_excerpt = content[:2000] + "..." if len(content) > 2000 else content
        
        prompt = f"""
Generate a high-quality blog comment for the following post:

BLOG POST DETAILS:
Title: {title}
Content: {content_excerpt}

KEY TOPICS IDENTIFIED: {', '.join(key_topics[:5])}

COMMENT OPPORTUNITIES: {json.dumps(opportunities[:3], indent=2)}

TARGET KEYWORDS: {', '.join(keywords or [])}

COMMENT TYPE: {comment_type}

REQUIREMENTS:
1. Length: {self.min_comment_length}-{self.max_comment_length} characters
2. Brand Voice: {self.brand_voice}
3. Company: {self.company_name} (mention subtly if relevant)
4. Expertise Areas: {', '.join(self.expertise_areas)}

GUIDELINES:
- Add genuine value to the discussion
- Be conversational and engaging
- Include relevant personal insights or experiences
- Ask thoughtful follow-up questions when appropriate
- Naturally integrate target keywords (avoid keyword stuffing)
- Maintain professionalism while being approachable
- Reference specific points from the article
- Offer additional resources or perspectives when relevant

AVOID:
- Generic or templated responses
- Over-promotion of services
- Keyword stuffing
- Controversial or polarizing statements
- Criticism without constructive alternatives

Generate a comment that would make the blog author and readers genuinely appreciate the contribution:
"""
        return prompt
    
    def _process_comment(self, raw_comment: str, keywords: List[str] = None) -> str:
        """Process and clean the generated comment"""
        # Remove any unwanted formatting
        comment = re.sub(r'\n+', ' ', raw_comment.strip())
        comment = re.sub(r'\s+', ' ', comment)
        
        # Ensure proper punctuation
        if not comment.endswith(('.', '!', '?')):
            comment += '.'
        
        # Capitalize first letter
        if comment:
            comment = comment[0].upper() + comment[1:]
        
        # Check length constraints
        if len(comment) > self.max_comment_length:
            # Truncate at last complete sentence within limit
            truncated = comment[:self.max_comment_length]
            last_sentence_end = max(
                truncated.rfind('.'),
                truncated.rfind('!'),
                truncated.rfind('?')
            )
            if last_sentence_end > self.min_comment_length:
                comment = truncated[:last_sentence_end + 1]
        
        return comment
    
    def _validate_comment(self, comment: str, blog_content: str) -> Dict[str, Any]:
        """Validate the generated comment for quality and appropriateness"""
        issues = []
        score = 100
        
        # Length validation
        if len(comment) < self.min_comment_length:
            issues.append(f"Comment too short ({len(comment)} chars)")
            score -= 20
        elif len(comment) > self.max_comment_length:
            issues.append(f"Comment too long ({len(comment)} chars)")
            score -= 10
        
        # Generic phrases detection
        generic_phrases = [
            "great post", "nice article", "thanks for sharing",
            "very informative", "good points", "i agree"
        ]
        
        comment_lower = comment.lower()
        generic_count = sum(1 for phrase in generic_phrases if phrase in comment_lower)
        if generic_count > 2:
            issues.append("Comment appears too generic")
            score -= 15
        
        # Keyword stuffing check
        words = comment.lower().split()
        for word in set(words):
            if words.count(word) > 3 and len(word) > 4:
                issues.append(f"Potential keyword stuffing: '{word}'")
                score -= 10
        
        # Spam indicators
        spam_indicators = [
            r'http[s]?://', r'www\.', r'\.com', r'click here',
            r'visit our', r'check out our', r'our website'
        ]
        
        for pattern in spam_indicators:
            if re.search(pattern, comment_lower):
                issues.append("Contains potential spam indicators")
                score -= 25
                break
        
        return {
            'score': max(0, score),
            'issues': issues,
            'is_valid': score >= 70
        }
    
    def _calculate_keyword_density(self, comment: str, keywords: List[str]) -> float:
        """Calculate keyword density in the comment"""
        if not keywords:
            return 0.0
        
        comment_words = comment.lower().split()
        total_words = len(comment_words)
        
        if total_words == 0:
            return 0.0
        
        keyword_count = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Count both single words and phrases
            if ' ' in keyword_lower:
                keyword_count += comment.lower().count(keyword_lower)
            else:
                keyword_count += comment_words.count(keyword_lower)
        
        return keyword_count / total_words
    
    async def generate_comment_variants(
        self,
        blog_data: Dict[str, Any],
        content_analysis: Dict[str, Any],
        variant_count: int = 3,
        target_keywords: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple comment variants for A/B testing"""
        
        comment_types = ["engaging", "question", "insight", "experience"]
        variants = []
        
        for i in range(min(variant_count, len(comment_types))):
            comment_type = comment_types[i]
            variant = await self.generate_comment(
                blog_data, content_analysis, target_keywords, comment_type
            )
            
            if variant['success']:
                variant['metadata']['variant_id'] = i + 1
                variant['metadata']['variant_type'] = comment_type
                variants.append(variant)
        
        return variants
    
    async def _log_comment_generation(self, blog_url: str, result: Dict[str, Any]):
        """Log comment generation results to database"""
        try:
            db_manager = DatabaseManager()
            
            log_data = {
                'agent_type': self.agent_type,
                'blog_url': blog_url,
                'task_type': 'comment_generation',
                'success': result['success'],
                'result': {
                    'comment_length': result['metadata'].get('length', 0),
                    'keyword_density': result['metadata'].get('keyword_density', 0),
                    'validation_score': result['metadata'].get('validation_score', 0),
                    'comment_type': result['metadata'].get('comment_type', 'unknown')
                },
                'error_message': result.get('error'),
                'execution_time': result['metadata'].get('generation_time', 0),
                'cost': self.get_accumulated_cost(),
                'timestamp': datetime.now()
            }
            
            await db_manager.log_agent_activity(log_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log comment generation: {str(e)}")
