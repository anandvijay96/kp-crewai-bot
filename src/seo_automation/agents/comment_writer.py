"""
Comment Writer Agent - AI-powered comment generation

This agent generates contextually relevant, high-quality comments based on blog analysis:
- AI-powered content creation using Vertex AI
- Context-aware comment generation based on blog content analysis
- Multiple comment styles and tones
- Integration with ContentAnalysisTool for understanding blog context
- Spam detection and quality assurance
- Customizable comment templates and strategies
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
import random

from crewai import Agent
from ..core.base_agent import BaseSEOAgent
from ..utils.database import Comment, Blog, db_manager


class CommentWriterAgent(BaseSEOAgent):
    """
    AI-powered Comment Writer Agent
    
    Capabilities:
    1. Context-aware comment generation based on blog analysis
    2. Multiple comment styles and strategies
    3. AI-powered content creation using Vertex AI
    4. Quality assurance and spam prevention
    5. Template-based comment generation
    6. Personalization and tone adaptation
    7. Database integration for comment storage
    8. Performance optimization and cost tracking
    """
    
    def __init__(self):
        super().__init__(
            name="CommentWriter",
            role="AI-Powered Content Creation Specialist",
            goal="""Generate high-quality, contextually relevant comments that add value to blog discussions
                   while promoting KloudPortal's expertise in cloud computing and DevOps""",
            backstory="""You are an expert content writer specializing in creating engaging, valuable comments
                      for technical blogs. You understand cloud computing, DevOps, and modern software development
                      practices. Your comments are always helpful, insightful, and naturally promote KloudPortal's
                      services without being spammy. You adapt your writing style to match the blog's tone and
                      audience while maintaining authenticity and providing genuine value.""",
            model_name="gemini-2.0-flash-exp"
        )
    
    # Remove the CrewAI agent method since we're using Vertex AI directly
    
    # Comment generation configuration
    COMMENT_TYPES = {
        "engaging": "Write an engaging, conversational comment that invites further discussion",
        "question": "Ask thoughtful questions that encourage the author and readers to share more insights",
        "insight": "Share a valuable insight or alternative perspective on the topic",
        "experience": "Share a relevant personal or professional experience related to the topic",
        "resource": "Suggest additional resources or tools that complement the article",
        "technical": "Provide technical details or clarifications on discussed concepts"
    }
    
    COMMENT_TEMPLATES = {
        "opener": [
            "Great insights on {topic}!",
            "This really resonates with my experience in {field}.",
            "Excellent breakdown of {concept}.",
            "Thanks for sharing this perspective on {topic}."
        ],
        "body": [
            "I've found that {insight} when working with similar challenges.",
            "One thing I'd add is {additional_point}.",
            "From my experience at KloudPortal, {experience}.",
            "This aligns with what we've seen in our {domain} projects."
        ],
        "closer": [
            "What's been your experience with {topic}?",
            "Would love to hear your thoughts on {question}.",
            "Looking forward to more content like this!",
            "Keep up the excellent work!"
        ]
    }
    
    # Brand voice settings
    BRAND_VOICE_CONFIG = {
        "company_name": "KloudPortal",
        "expertise_areas": [
            "cloud computing", "DevOps", "infrastructure automation",
            "containerization", "microservices", "CI/CD", "cloud migration"
        ],
        "tone": "professional yet approachable",
        "max_comment_length": 500,
        "min_comment_length": 80
    }

    async def generate_comment(
        self, 
        blog_data: Dict[str, Any], 
        content_analysis: Dict[str, Any],
        target_keywords: List[str] = None,
        comment_type: str = "engaging"
    ) -> Dict[str, Any]:
        """
        Generate a contextual comment for a blog post using AI
        
        Args:
            blog_data: Blog information (title, content, author, etc.)
            content_analysis: Analysis results from ContentAnalysisTool
            target_keywords: Keywords to strategically include
            comment_type: Type of comment to generate
            
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
            sentiment = content_analysis.get('sentiment', 'neutral')
            
            # Build comment generation prompt
            prompt = self._build_comment_prompt(
                blog_title, blog_content, key_topics, 
                target_keywords, comment_type, sentiment
            )
            
            # Generate comment using Vertex AI with higher token limit
            comment_result = await self.execute_ai_task(
                prompt=prompt,
                task_type="comment_generation",
                max_tokens=512  # Increased token limit for proper generation
            )
            
            if not comment_result.success:
                raise Exception(f"AI comment generation failed: {comment_result.error}")
            
            generated_comment = comment_result.result
            
            # Post-process and validate comment
            processed_comment = self._process_comment(generated_comment, target_keywords)
            validation_result = self._validate_comment(processed_comment, blog_content)
            
            if not validation_result['is_valid']:
                # Try regenerating with stricter guidelines
                refined_prompt = self._build_refined_prompt(prompt, validation_result['issues'])
                retry_result = await self.execute_ai_task(
                    prompt=refined_prompt,
                    task_type="comment_generation_retry",
                    max_tokens=512  # Increased token limit for retry
                )
                
                if retry_result.success:
                    processed_comment = self._process_comment(retry_result.result, target_keywords)
                    validation_result = self._validate_comment(processed_comment, blog_content)
            
            # Calculate metrics
            keyword_density = self._calculate_keyword_density(processed_comment, target_keywords or [])
            readability_score = self._calculate_readability(processed_comment)
            
            result = {
                'success': True,
                'comment': processed_comment,
                'metadata': {
                    'comment_type': comment_type,
                    'length': len(processed_comment),
                    'word_count': len(processed_comment.split()),
                    'keyword_density': keyword_density,
                    'readability_score': readability_score,
                    'relevance_score': relevance_score,
                    'validation_score': validation_result['score'],
                    'validation_issues': validation_result['issues'],
                    'is_valid': validation_result['is_valid'],
                    'target_keywords': target_keywords or [],
                    'key_topics_addressed': key_topics[:3],
                    'generation_time': (datetime.now() - task_start_time).total_seconds(),
                    'cost': self.get_accumulated_cost()
                }
            }
            
            # Store comment in database (temporarily disabled for testing)
            # await self._store_comment(blog_url, result)
            
            return result
            
        except Exception as e:
            error_msg = f"Comment generation failed: {str(e)}"
            print(f"ERROR: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'comment': None,
                'metadata': {
                    'generation_time': (datetime.now() - task_start_time).total_seconds(),
                    'cost': self.get_accumulated_cost()
                }
            }
    
    # Removed duplicate method definitions - keeping the improved versions below
    
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
    
    def _build_comment_prompt(
        self, 
        title: str, 
        content: str, 
        key_topics: List[str],
        target_keywords: List[str],
        comment_type: str,
        sentiment: str
    ) -> str:
        """Build a comprehensive AI prompt for comment generation"""
        
        # Truncate content for prompt efficiency
        content_excerpt = content[:1500] + "..." if len(content) > 1500 else content
        
        # Get comment type instruction
        type_instruction = self.COMMENT_TYPES.get(comment_type, "Write an engaging comment")
        
        # Select appropriate templates based on topics
        topic_context = key_topics[0] if key_topics else "the topic"
        
        prompt = f"""
