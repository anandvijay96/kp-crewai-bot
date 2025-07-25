"""
BlogValidatorTool - Blog validation and quality assessment

This tool specializes in:
- Validating blog eligibility for commenting
- Assessing blog quality and authority
- Checking comment policy and guidelines
- Evaluating commenting opportunities and risks
- Integration with CrewAI for automated blog assessment
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, urljoin
from crewai.tools import BaseTool
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

# Module-level constants to avoid Pydantic issues
AUTHORITY_INDICATORS = {
    'high_authority': ['wikipedia', 'harvard', 'stanford', 'mit', 'gov', 'edu'],
    'medium_authority': ['forbes', 'entrepreneur', 'inc', 'techcrunch', 'mashable'],
    'blacklisted': ['spam', 'adult', 'gambling', 'pharmacy', 'loan']
}

COMMENT_SYSTEMS = [
    'disqus', 'facebook', 'wordpress', 'livefyre', 'intensedebate',
    'commentluv', 'jetpack', 'wpcomments'
]

SPAM_INDICATORS = [
    'free', 'discount', 'limited time', 'click here', 'buy now',
    'guaranteed', 'make money', 'work from home', 'get rich'
]


class BlogValidatorTool(BaseTool):
    """
    CrewAI tool for comprehensive blog validation and assessment
    
    Capabilities:
    - Blog quality and authority scoring
    - Comment policy analysis  
    - Technical validation (loading speed, mobile-friendly)
    - Spam risk assessment
    - Comment opportunity evaluation
    """
    
    name: str = "blog_validator_tool"
    description: str = """
    Validate and assess blogs for commenting opportunities and quality.
    
    This tool can:
    - Evaluate blog authority and quality metrics
    - Check comment policies and guidelines
    - Assess technical factors (speed, mobile-friendly)
    - Identify spam risks and blacklisted domains
    - Score commenting opportunities and success potential
    
    Input: Blog URL (string)
    Output: Comprehensive validation report with scores and recommendations
    """
    
    def __init__(self):
        super().__init__()
        # Use module-level constants to avoid Pydantic issues
    
    def _run(self, blog_url: str) -> Dict[str, Any]:
        """
        Main execution method for blog validation
        
        Args:
            blog_url: The URL of the blog to validate
            
        Returns:
            Dictionary containing comprehensive validation results
        """
        try:
            # Basic URL validation
            url_validation = self._validate_url(blog_url)
            if not url_validation['is_valid']:
                return {
                    'success': False,
                    'error': 'Invalid URL',
                    'url_validation': url_validation,
                    'overall_score': 0
                }
            
            # Fetch blog content
            content_result = self._fetch_blog_content(blog_url)
            if not content_result['success']:
                return {
                    'success': False,
                    'error': content_result['error'],
                    'url_validation': url_validation,
                    'overall_score': 0
                }
            
            html_content = content_result['content']
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Perform comprehensive validation
            authority_score = self._assess_authority(blog_url, soup)
            quality_metrics = self._evaluate_quality_metrics(soup, html_content)
            comment_analysis = self._analyze_comment_system(soup, html_content)
            technical_factors = self._check_technical_factors(blog_url, html_content)
            spam_risk = self._assess_spam_risk(soup, blog_url)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                authority_score, quality_metrics, comment_analysis, 
                technical_factors, spam_risk
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                authority_score, quality_metrics, comment_analysis, spam_risk
            )
            
            return {
                'success': True,
                'blog_url': blog_url,
                'url_validation': url_validation,
                'authority_score': authority_score,
                'quality_metrics': quality_metrics,
                'comment_analysis': comment_analysis,
                'technical_factors': technical_factors,
                'spam_risk': spam_risk,
                'overall_score': overall_score,
                'recommendations': recommendations,
                'is_suitable': overall_score >= 60,
                'risk_level': self._determine_risk_level(spam_risk, overall_score)
            }
            
        except Exception as e:
            logging.error(f"Blog validation failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'blog_url': blog_url,
                'overall_score': 0,
                'is_suitable': False,
                'risk_level': 'high'
            }
    
    def _validate_url(self, url: str) -> Dict[str, Any]:
        """Validate URL format and accessibility"""
        try:
            parsed = urlparse(url)
            
            is_valid = bool(parsed.netloc and parsed.scheme in ['http', 'https'])
            domain = parsed.netloc.lower()
            
            # Check against blacklisted domains
            is_blacklisted = any(
                indicator in domain 
                for indicator in AUTHORITY_INDICATORS['blacklisted']
            )
            
            return {
                'is_valid': is_valid and not is_blacklisted,
                'domain': domain,
                'scheme': parsed.scheme,
                'is_blacklisted': is_blacklisted,
                'is_secure': parsed.scheme == 'https'
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'domain': '',
                'scheme': '',
                'is_blacklisted': True,
                'is_secure': False
            }
    
    def _fetch_blog_content(self, url: str) -> Dict[str, Any]:
        """Fetch blog content with error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'content': response.text,
                'status_code': response.status_code,
                'content_length': len(response.text),
                'response_time': response.elapsed.total_seconds()
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'status_code': 0,
                'content_length': 0,
                'response_time': 0
            }
    
    def _assess_authority(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Assess blog authority and credibility"""
        domain = urlparse(url).netloc.lower()
        
        # Domain authority indicators
        authority_level = 'low'
        authority_score = 30
        
        for level, indicators in AUTHORITY_INDICATORS.items():
            if level == 'blacklisted':
                continue
                
            for indicator in indicators:
                if indicator in domain:
                    authority_level = level
                    authority_score = 90 if level == 'high_authority' else 70
                    break
        
        # Content quality indicators
        content_indicators = {
            'has_author': bool(soup.find(['div', 'span'], class_=re.compile(r'author', re.I))),
            'has_date': bool(soup.find(['time', 'div', 'span'], class_=re.compile(r'date|time', re.I))),
            'has_categories': bool(soup.find(['div', 'span'], class_=re.compile(r'categor|tag', re.I))),
            'has_about_page': bool(soup.find('a', href=re.compile(r'about', re.I))),
            'has_contact_page': bool(soup.find('a', href=re.compile(r'contact', re.I)))
        }
        
        # Adjust score based on content indicators
        indicator_bonus = sum(5 for indicator in content_indicators.values() if indicator)
        authority_score = min(100, authority_score + indicator_bonus)
        
        return {
            'domain_authority': authority_level,
            'authority_score': authority_score,
            'content_indicators': content_indicators,
            'is_credible': authority_score >= 60
        }
    
    def _evaluate_quality_metrics(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """Evaluate blog quality metrics"""
        
        # Content length and structure
        text_content = soup.get_text(strip=True)
        word_count = len(text_content.split())
        
        # Header structure
        headers = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
        has_proper_structure = sum(headers.values()) > 0
        
        # Images and media
        images = soup.find_all('img')
        images_with_alt = sum(1 for img in images if img.get('alt'))
        
        # External links
        external_links = len([
            link for link in soup.find_all('a', href=True)
            if link['href'].startswith('http') and urlparse(link['href']).netloc != urlparse(soup.base['href'] if soup.base else '').netloc
        ])
        
        # Social media presence
        social_links = len([
            link for link in soup.find_all('a', href=True)
            if any(social in link['href'].lower() for social in ['twitter', 'facebook', 'instagram', 'linkedin'])
        ])
        
        # Calculate quality score
        quality_score = 0
        
        # Word count scoring
        if 300 <= word_count <= 3000:
            quality_score += 25
        elif word_count > 100:
            quality_score += 15
        
        # Structure scoring
        if has_proper_structure:
            quality_score += 20
        
        # Media scoring
        if len(images) > 0:
            quality_score += 10
            if images_with_alt / len(images) > 0.5:
                quality_score += 10
        
        # Link scoring
        if external_links > 0:
            quality_score += 15
        
        # Social presence scoring
        if social_links > 0:
            quality_score += 20
        
        return {
            'word_count': word_count,
            'header_structure': headers,
            'has_proper_structure': has_proper_structure,
            'image_count': len(images),
            'images_with_alt': images_with_alt,
            'external_links': external_links,
            'social_links': social_links,
            'quality_score': min(100, quality_score),
            'is_high_quality': quality_score >= 70
        }
    
    def _analyze_comment_system(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """Analyze comment system and policies"""
        
        # Detect comment system
        detected_system = None
        for system in COMMENT_SYSTEMS:
            if system.lower() in html_content.lower():
                detected_system = system
                break
        
        # Look for comment forms
        comment_forms = soup.find_all('form', id=re.compile(r'comment', re.I))
        comment_textareas = soup.find_all('textarea', {'name': re.compile(r'comment', re.I)})
        
        has_comment_form = len(comment_forms) > 0 or len(comment_textareas) > 0
        
        # Look for existing comments
        comment_sections = soup.find_all(['div', 'section'], class_=re.compile(r'comment', re.I))
        comment_count = len(comment_sections)
        
        # Check for comment policy
        policy_keywords = ['comment policy', 'commenting guidelines', 'comment rules']
        has_comment_policy = any(keyword in html_content.lower() for keyword in policy_keywords)
        
        # Check for moderation indicators
        moderation_keywords = ['moderated', 'approval', 'review before', 'pending approval']
        is_moderated = any(keyword in html_content.lower() for keyword in moderation_keywords)
        
        # Calculate comment opportunity score
        opportunity_score = 0
        
        if has_comment_form:
            opportunity_score += 40
        
        if detected_system:
            opportunity_score += 30
        
        if comment_count > 0:
            opportunity_score += 20
        
        if not is_moderated:
            opportunity_score += 10
        
        return {
            'detected_system': detected_system,
            'has_comment_form': has_comment_form,
            'comment_count': comment_count,
            'has_comment_policy': has_comment_policy,
            'is_moderated': is_moderated,
            'opportunity_score': min(100, opportunity_score),
            'allows_comments': has_comment_form or detected_system is not None
        }
    
    def _check_technical_factors(self, url: str, html_content: str) -> Dict[str, Any]:
        """Check technical factors affecting commenting"""
        
        # Page size
        page_size_kb = len(html_content.encode('utf-8')) / 1024
        
        # Mobile viewport
        soup = BeautifulSoup(html_content, 'html.parser')
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        is_mobile_friendly = viewport_meta is not None
        
        # HTTPS check
        is_secure = url.startswith('https://')
        
        # Check for common CMS
        cms_indicators = {
            'wordpress': 'wp-content' in html_content or 'wordpress' in html_content.lower(),
            'drupal': 'drupal' in html_content.lower() or '/sites/default/' in html_content,
            'joomla': 'joomla' in html_content.lower() or 'option=com_' in html_content,
            'blogger': 'blogger' in html_content.lower() or 'blogspot' in url,
            'medium': 'medium.com' in url or 'medium-' in html_content
        }
        
        detected_cms = next((cms for cms, detected in cms_indicators.items() if detected), None)
        
        # Technical score
        technical_score = 50  # Base score
        
        if page_size_kb < 500:  # Under 500KB is good
            technical_score += 15
        elif page_size_kb < 1000:  # Under 1MB is acceptable
            technical_score += 10
        
        if is_mobile_friendly:
            technical_score += 20
        
        if is_secure:
            technical_score += 15
        
        return {
            'page_size_kb': round(page_size_kb, 2),
            'is_mobile_friendly': is_mobile_friendly,
            'is_secure': is_secure,
            'detected_cms': detected_cms,
            'technical_score': min(100, technical_score),
            'is_technically_sound': technical_score >= 70
        }
    
    def _assess_spam_risk(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Assess spam risk factors"""
        
        text_content = soup.get_text().lower()
        domain = urlparse(url).netloc.lower()
        
        # Check for spam indicators in content
        spam_count = sum(1 for indicator in SPAM_INDICATORS if indicator in text_content)
        
        # Check domain reputation
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.info', '.biz']
        has_suspicious_tld = any(tld in domain for tld in suspicious_tlds)
        
        # Check for excessive ads
        ad_indicators = ['advertisement', 'sponsored', 'adsense', 'google_ads']
        ad_count = sum(1 for indicator in ad_indicators if indicator in text_content)
        
        # Check for poor grammar/spelling (simple heuristic)
        common_misspellings = ['teh', 'recieve', 'seperate', 'occured', 'acheive']
        misspelling_count = sum(1 for error in common_misspellings if error in text_content)
        
        # Calculate risk score
        risk_score = 0
        
        risk_score += spam_count * 10
        risk_score += 20 if has_suspicious_tld else 0
        risk_score += ad_count * 5
        risk_score += misspelling_count * 3
        
        risk_level = 'low'
        if risk_score > 50:
            risk_level = 'high'
        elif risk_score > 20:
            risk_level = 'medium'
        
        return {
            'spam_indicators': spam_count,
            'has_suspicious_tld': has_suspicious_tld,
            'ad_indicators': ad_count,
            'misspelling_count': misspelling_count,
            'risk_score': min(100, risk_score),
            'risk_level': risk_level,
            'is_safe': risk_level in ['low', 'medium']
        }
    
    def _calculate_overall_score(
        self,
        authority: Dict[str, Any],
        quality: Dict[str, Any],
        comments: Dict[str, Any],
        technical: Dict[str, Any],
        spam_risk: Dict[str, Any]
    ) -> float:
        """Calculate weighted overall score"""
        
        # Weight the different factors
        weights = {
            'authority': 0.25,
            'quality': 0.25,
            'comments': 0.30,
            'technical': 0.10,
            'spam_safety': 0.10
        }
        
        # Get scores
        authority_score = authority.get('authority_score', 0)
        quality_score = quality.get('quality_score', 0)
        comment_score = comments.get('opportunity_score', 0)
        technical_score = technical.get('technical_score', 0)
        spam_safety_score = 100 - spam_risk.get('risk_score', 0)  # Invert risk score
        
        # Calculate weighted average
        overall_score = (
            authority_score * weights['authority'] +
            quality_score * weights['quality'] +
            comment_score * weights['comments'] +
            technical_score * weights['technical'] +
            spam_safety_score * weights['spam_safety']
        )
        
        return round(min(100, max(0, overall_score)), 2)
    
    def _generate_recommendations(
        self,
        authority: Dict[str, Any],
        quality: Dict[str, Any],
        comments: Dict[str, Any],
        spam_risk: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Authority recommendations
        if authority.get('authority_score', 0) < 60:
            recommendations.append("Consider targeting higher authority blogs for better credibility")
        
        # Quality recommendations
        if not quality.get('is_high_quality', False):
            recommendations.append("Blog quality is moderate - ensure comments add significant value")
        
        # Comment system recommendations
        if not comments.get('allows_comments', False):
            recommendations.append("Blog doesn't appear to allow comments - verify before proceeding")
        elif comments.get('is_moderated', False):
            recommendations.append("Comments are moderated - expect potential delays in approval")
        
        # Spam risk recommendations
        if spam_risk.get('risk_level') == 'high':
            recommendations.append("High spam risk detected - avoid this blog")
        elif spam_risk.get('risk_level') == 'medium':
            recommendations.append("Medium spam risk - proceed with caution and extra quality checks")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Blog appears suitable for commenting - proceed with high-quality content")
        
        return recommendations
    
    def _determine_risk_level(self, spam_risk: Dict[str, Any], overall_score: float) -> str:
        """Determine overall risk level"""
        
        spam_level = spam_risk.get('risk_level', 'high')
        
        if spam_level == 'high' or overall_score < 40:
            return 'high'
        elif spam_level == 'medium' or overall_score < 60:
            return 'medium'
        else:
            return 'low'
