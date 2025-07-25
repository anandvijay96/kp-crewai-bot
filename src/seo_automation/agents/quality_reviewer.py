"""
QualityReviewer Agent - Reviews and scores comments for quality and brand safety

This agent specializes in:
- Quality assessment of generated comments
- Brand safety and compliance checks
- Engagement potential evaluation
- Risk assessment and mitigation
- Performance prediction and optimization recommendations
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from crewai import Agent
from ..utils.database import DatabaseManager
from .base_agent import BaseAgent


class QualityReviewer(BaseAgent):
    """
    Specialized agent for reviewing comment quality and ensuring brand safety
    
    Capabilities:
    - Comprehensive quality scoring
    - Brand safety assessment
    - Engagement potential evaluation
    - Risk identification and mitigation
    - Performance optimization recommendations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the QualityReviewer agent"""
        super().__init__(config)
        self.agent_type = "quality_reviewer"
        self.logger = logging.getLogger(f"{__name__}.QualityReviewer")
        
        # Review thresholds and weights
        self.quality_threshold = config.get('quality_threshold', 75) if config else 75
        self.brand_safety_threshold = config.get('brand_safety_threshold', 85) if config else 85
        
        # Scoring weights
        self.scoring_weights = config.get('scoring_weights', {
            'relevance': 0.25,
            'value_addition': 0.20,
            'engagement_potential': 0.20,
            'brand_safety': 0.15,
            'professional_tone': 0.10,
            'keyword_integration': 0.10
        }) if config else {
            'relevance': 0.25,
            'value_addition': 0.20,
            'engagement_potential': 0.20,
            'brand_safety': 0.15,
            'professional_tone': 0.10,
            'keyword_integration': 0.10
        }
        
        # Brand guidelines
        self.brand_guidelines = config.get('brand_guidelines', {
            'company_name': 'KnowladgePoint',
            'voice': 'professional_friendly',
            'forbidden_topics': ['politics', 'religion', 'controversial_social_issues'],
            'required_values': ['expertise', 'helpfulness', 'authenticity'],
            'compliance_rules': ['no_spam', 'no_self_promotion', 'add_genuine_value']
        }) if config else {
            'company_name': 'KnowladgePoint',
            'voice': 'professional_friendly',
            'forbidden_topics': ['politics', 'religion', 'controversial_social_issues'],
            'required_values': ['expertise', 'helpfulness', 'authenticity'],
            'compliance_rules': ['no_spam', 'no_self_promotion', 'add_genuine_value']
        }
        
        self.agent = self._create_crewai_agent()
    
    def _create_crewai_agent(self) -> Agent:
        """Create and configure the CrewAI agent"""
        return Agent(
            role="Senior Content Quality Reviewer",
            goal=f"""Ensure all comments meet the highest standards of quality, brand safety, and compliance 
                     while maximizing engagement potential and SEO value for {self.brand_guidelines['company_name']}""",
            backstory=f"""You are a senior content strategist and brand safety expert at {self.brand_guidelines['company_name']} 
                        with extensive experience in digital marketing, SEO, and online reputation management. 
                        You have a keen eye for quality, understand the nuances of effective online engagement, 
                        and are passionate about maintaining brand integrity while maximizing marketing impact.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=3,
            memory=True
        )
    
    async def review_comment(
        self,
        comment: str,
        blog_data: Dict[str, Any],
        content_analysis: Dict[str, Any],
        target_keywords: List[str] = None,
        generation_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive comment review and scoring
        
        Args:
            comment: The comment to review
            blog_data: Original blog post information
            content_analysis: Content analysis results
            target_keywords: Target keywords for the comment
            generation_metadata: Metadata from comment generation
            
        Returns:
            Dict containing review results, scores, and recommendations
        """
        review_start_time = datetime.now()
        
        try:
            # Perform multi-dimensional analysis
            quality_scores = await self._analyze_quality_dimensions(
                comment, blog_data, content_analysis, target_keywords
            )
            
            # Assess brand safety
            brand_safety_result = self._assess_brand_safety(comment, blog_data)
            
            # Evaluate engagement potential
            engagement_score = self._evaluate_engagement_potential(comment, blog_data)
            
            # Check for risks
            risk_assessment = self._assess_risks(comment, blog_data)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                quality_scores, brand_safety_result, engagement_score
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                comment, quality_scores, brand_safety_result, risk_assessment
            )
            
            # Determine approval status
            approval_status = self._determine_approval_status(
                overall_score, brand_safety_result, risk_assessment
            )
            
            result = {
                'success': True,
                'overall_score': overall_score,
                'approval_status': approval_status,
                'quality_scores': quality_scores,
                'brand_safety': brand_safety_result,
                'engagement_score': engagement_score,
                'risk_assessment': risk_assessment,
                'recommendations': recommendations,
                'metadata': {
                    'review_time': (datetime.now() - review_start_time).total_seconds(),
                    'reviewer_confidence': self._calculate_confidence_score(quality_scores),
                    'target_keywords': target_keywords or [],
                    'generation_metadata': generation_metadata or {}
                }
            }
            
            # Log review to database
            await self._log_review_results(
                blog_data.get('url', ''), comment, result
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Comment review failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return {
                'success': False,
                'error': error_msg,
                'overall_score': 0,
                'approval_status': 'rejected',
                'metadata': {
                    'review_time': (datetime.now() - review_start_time).total_seconds()
                }
            }
    
    async def _analyze_quality_dimensions(
        self,
        comment: str,
        blog_data: Dict[str, Any],
        content_analysis: Dict[str, Any],
        target_keywords: List[str]
    ) -> Dict[str, float]:
        """Analyze multiple quality dimensions of the comment"""
        
        # Build comprehensive analysis prompt
        analysis_prompt = self._build_quality_analysis_prompt(
            comment, blog_data, content_analysis, target_keywords
        )
        
        # Get AI analysis
        analysis_result = await self.execute_task(
            agent=self.agent,
            task_description=analysis_prompt,
            expected_output="JSON analysis with scores for each quality dimension"
        )
        
        if not analysis_result.get('success'):
            # Fallback to rule-based analysis
            return self._fallback_quality_analysis(comment, blog_data, target_keywords)
        
        try:
            # Parse AI analysis results
            ai_scores = json.loads(analysis_result['result'])
            
            # Validate and normalize scores
            quality_scores = {}
            for dimension in self.scoring_weights.keys():
                score = ai_scores.get(dimension, 50)
                quality_scores[dimension] = max(0, min(100, float(score)))
            
            return quality_scores
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse AI analysis, using fallback: {e}")
            return self._fallback_quality_analysis(comment, blog_data, target_keywords)
    
    def _build_quality_analysis_prompt(
        self,
        comment: str,
        blog_data: Dict[str, Any],
        content_analysis: Dict[str, Any],
        target_keywords: List[str]
    ) -> str:
        """Build prompt for AI-powered quality analysis"""
        
        blog_title = blog_data.get('title', '')
        blog_excerpt = blog_data.get('content', '')[:1000]
        
        prompt = f"""
Analyze the following blog comment across multiple quality dimensions and provide scores (0-100) for each:

BLOG POST:
Title: {blog_title}
Content excerpt: {blog_excerpt}...

COMMENT TO REVIEW:
"{comment}"

TARGET KEYWORDS: {', '.join(target_keywords or [])}

CONTENT ANALYSIS CONTEXT: {json.dumps(content_analysis.get('key_topics', [])[:5])}

Please score the comment (0-100) on these dimensions:

1. RELEVANCE (0-100): How well does the comment relate to the blog post content?
   - Consider topic alignment, specific references to the article
   - Higher scores for comments that directly address main points

2. VALUE_ADDITION (0-100): How much genuine value does this comment add?
   - Consider new insights, different perspectives, useful information
   - Higher scores for substantive contributions vs generic responses

3. ENGAGEMENT_POTENTIAL (0-100): How likely is this comment to generate engagement?
   - Consider questions asked, discussion prompts, thought-provoking elements
   - Higher scores for comments that invite responses

4. BRAND_SAFETY (0-100): How safe is this comment from a brand perspective?
   - Consider tone, potential controversies, professionalism
   - Higher scores for safe, professional, and appropriate content

5. PROFESSIONAL_TONE (0-100): How professional and appropriate is the tone?
   - Consider language quality, grammar, respectfulness
   - Higher scores for polished, professional communication

6. KEYWORD_INTEGRATION (0-100): How naturally are target keywords integrated?
   - Consider natural flow, relevance, avoiding keyword stuffing
   - Higher scores for seamless, relevant keyword usage

Respond with ONLY a JSON object in this format:
{{
    "relevance": 85,
    "value_addition": 78,
    "engagement_potential": 82,
    "brand_safety": 95,
    "professional_tone": 88,
    "keyword_integration": 75
}}
"""
        return prompt
    
    def _fallback_quality_analysis(
        self,
        comment: str,
        blog_data: Dict[str, Any],
        target_keywords: List[str]
    ) -> Dict[str, float]:
        """Rule-based fallback quality analysis"""
        
        scores = {}
        comment_lower = comment.lower()
        comment_words = comment.split()
        
        # Relevance score (basic keyword matching)
        blog_title_words = set(blog_data.get('title', '').lower().split())
        blog_content_words = set(blog_data.get('content', '')[:500].lower().split())
        comment_words_set = set(comment_lower.split())
        
        title_overlap = len(comment_words_set.intersection(blog_title_words))
        content_overlap = len(comment_words_set.intersection(blog_content_words))
        
        scores['relevance'] = min(100, (title_overlap * 15 + content_overlap * 5) + 40)
        
        # Value addition (length and complexity indicators)
        value_score = 50
        if len(comment) > 100:
            value_score += 20
        if '?' in comment:
            value_score += 10
        if any(word in comment_lower for word in ['example', 'experience', 'suggest', 'recommend']):
            value_score += 15
        
        scores['value_addition'] = min(100, value_score)
        
        # Engagement potential
        engagement_score = 60
        if comment.count('?') > 0:
            engagement_score += 15
        if any(word in comment_lower for word in ['what', 'how', 'why', 'thoughts', 'opinion']):
            engagement_score += 10
        if len(comment) > 150:
            engagement_score += 10
        
        scores['engagement_potential'] = min(100, engagement_score)
        
        # Brand safety (conservative scoring)
        scores['brand_safety'] = 85  # Start high, reduce for issues
        
        # Professional tone
        professional_score = 80
        if comment[0].isupper():
            professional_score += 5
        if comment.endswith('.'):
            professional_score += 5
        if len([w for w in comment_words if w.isupper()]) > 2:
            professional_score -= 15
        
        scores['professional_tone'] = max(0, min(100, professional_score))
        
        # Keyword integration
        if target_keywords:
            keyword_mentions = sum(
                1 for keyword in target_keywords 
                if keyword.lower() in comment_lower
            )
            scores['keyword_integration'] = min(100, keyword_mentions * 25 + 50)
        else:
            scores['keyword_integration'] = 75
        
        return scores
    
    def _assess_brand_safety(self, comment: str, blog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess brand safety and compliance"""
        
        safety_score = 100
        issues = []
        warnings = []
        
        comment_lower = comment.lower()
        
        # Check forbidden topics
        for topic in self.brand_guidelines['forbidden_topics']:
            if topic.lower() in comment_lower:
                issues.append(f"Contains forbidden topic: {topic}")
                safety_score -= 25
        
        # Check for spam indicators
        spam_patterns = [
            r'http[s]?://[^\s]+',
            r'www\.[^\s]+',
            r'click here',
            r'visit our',
            r'check out our',
            r'buy now',
            r'limited time'
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, comment_lower):
                issues.append(f"Contains spam indicator: {pattern}")
                safety_score -= 20
        
        # Check for excessive self-promotion
        company_mentions = comment_lower.count(self.brand_guidelines['company_name'].lower())
        if company_mentions > 1:
            warnings.append("Multiple company mentions detected")
            safety_score -= 10
        
        # Check for inappropriate language
        inappropriate_words = ['damn', 'hell', 'stupid', 'idiot', 'suck', 'hate']
        for word in inappropriate_words:
            if word in comment_lower:
                warnings.append(f"Potentially inappropriate language: {word}")
                safety_score -= 5
        
        # Check for overly promotional language
        promotional_phrases = [
            'our services', 'we offer', 'contact us', 'hire us',
            'our company', 'we can help', 'call us'
        ]
        
        promotional_count = sum(1 for phrase in promotional_phrases if phrase in comment_lower)
        if promotional_count > 1:
            issues.append("Overly promotional content")
            safety_score -= 15
        
        return {
            'score': max(0, safety_score),
            'issues': issues,
            'warnings': warnings,
            'is_safe': safety_score >= self.brand_safety_threshold
        }
    
    def _evaluate_engagement_potential(self, comment: str, blog_data: Dict[str, Any]) -> float:
        """Evaluate the comment's potential to generate engagement"""
        
        engagement_score = 50
        comment_lower = comment.lower()
        
        # Questions boost engagement
        question_count = comment.count('?')
        engagement_score += min(20, question_count * 10)
        
        # Discussion starters
        discussion_starters = [
            'what do you think', 'in your experience', 'have you tried',
            'would love to hear', 'curious about', 'what are your thoughts'
        ]
        
        for starter in discussion_starters:
            if starter in comment_lower:
                engagement_score += 15
                break
        
        # Personal experience sharing
        experience_indicators = [
            'in my experience', 'i found that', 'i noticed', 'i\'ve seen',
            'when i', 'i recently', 'i usually'
        ]
        
        for indicator in experience_indicators:
            if indicator in comment_lower:
                engagement_score += 10
                break
        
        # Length factor (longer comments tend to get more engagement)
        if len(comment) > 200:
            engagement_score += 10
        elif len(comment) < 50:
            engagement_score -= 15
        
        # Call to action or invitation for discussion
        cta_phrases = [
            'let me know', 'share your', 'would appreciate',
            'feedback welcome', 'thoughts?', 'agree or disagree'
        ]
        
        for phrase in cta_phrases:
            if phrase in comment_lower:
                engagement_score += 12
                break
        
        return max(0, min(100, engagement_score))
    
    def _assess_risks(self, comment: str, blog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential risks associated with the comment"""
        
        risks = []
        risk_level = 'low'
        
        comment_lower = comment.lower()
        
        # High-risk indicators
        high_risk_patterns = [
            r'guaranteed results?',
            r'100% success',
            r'secret method',
            r'insider information',
            r'exclusive offer'
        ]
        
        for pattern in high_risk_patterns:
            if re.search(pattern, comment_lower):
                risks.append(f"High-risk claim detected: {pattern}")
                risk_level = 'high'
        
        # Medium-risk indicators
        medium_risk_patterns = [
            r'best ever',
            r'revolutionary',
            r'life-changing',
            r'game-changer',
            r'breakthrough'
        ]
        
        for pattern in medium_risk_patterns:
            if re.search(pattern, comment_lower):
                risks.append(f"Medium-risk claim detected: {pattern}")
                if risk_level == 'low':
                    risk_level = 'medium'
        
        # Check for potential copyright issues
        if 'copyright' in comment_lower or '©' in comment:
            risks.append("Potential copyright reference")
            risk_level = 'medium'
        
        # Check for competitor mentions
        competitors = ['semrush', 'ahrefs', 'moz', 'hubspot', 'marketo']
        for competitor in competitors:
            if competitor in comment_lower:
                risks.append(f"Competitor mention: {competitor}")
                if risk_level == 'low':
                    risk_level = 'medium'
        
        return {
            'level': risk_level,
            'risks': risks,
            'is_safe': risk_level != 'high'
        }
    
    def _calculate_overall_score(
        self,
        quality_scores: Dict[str, float],
        brand_safety: Dict[str, Any],
        engagement_score: float
    ) -> float:
        """Calculate weighted overall score"""
        
        # Calculate weighted quality score
        weighted_quality = sum(
            quality_scores[dimension] * weight
            for dimension, weight in self.scoring_weights.items()
        )
        
        # Apply brand safety penalty
        safety_penalty = max(0, (100 - brand_safety['score']) * 0.3)
        
        # Apply engagement bonus (small positive factor)
        engagement_bonus = (engagement_score - 50) * 0.1
        
        overall_score = weighted_quality - safety_penalty + engagement_bonus
        
        return max(0, min(100, overall_score))
    
    async def _generate_recommendations(
        self,
        comment: str,
        quality_scores: Dict[str, float],
        brand_safety: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Quality-based recommendations
        for dimension, score in quality_scores.items():
            if score < 70:
                if dimension == 'relevance':
                    recommendations.append("Improve relevance by referencing specific points from the blog post")
                elif dimension == 'value_addition':
                    recommendations.append("Add more substantive insights or personal experiences")
                elif dimension == 'engagement_potential':
                    recommendations.append("Include questions or discussion prompts to encourage engagement")
                elif dimension == 'professional_tone':
                    recommendations.append("Enhance professional tone and grammar")
                elif dimension == 'keyword_integration':
                    recommendations.append("Better integrate target keywords naturally")
        
        # Brand safety recommendations
        if brand_safety['issues']:
            recommendations.append("Address brand safety issues: " + ", ".join(brand_safety['issues']))
        
        if brand_safety['warnings']:
            recommendations.append("Consider warnings: " + ", ".join(brand_safety['warnings']))
        
        # Risk-based recommendations
        if risk_assessment['level'] == 'high':
            recommendations.append("Remove high-risk claims and statements")
        elif risk_assessment['level'] == 'medium':
            recommendations.append("Review and moderate medium-risk elements")
        
        return recommendations
    
    def _determine_approval_status(
        self,
        overall_score: float,
        brand_safety: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> str:
        """Determine final approval status"""
        
        # Hard rejections
        if not brand_safety['is_safe']:
            return 'rejected'
        
        if risk_assessment['level'] == 'high':
            return 'rejected'
        
        # Score-based approval
        if overall_score >= self.quality_threshold:
            if risk_assessment['level'] == 'low':
                return 'approved'
            else:
                return 'conditional_approval'
        elif overall_score >= 60:
            return 'needs_revision'
        else:
            return 'rejected'
    
    def _calculate_confidence_score(self, quality_scores: Dict[str, float]) -> float:
        """Calculate reviewer confidence based on score consistency"""
        
        if not quality_scores:
            return 0.5
        
        scores = list(quality_scores.values())
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        
        # Higher variance = lower confidence
        confidence = max(0.3, min(1.0, 1.0 - (variance / 1000)))
        
        return confidence
    
    async def batch_review_comments(
        self,
        comments_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Review multiple comments in batch"""
        
        results = []
        
        for comment_data in comments_data:
            try:
                review_result = await self.review_comment(
                    comment=comment_data['comment'],
                    blog_data=comment_data.get('blog_data', {}),
                    content_analysis=comment_data.get('content_analysis', {}),
                    target_keywords=comment_data.get('target_keywords', []),
                    generation_metadata=comment_data.get('generation_metadata', {})
                )
                
                results.append({
                    'comment_id': comment_data.get('id'),
                    'review_result': review_result
                })
                
            except Exception as e:
                self.logger.error(f"Failed to review comment {comment_data.get('id')}: {e}")
                results.append({
                    'comment_id': comment_data.get('id'),
                    'review_result': {
                        'success': False,
                        'error': str(e),
                        'approval_status': 'rejected'
                    }
                })
        
        return results
    
    async def _log_review_results(
        self,
        blog_url: str,
        comment: str,
        review_result: Dict[str, Any]
    ):
        """Log review results to database"""
        try:
            db_manager = DatabaseManager()
            
            log_data = {
                'agent_type': self.agent_type,
                'blog_url': blog_url,
                'task_type': 'comment_review',
                'success': review_result['success'],
                'result': {
                    'overall_score': review_result.get('overall_score', 0),
                    'approval_status': review_result.get('approval_status', 'unknown'),
                    'quality_scores': review_result.get('quality_scores', {}),
                    'brand_safety_score': review_result.get('brand_safety', {}).get('score', 0),
                    'engagement_score': review_result.get('engagement_score', 0),
                    'risk_level': review_result.get('risk_assessment', {}).get('level', 'unknown')
                },
                'error_message': review_result.get('error'),
                'execution_time': review_result.get('metadata', {}).get('review_time', 0),
                'cost': self.get_accumulated_cost(),
                'timestamp': datetime.now()
            }
            
            await db_manager.log_agent_activity(log_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log review results: {str(e)}")