You are a cloud computing and DevOps expert at KloudPortal. Generate a high-quality blog comment that demonstrates your expertise while adding genuine value to the discussion.

BLOG POST:
Title: {title}
Content: {content_excerpt}

KEY TOPICS: {', '.join(key_topics[:3])}
COMMENT STYLE: {type_instruction}
TARGET KEYWORDS: {', '.join(target_keywords or [])}
CONTENT SENTIMENT: {sentiment}

REQUIREMENTS:
- Length: {self.BRAND_VOICE_CONFIG['min_comment_length']}-{self.BRAND_VOICE_CONFIG['max_comment_length']} characters
- Tone: {self.BRAND_VOICE_CONFIG['tone']}
- Expertise areas: {', '.join(self.BRAND_VOICE_CONFIG['expertise_areas'][:3])}

GUIDELINES:
1. Reference specific points from the article
2. Share relevant technical insights or experiences
3. Add practical value to the discussion
4. Include keywords naturally (no stuffing)
5. Ask engaging follow-up questions when appropriate
6. Mention KloudPortal subtly if relevant to the topic
7. Maintain professional yet conversational tone

AVOID:
- Generic responses ("Great post!", "Thanks for sharing")
- Over-promotion or sales pitches
- Controversial statements
- Keyword stuffing
- Off-topic content

