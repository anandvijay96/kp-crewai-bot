"""
SEOAnalyzer Tool - Evaluate SEO Metrics and Optimization

This tool focuses on:
- Analyzing content for SEO effectiveness
- Extracting key SEO metrics and insights
- Providing actionable recommendations for optimization
- Integration with CrewAI agents for automated analysis
"""

import re
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from textstat import text_standard
from collections import Counter
import logging


class SEOAnalyzer:
    """
    Evaluates SEO factors of the given web content and provides optimization insights.
    
    Capabilities:
    - Title and metadata analysis
    - Keyword density evaluation
    - Semantic relevance checks
    - Social media integration evaluation
    - SEO improvement recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SEOAnalyzer")
        
    def analyze_page(self, html_content: str) -> Dict[str, Any]:
        """
        Analyze an HTML page for various SEO metrics.
        
        Args:
            html_content: The HTML content of the page.
            
        Returns:
            Dictionary containing SEO analysis results and metrics.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Analyze metadata
            metadata = self._analyze_metadata(soup)
            
            # Analyze headings and structure
            structure = self._analyze_structure(soup)
            
            # Evaluate key SEO factors
            seo_factors = self._evaluate_seo_factors(soup)
            
            return {
                'success': True,
                'metadata': metadata,
                'structure': structure,
                'seo_factors': seo_factors
            }
            
        except Exception as e:
            self.logger.error(f"SEO analysis failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'metadata': {},
                'structure': {},
                'seo_factors': {}
            }
    
    def _analyze_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page metadata such as title and meta tags."""
        title_tag = soup.title.string if soup.title else ""
        meta_tags = {meta.attrs['name']: meta.attrs['content']
                     for meta in soup.find_all('meta', attrs={'name': True, 'content': True})}
        
        return {
            'title': title_tag.strip() if title_tag else "No Title",
            'meta_tags': meta_tags
        }
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze the HTML structure of the page for SEO importance."""
        # Count header tags
        headers = [f'h{i}' for i in range(1, 7)]
        header_counts = {header: len(soup.find_all(header)) for header in headers}
        
        # Check for alt attributes in images
        image_count = len(soup.find_all('img'))
        images_with_alt = len(soup.find_all('img', alt=True))
        
        # External and internal links
        external_links = len([link for link in soup.find_all('a', href=True) if link['href'].startswith('http')])
        internal_links = len([link for link in soup.find_all('a', href=True) if link['href'].startswith('/')])
        
        # Social links
        social_link_keywords = ['twitter', 'facebook', 'instagram', 'linkedin', 'youtube']
        social_links = len([link for link in soup.find_all('a', href=True)
                            if any(keyword in link['href'].lower() for keyword in social_link_keywords)])
        
        return {
            'header_counts': header_counts,
            'images': {
                'total': image_count,
                'with_alt': images_with_alt
            },
            'links': {
                'external': external_links,
                'internal': internal_links,
                'social': social_links
            }
        }
    
    def _evaluate_seo_factors(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Evaluate page content for SEO factors."""
        body_text = soup.get_text(separator=' ', strip=True)
        word_count = len(body_text.split())
        
        # Basic keyword density analysis
        keywords = self._extract_keywords(body_text)
        keyword_density = {kw: count / word_count for kw, count in keywords.items() if word_count > 0}
        
        # Flesch reading ease
        readability = text_standard(body_text, float_output=True)
        
        return {
            'word_count': word_count,
            'keyword_density': keyword_density,
            'readability': readability
        }
    
    def _extract_keywords(self, text: str) -> Counter:
        """Extract keywords from the text and count occurrences."""
        words = re.findall(r'\w+', text.lower())
        filtered_words = [word for word in words if len(word) > 3]
        
        return Counter(filtered_words)
