"""
Data Validator - Validates and cleans scraped blog data
"""
import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import validators

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates and cleans scraped blog data for quality and consistency
    """
    
    def __init__(self):
        # Minimum quality thresholds
        self.min_title_length = 10
        self.min_description_length = 20
        self.min_quality_score = 0.3
        
        # Excluded domains and patterns
        self.excluded_domains = {
            'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'linkedin.com', 'pinterest.com', 'reddit.com', 'tiktok.com',
            'snapchat.com', 'whatsapp.com', 'telegram.org'
        }
        
        self.excluded_patterns = [
            r'\.pdf$', r'\.doc$', r'\.docx$', r'\.xls$', r'\.xlsx$',
            r'\.ppt$', r'\.pptx$', r'\.zip$', r'\.rar$', r'\.exe$'
        ]
    
    def validate_blog_result(self, blog_result) -> bool:
        """
        Validate a blog result object for quality and completeness
        """
        try:
            # Validate URL
            if not self._is_valid_url(blog_result.url):
                logger.debug(f"Invalid URL: {blog_result.url}")
                return False
            
            # Validate domain
            if not self._is_valid_domain(blog_result.domain):
                logger.debug(f"Invalid or excluded domain: {blog_result.domain}")
                return False
            
            # Validate content quality
            if not self._has_sufficient_content(blog_result):
                logger.debug(f"Insufficient content quality: {blog_result.url}")
                return False
            
            # Validate authority scores (if present)
            if not self._has_valid_authority_scores(blog_result):
                logger.debug(f"Invalid authority scores: {blog_result.url}")
                return False
            
            # Validate comment opportunities
            if not self._has_comment_opportunities(blog_result):
                logger.debug(f"No valid comment opportunities: {blog_result.url}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error for {getattr(blog_result, 'url', 'unknown')}: {str(e)}")
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format and accessibility
        """
        if not url or not isinstance(url, str):
            return False
        
        # Check URL format
        if not validators.url(url):
            return False
        
        # Check for excluded file extensions
        url_lower = url.lower()
        for pattern in self.excluded_patterns:
            if re.search(pattern, url_lower):
                return False
        
        # Must be HTTP or HTTPS
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        
        return True
    
    def _is_valid_domain(self, domain: str) -> bool:
        """
        Validate domain and check against exclusion list
        """
        if not domain or not isinstance(domain, str):
            return False
        
        domain_lower = domain.lower().strip()
        
        # Check against excluded domains
        if domain_lower in self.excluded_domains:
            return False
        
        # Check for partial matches with excluded domains
        for excluded in self.excluded_domains:
            if excluded in domain_lower or domain_lower in excluded:
                return False
        
        # Basic domain format validation
        if not validators.domain(domain_lower):
            return False
        
        return True
    
    def _has_sufficient_content(self, blog_result) -> bool:
        """
        Check if the blog result has sufficient content quality
        """
        # Check title length
        title = getattr(blog_result, 'title', '') or ''
        if len(title.strip()) < self.min_title_length:
            return False
        
        # Check description length
        description = getattr(blog_result, 'description', '') or ''
        if len(description.strip()) < self.min_description_length:
            return False
        
        # Check quality score if available
        quality_score = getattr(blog_result, 'content_quality_score', None)
        if quality_score is not None and quality_score < self.min_quality_score:
            return False
        
        # Check for spammy patterns in title and description
        combined_text = f"{title} {description}".lower()
        spam_indicators = [
            'buy now', 'click here', 'limited time', 'special offer',
            'guarantee', 'free money', 'work from home', 'lose weight fast'
        ]
        
        spam_count = sum(1 for indicator in spam_indicators if indicator in combined_text)
        if spam_count > 2:  # Too many spam indicators
            return False
        
        return True
    
    def _has_valid_authority_scores(self, blog_result) -> bool:
        """
        Validate authority scores if present
        """
        domain_authority = getattr(blog_result, 'domain_authority', None)
        page_authority = getattr(blog_result, 'page_authority', None)
        
        # If scores are present, they should be reasonable
        if domain_authority is not None:
            if not isinstance(domain_authority, (int, float)) or domain_authority < 0 or domain_authority > 100:
                return False
        
        if page_authority is not None:
            if not isinstance(page_authority, (int, float)) or page_authority < 0 or page_authority > 100:
                return False
        
        return True
    
    def _has_comment_opportunities(self, blog_result) -> bool:
        """
        Check if there are valid comment opportunities
        """
        opportunities = getattr(blog_result, 'comment_opportunities', None)
        
        if not opportunities:
            return False
        
        if not isinstance(opportunities, list):
            return False
        
        if len(opportunities) == 0:
            return False
        
        # Check that opportunities are meaningful strings
        valid_opportunities = [
            opp for opp in opportunities 
            if isinstance(opp, str) and len(opp.strip()) > 5
        ]
        
        return len(valid_opportunities) > 0
    
    def clean_blog_result(self, blog_result) -> Optional[Any]:
        """
        Clean and normalize a blog result object
        """
        try:
            # Clean title
            if hasattr(blog_result, 'title') and blog_result.title:
                blog_result.title = self._clean_text(blog_result.title)
            
            # Clean description
            if hasattr(blog_result, 'description') and blog_result.description:
                blog_result.description = self._clean_text(blog_result.description)
            
            # Clean author name
            if hasattr(blog_result, 'author') and blog_result.author:
                blog_result.author = self._clean_text(blog_result.author)
            
            # Normalize URL
            if hasattr(blog_result, 'url') and blog_result.url:
                blog_result.url = blog_result.url.strip()
            
            # Clean comment opportunities
            if hasattr(blog_result, 'comment_opportunities') and blog_result.comment_opportunities:
                cleaned_opportunities = []
                for opp in blog_result.comment_opportunities:
                    if isinstance(opp, str):
                        cleaned_opp = self._clean_text(opp)
                        if len(cleaned_opp) > 5:
                            cleaned_opportunities.append(cleaned_opp)
                blog_result.comment_opportunities = cleaned_opportunities
            
            return blog_result
            
        except Exception as e:
            logger.error(f"Error cleaning blog result: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        # Remove or replace smart quotes and other special characters
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('…', '...')
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics and configuration
        """
        return {
            'min_title_length': self.min_title_length,
            'min_description_length': self.min_description_length,
            'min_quality_score': self.min_quality_score,
            'excluded_domains_count': len(self.excluded_domains),
            'excluded_patterns_count': len(self.excluded_patterns)
        }