Generate only the comment text (no meta-commentary):
"""
        return prompt
    
    def _build_refined_prompt(self, original_prompt: str, issues: List[str]) -> str:
        """Build a refined prompt addressing validation issues"""
        issue_fixes = {
            'too short': 'Make the comment longer and more detailed',
            'too long': 'Make the comment more concise',
            'generic': 'Be more specific and avoid generic phrases',
            'keyword stuffing': 'Use keywords more naturally and sparingly',
            'spam indicators': 'Remove any promotional language or links'
        }
        
        additional_instructions = []
        for issue in issues:
            for problem, fix in issue_fixes.items():
                if problem in issue.lower():
                    additional_instructions.append(f"- {fix}")
        
        if additional_instructions:
            refinement = "\n\nADDITIONAL REQUIREMENTS:\n" + "\n".join(additional_instructions)
            return original_prompt + refinement
        
        return original_prompt
    
    def _process_comment(self, raw_comment: str, keywords: List[str] = None) -> str:
        """Process and clean the generated comment"""
        # Remove any unwanted formatting and quotes
        comment = raw_comment.strip()
        comment = re.sub(r'^["\']|["\']$', '', comment)  # Remove surrounding quotes
        comment = re.sub(r'\n+', ' ', comment)  # Replace newlines with spaces
        comment = re.sub(r'\s+', ' ', comment)  # Normalize whitespace
        
        # Ensure proper sentence structure
        if comment and not comment[0].isupper():
            comment = comment[0].upper() + comment[1:]
        
        # Ensure proper punctuation
        if comment and not comment.endswith(('.', '!', '?')):
            comment += '.'
        
        # Apply length constraints
        max_len = self.BRAND_VOICE_CONFIG['max_comment_length']
        min_len = self.BRAND_VOICE_CONFIG['min_comment_length']
        
        if len(comment) > max_len:
            # Truncate at last complete sentence within limit
            truncated = comment[:max_len]
            last_sentence_end = max(
                truncated.rfind('.'),
                truncated.rfind('!'),
                truncated.rfind('?')
            )
            if last_sentence_end > min_len:
                comment = truncated[:last_sentence_end + 1]
            else:
                comment = truncated[:max_len-3] + '...'
        
        return comment
    
    def _validate_comment(self, comment: str, blog_content: str) -> Dict[str, Any]:
        """Validate the generated comment for quality and appropriateness"""
        issues = []
        score = 100
        
        # Length validation
        min_len = self.BRAND_VOICE_CONFIG['min_comment_length']
        max_len = self.BRAND_VOICE_CONFIG['max_comment_length']
        
        if len(comment) < min_len:
            issues.append(f"Comment too short ({len(comment)} chars, min: {min_len})")
            score -= 25
        elif len(comment) > max_len:
            issues.append(f"Comment too long ({len(comment)} chars, max: {max_len})")
            score -= 10
        
        # Generic phrases detection
        generic_phrases = [
            "great post", "nice article", "thanks for sharing", "very informative",
            "good points", "i agree", "well written", "interesting read"
        ]
        
        comment_lower = comment.lower()
        generic_count = sum(1 for phrase in generic_phrases if phrase in comment_lower)
        if generic_count > 1:
            issues.append("Comment contains generic phrases")
            score -= 15
        
        # Word repetition check (potential keyword stuffing)
        words = [w.lower() for w in comment.split() if len(w) > 3]
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        for word, count in word_counts.items():
            if count > 3:
                issues.append(f"Word '{word}' repeated {count} times")
                score -= 15
        
        # Spam/promotional content detection
        spam_patterns = [
            r'\b(visit|check out|click)\s+(our|my)\s+\w+',
            r'\b(contact|email|call)\s+(us|me)\b',
            r'https?://\S+',
            r'\b\w+\.(com|net|org)\b',
            r'\b(buy|purchase|order|sale|discount)\b'
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, comment_lower):
                issues.append("Contains promotional/spam indicators")
                score -= 30
                break
        
        # Content relevance check (basic)
        blog_words = set(blog_content.lower().split())
        comment_words = set(comment.lower().split())
        overlap = len(blog_words.intersection(comment_words))
        
        if overlap < 2:
            issues.append("Comment may not be relevant to blog content")
            score -= 20
        
        return {
            'score': max(0, score),
            'issues': issues,
            'is_valid': score >= 70
        }
    
    def _calculate_keyword_density(self, comment: str, keywords: List[str]) -> float:
        """Calculate keyword density in the comment"""
        if not keywords or not comment:
            return 0.0
        
        comment_words = comment.lower().split()
        total_words = len(comment_words)
        
        if total_words == 0:
            return 0.0
        
        keyword_occurrences = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Count phrase occurrences
            if ' ' in keyword_lower:
                keyword_occurrences += comment.lower().count(keyword_lower)
            else:
                # Count individual word occurrences
                keyword_occurrences += comment_words.count(keyword_lower)
        
        return keyword_occurrences / total_words
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate basic readability score (simplified Flesch Reading Ease)"""
        if not text:
            return 0.0
        
        # Count sentences, words, and syllables
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Simplified syllable counting
        syllables = 0
        for word in text.split():
            word = word.lower().strip('.,!?;:')
            syllable_count = max(1, len(re.findall(r'[aeiouAEIOU]', word)))
            syllables += syllable_count
        
        # Simplified Flesch Reading Ease formula
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, score))
    
    async def _store_comment(self, blog_url: str, result: Dict[str, Any]):
        """Store generated comment in database"""
        try:
            if result['success']:
                comment = Comment(
                    blog_url=blog_url,
                    content=result['comment'],
                    comment_type=result['metadata']['comment_type'],
                    length=result['metadata']['length'],
                    keyword_density=result['metadata']['keyword_density'],
                    validation_score=result['metadata']['validation_score'],
                    is_valid=result['metadata']['is_valid'],
                    target_keywords=json.dumps(result['metadata']['target_keywords']),
                    generation_cost=result['metadata']['cost'],
                    created_at=datetime.now()
                )
                
                await db_manager.store_comment(comment)
                print(f"✓ Comment stored for: {blog_url}")
            
        except Exception as e:
            print(f"ERROR storing comment: {str(e)}")
    
    async def batch_generate_comments(
        self,
        blog_list: List[Dict[str, Any]],
        keywords_per_blog: Dict[str, List[str]] = None,
        comment_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate comments for multiple blogs in batch"""
        
        if not comment_types:
            comment_types = ["engaging", "question", "insight"]
        
        results = {
            'successful': [],
            'failed': [],
            'total_cost': 0.0,
            'total_time': 0.0
        }
        
        start_time = datetime.now()
        
        for blog_data in blog_list:
            blog_url = blog_data.get('url', '')
            target_keywords = keywords_per_blog.get(blog_url, []) if keywords_per_blog else []
            
            # Select random comment type for variety
            comment_type = random.choice(comment_types)
            
            try:
                # Assume we have content analysis available
                # In practice, this would come from ContentAnalysisTool
                content_analysis = {
                    'relevance_score': 0.8,
                    'key_topics': ['cloud computing', 'DevOps', 'automation'],
                    'sentiment': 'positive'
                }
                
                comment_result = await self.generate_comment(
                    blog_data, content_analysis, target_keywords, comment_type
                )
                
                if comment_result['success']:
                    results['successful'].append({
                        'url': blog_url,
                        'comment': comment_result['comment'],
                        'metadata': comment_result['metadata']
                    })
                else:
                    results['failed'].append({
                        'url': blog_url,
                        'error': comment_result['error']
                    })
                
                results['total_cost'] += comment_result['metadata'].get('cost', 0)
                
            except Exception as e:
                results['failed'].append({
                    'url': blog_url,
                    'error': str(e)
                })
        
        results['total_time'] = (datetime.now() - start_time).total_seconds()
        results['success_rate'] = len(results['successful']) / len(blog_list) if blog_list else 0
        
        return results
    
    def _execute_task(self, task: str, context: Dict[str, Any] = None) -> Any:
        """Execute the specific task for comment generation."""
        # This is the main entry point for the base class
        # For comment generation, we'll use the async methods
        return {
            'message': 'Use async generate_comment methods for comment generation tasks',
            'available_methods': ['generate_comment', 'generate_comment_variants', 'batch_generate_comments']
        }
    
    async def execute_ai_task(self, prompt: str, task_type: str, max_tokens: int = 300) -> Any:
        """Execute an AI task using Vertex AI"""
        try:
            # Use the VertexAI manager from the base class
            response = await self.vertex_ai.generate_text(
                prompt=prompt,
                model_name=self.model_name,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return type('Response', (), {
                'success': True,
                'result': response,
                'error': None
            })()
            
        except Exception as e:
            return type('Response', (), {
                'success': False,
                'result': None,
                'error': str(e)
            })()
    
    def get_accumulated_cost(self) -> float:
        """Get accumulated cost from Vertex AI"""
        return self.vertex_ai.get_session_cost()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            'agent_name': self.name,
            'total_cost': self.get_accumulated_cost(),
            'supported_comment_types': list(self.COMMENT_TYPES.keys()),
            'brand_config': self.BRAND_VOICE_CONFIG,
            'min_comment_length': self.BRAND_VOICE_CONFIG['min_comment_length'],
            'max_comment_length': self.BRAND_VOICE_CONFIG['max_comment_length']
        }
