"""
BlogResearcher Agent

This agent discovers and validates high-value blogs for comment opportunities.
It searches for blogs by keywords/topics, validates blog authority and engagement,
checks comment policies, and identifies recent posts.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import re

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool

from .base_agent import BaseAgent
from ..utils.database import Blog, BlogPost, db_manager


class BlogSearchTool(BaseTool):
    """Tool for searching blogs using various search engines and methods."""
    
    name: str = "blog_search_tool"
    description: str = "Search for blogs by keywords and topics"
    
    def _run(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for blogs using multiple methods.
        
        Args:
            query: Search query with keywords
            max_results: Maximum number of results to return
            
        Returns:
            List of discovered blog information
        """
        results = []
        
        try:
            # Method 1: Use Google search with site-specific queries for blog platforms
            blog_platforms = [
                "site:medium.com",
                "site:dev.to", 
                "site:hashnode.com",
                "site:substack.com",
                "inurl:blog",
                "inurl:wordpress.com",
                "inurl:blogspot.com"
            ]
            
            for platform in blog_platforms[:3]:  # Limit to prevent too many requests
                platform_results = self._google_search(f"{query} {platform}", max_results//3)
                results.extend(platform_results)
                
            # Method 2: Direct blog directory search (simulated)
            directory_results = self._blog_directory_search(query, max_results//2)
            results.extend(directory_results)
            
            # Remove duplicates and limit results
            seen_domains = set()
            unique_results = []
            
            for result in results:
                domain = urlparse(result.get('url', '')).netloc
                if domain not in seen_domains and len(unique_results) < max_results:
                    seen_domains.add(domain)
                    unique_results.append(result)
            
            return unique_results[:max_results]
            
        except Exception as e:
            logging.error(f"Blog search failed: {e}")
            return []
    
    def _google_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Simulate Google search results for blogs."""
        # In a real implementation, this would use Google Custom Search API
        # For now, we'll return mock data with realistic blog information
        
        mock_results = [
            {
                "url": "https://cloudcomputing.example.com/blog",
                "title": "Cloud Computing Insights Blog",
                "description": "Latest insights and trends in cloud computing, DevOps, and infrastructure.",
                "domain": "cloudcomputing.example.com",
                "estimated_authority": 75,
                "platform": "custom"
            },
            {
                "url": "https://medium.com/@techexpert/cloud-infrastructure",
                "title": "Cloud Infrastructure Best Practices - Medium",
                "description": "Comprehensive guide to cloud infrastructure and automation.",
                "domain": "medium.com",
                "estimated_authority": 85,
                "platform": "medium"
            },
            {
                "url": "https://dev.to/cloudarchitect/devops-automation",
                "title": "DevOps Automation Strategies - DEV Community",
                "description": "Modern DevOps practices and automation techniques.",
                "domain": "dev.to", 
                "estimated_authority": 80,
                "platform": "dev.to"
            }
        ]
        
        # Filter results based on query keywords
        query_lower = query.lower()
        filtered_results = []
        
        for result in mock_results:
            if any(keyword in result['title'].lower() or keyword in result['description'].lower() 
                   for keyword in query_lower.split()):
                filtered_results.append(result)
        
        return filtered_results[:max_results]
    
    def _blog_directory_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search blog directories and aggregators."""
        # Simulate blog directory results
        mock_directory_results = [
            {
                "url": "https://techblog.example.org/",
                "title": "TechBlog - Technology Insights",
                "description": "In-depth technology articles and tutorials.",
                "domain": "techblog.example.org",
                "estimated_authority": 70,
                "platform": "wordpress"
            },
            {
                "url": "https://cloudnative.example.io/blog",
                "title": "Cloud Native Blog",
                "description": "Cloud native technologies and Kubernetes insights.",
                "domain": "cloudnative.example.io",
                "estimated_authority": 78,
                "platform": "custom"
            }
        ]
        
        return mock_directory_results[:max_results]


class BlogAnalysisTool(BaseTool):
    """Tool for analyzing blog characteristics and comment policies."""
    
    name: str = "blog_analysis_tool"
    description: str = "Analyze blog for authority, engagement, and comment policies"
    
    def _run(self, blog_url: str) -> Dict[str, Any]:
        """
        Analyze a blog for commenting opportunities.
        
        Args:
            blog_url: URL of the blog to analyze
            
        Returns:
            Blog analysis results
        """
        try:
            # Fetch blog homepage
            response = requests.get(blog_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch blog: {response.status_code}"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                "url": blog_url,
                "domain": urlparse(blog_url).netloc,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "platform": self._detect_platform(soup, blog_url),
                "has_comments": self._check_comments_enabled(soup),
                "comment_policy": self._analyze_comment_policy(soup),
                "recent_posts": self._find_recent_posts(soup, blog_url),
                "social_presence": self._check_social_presence(soup),
                "estimated_authority": self._estimate_authority(soup, blog_url),
                "content_quality": self._assess_content_quality(soup),
                "posting_frequency": self._estimate_posting_frequency(soup),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logging.error(f"Blog analysis failed for {blog_url}: {e}")
            return {"error": str(e), "url": blog_url}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract blog title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Unknown Blog"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract blog description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Try to find tagline or subtitle
        tagline = soup.find(['p', 'div'], class_=re.compile(r'tagline|subtitle|description'))
        if tagline:
            return tagline.get_text().strip()
        
        return ""
    
    def _detect_platform(self, soup: BeautifulSoup, url: str) -> str:
        """Detect blogging platform."""
        url_lower = url.lower()
        
        if 'wordpress' in url_lower or soup.find('meta', attrs={'name': 'generator', 'content': re.compile(r'WordPress')}):
            return "wordpress"
        elif 'medium.com' in url_lower:
            return "medium"
        elif 'dev.to' in url_lower:
            return "dev.to"
        elif 'hashnode' in url_lower:
            return "hashnode"
        elif 'substack' in url_lower:
            return "substack"
        elif 'ghost.org' in url_lower or soup.find('meta', attrs={'name': 'generator', 'content': re.compile(r'Ghost')}):
            return "ghost"
        else:
            return "custom"
    
    def _check_comments_enabled(self, soup: BeautifulSoup) -> bool:
        """Check if comments are enabled on the blog."""
        # Look for common comment indicators
        comment_indicators = [
            'comment-form',
            'comments-section', 
            'disqus',
            'wp-comment',
            'comment-respond',
            'utterances'
        ]
        
        for indicator in comment_indicators:
            if soup.find(attrs={'class': re.compile(indicator, re.I)}) or \
               soup.find(attrs={'id': re.compile(indicator, re.I)}):
                return True
        
        # Check for comment-related text
        if soup.find(text=re.compile(r'leave\s+a\s+comment|post\s+comment|add\s+comment', re.I)):
            return True
        
        return False
    
    def _analyze_comment_policy(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze comment policy and moderation."""
        policy = {
            "moderation": "unknown",
            "registration_required": False,
            "guidelines_found": False,
            "policy_text": ""
        }
        
        # Look for comment policy text
        policy_keywords = ['comment policy', 'commenting guidelines', 'moderation policy']
        
        for keyword in policy_keywords:
            policy_element = soup.find(text=re.compile(keyword, re.I))
            if policy_element:
                policy["guidelines_found"] = True
                # Try to extract nearby text
                parent = policy_element.parent if policy_element.parent else None
                if parent:
                    policy["policy_text"] = parent.get_text()[:200] + "..."
                break
        
        # Check for registration requirements
        if soup.find(text=re.compile(r'login|register|sign\s+in.*comment', re.I)):
            policy["registration_required"] = True
        
        return policy
    
    def _find_recent_posts(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Find recent blog posts."""
        posts = []
        
        # Look for common post link patterns
        post_links = soup.find_all('a', href=re.compile(r'/blog/|/post/|/\d{4}/'))
        
        for link in post_links[:5]:  # Limit to 5 recent posts
            href = link.get('href', '')
            if href.startswith('/'):
                href = urljoin(base_url, href)
            
            title = link.get_text().strip()
            if title and len(title) > 10:  # Filter out short/empty titles
                posts.append({
                    "url": href,
                    "title": title[:100] + ("..." if len(title) > 100 else "")
                })
        
        return posts
    
    def _check_social_presence(self, soup: BeautifulSoup) -> Dict[str, bool]:
        """Check for social media presence."""
        social_platforms = {
            "twitter": False,
            "linkedin": False, 
            "facebook": False,
            "github": False
        }
        
        # Look for social media links
        social_links = soup.find_all('a', href=re.compile(r'twitter\.com|linkedin\.com|facebook\.com|github\.com'))
        
        for link in social_links:
            href = link.get('href', '').lower()
            for platform in social_platforms:
                if platform in href:
                    social_platforms[platform] = True
        
        return social_platforms
    
    def _estimate_authority(self, soup: BeautifulSoup, url: str) -> int:
        """Estimate blog authority score."""
        score = 50  # Base score
        
        # Domain age and authority (simulated)
        domain = urlparse(url).netloc
        if any(platform in domain for platform in ['medium.com', 'dev.to', 'hashnode.com']):
            score += 20
        
        # Content quality indicators
        if len(soup.get_text()) > 5000:  # Substantial content
            score += 10
        
        # Social presence
        social_links = len(soup.find_all('a', href=re.compile(r'twitter\.com|linkedin\.com|facebook\.com')))
        score += min(social_links * 5, 15)
        
        # Comment engagement
        if self._check_comments_enabled(soup):
            score += 10
        
        return min(score, 100)
    
    def _assess_content_quality(self, soup: BeautifulSoup) -> str:
        """Assess overall content quality."""
        text_content = soup.get_text()
        word_count = len(text_content.split())
        
        if word_count > 2000:
            return "high"
        elif word_count > 500:
            return "medium"
        else:
            return "low"
    
    def _estimate_posting_frequency(self, soup: BeautifulSoup) -> str:
        """Estimate how frequently the blog posts."""
        # This is a simplified estimation
        # In a real implementation, you'd analyze post dates
        
        date_patterns = soup.find_all(text=re.compile(r'\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2},\s+\d{4}'))
        
        if len(date_patterns) > 10:
            return "high"  # Multiple recent dates found
        elif len(date_patterns) > 3:
            return "medium"
        else:
            return "low"


class BlogResearcher(BaseAgent):
    """
    BlogResearcher Agent - Discovers and validates high-value blogs for comment opportunities.
    
    This agent:
    1. Searches for blogs by keywords/topics
    2. Validates blog authority and engagement
    3. Checks comment policies and requirements  
    4. Identifies recent posts with comment opportunities
    5. Stores blog data for future reference
    """
    
    def __init__(self):
        # Initialize tools
        tools = [
            BlogSearchTool(),
            BlogAnalysisTool()
        ]
        
        super().__init__(
            name="BlogResearcher",
            role="SEO Blog Discovery Specialist",
            goal="Discover and validate high-value blogs with active comment sections for SEO engagement opportunities",
            backstory="""You are an expert at finding valuable blogs in specific niches. 
            You have deep knowledge of blog platforms, SEO metrics, and content quality indicators.
            Your expertise helps identify blogs where meaningful engagement can build brand awareness 
            and drive traffic back to KloudPortal. You understand the importance of finding blogs 
            with active communities, clear comment policies, and content relevant to cloud computing and DevOps.""",
            tools=tools,
            model_name="gemini-2.0-flash-exp"
        )
    
    def _execute_task(self, task: str, context: Dict[str, Any] = None) -> Any:
        """
        Execute blog research task.
        
        Args:
            task: Task description (should include keywords and parameters)
            context: Additional context like target keywords, max results, etc.
            
        Returns:
            Research results with discovered and analyzed blogs
        """
        try:
            # Parse task parameters
            keywords = context.get('keywords', '') if context else ''
            max_results = context.get('max_results', 10) if context else 10
            min_authority = context.get('min_authority', 60) if context else 60
            
            if not keywords:
                # Try to extract keywords from task description
                keywords = self._extract_keywords_from_task(task)
            
            self.logger.info(f"Starting blog research for keywords: {keywords}")
            
            # Step 1: Search for blogs
            search_results = self._search_blogs(keywords, max_results * 2)  # Get more to filter
            
            # Step 2: Analyze each blog
            analyzed_blogs = []
            for blog_info in search_results:
                analysis = self._analyze_blog(blog_info['url'])
                if analysis and not analysis.get('error'):
                    # Combine search info with analysis
                    combined_info = {**blog_info, **analysis}
                    analyzed_blogs.append(combined_info)
            
            # Step 3: Filter by quality criteria
            qualified_blogs = self._filter_qualified_blogs(analyzed_blogs, min_authority)
            
            # Step 4: Store in database
            stored_blogs = self._store_blogs(qualified_blogs)
            
            # Step 5: Prepare final results
            results = {
                "search_keywords": keywords,
                "total_discovered": len(search_results),
                "total_analyzed": len(analyzed_blogs),
                "qualified_blogs": len(qualified_blogs),
                "stored_count": stored_blogs,
                "blogs": qualified_blogs[:max_results],
                "summary": self._generate_summary(qualified_blogs)
            }
            
            self.logger.info(f"Blog research completed: {qualified_blogs} qualified blogs found")
            return results
            
        except Exception as e:
            self.logger.error(f"Blog research task failed: {e}")
            raise
    
    def _extract_keywords_from_task(self, task: str) -> str:
        """Extract keywords from task description."""
        # Simple keyword extraction
        task_lower = task.lower()
        
        # Common tech keywords to look for
        tech_keywords = [
            'cloud computing', 'devops', 'kubernetes', 'docker', 'aws', 'azure',
            'microservices', 'serverless', 'infrastructure', 'automation',
            'ci/cd', 'monitoring', 'logging', 'security', 'scalability'
        ]
        
        found_keywords = []
        for keyword in tech_keywords:
            if keyword in task_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            return ' '.join(found_keywords)
        
        # Default fallback
        return 'cloud computing devops'
    
    def _search_blogs(self, keywords: str, max_results: int) -> List[Dict[str, Any]]:
        """Search for blogs using the blog search tool."""
        search_tool = BlogSearchTool()
        return search_tool._run(keywords, max_results)
    
    def _analyze_blog(self, blog_url: str) -> Dict[str, Any]:
        """Analyze a blog using the blog analysis tool."""
        analysis_tool = BlogAnalysisTool()
        return analysis_tool._run(blog_url)
    
    def _filter_qualified_blogs(self, blogs: List[Dict[str, Any]], min_authority: int) -> List[Dict[str, Any]]:
        """Filter blogs based on quality criteria."""
        qualified = []
        
        for blog in blogs:
            # Check authority score
            if blog.get('estimated_authority', 0) < min_authority:
                continue
            
            # Check if comments are enabled
            if not blog.get('has_comments', False):
                continue
            
            # Check content quality
            if blog.get('content_quality') == 'low':
                continue
            
            # Calculate qualification score
            score = self._calculate_qualification_score(blog)
            blog['qualification_score'] = score
            
            qualified.append(blog)
        
        # Sort by qualification score
        qualified.sort(key=lambda x: x.get('qualification_score', 0), reverse=True)
        
        return qualified
    
    def _calculate_qualification_score(self, blog: Dict[str, Any]) -> int:
        """Calculate overall qualification score for a blog."""
        score = 0
        
        # Authority score (0-100)
        score += blog.get('estimated_authority', 0)
        
        # Comment availability
        if blog.get('has_comments'):
            score += 20
        
        # Content quality bonus
        quality = blog.get('content_quality', 'low')
        if quality == 'high':
            score += 15
        elif quality == 'medium':
            score += 10
        
        # Social presence bonus
        social = blog.get('social_presence', {})
        social_count = sum(1 for platform, present in social.items() if present)
        score += social_count * 5
        
        # Posting frequency bonus
        frequency = blog.get('posting_frequency', 'low')
        if frequency == 'high':
            score += 10
        elif frequency == 'medium':
            score += 5
        
        # Recent posts bonus
        recent_posts = blog.get('recent_posts', [])
        score += min(len(recent_posts) * 2, 10)
        
        return score
    
    def _store_blogs(self, blogs: List[Dict[str, Any]]) -> int:
        """Store qualified blogs in database."""
        if not self.db_session:
            self.logger.warning("No database session available, skipping storage")
            return 0
        
        stored_count = 0
        
        for blog_data in blogs:
            try:
                # Check if blog already exists
                existing_blog = self.db_session.query(Blog).filter_by(
                    url=blog_data['url']
                ).first()
                
                if existing_blog:
                    # Update existing blog
                    existing_blog.domain_authority = blog_data.get('estimated_authority')
                    existing_blog.updated_at = datetime.utcnow()
                else:
                    # Create new blog entry
                    new_blog = Blog(
                        url=blog_data['url'],
                        domain=blog_data['domain'],
                        domain_authority=blog_data.get('estimated_authority'),
                        category='tech',  # Default category
                        status='active'
                    )
                    self.db_session.add(new_blog)
                
                stored_count += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to store blog {blog_data['url']}: {e}")
                continue
        
        try:
            self.db_session.commit()
            self.logger.info(f"Stored {stored_count} blogs in database")
        except Exception as e:
            self.logger.error(f"Failed to commit blog storage: {e}")
            self.db_session.rollback()
            stored_count = 0
        
        return stored_count
    
    def _generate_summary(self, blogs: List[Dict[str, Any]]) -> str:
        """Generate a summary of the research results."""
        if not blogs:
            return "No qualified blogs found matching the criteria."
        
        avg_authority = sum(blog.get('estimated_authority', 0) for blog in blogs) / len(blogs)
        
        platforms = {}
        for blog in blogs:
            platform = blog.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
        
        top_platform = max(platforms.items(), key=lambda x: x[1])[0] if platforms else 'unknown'
        
        comment_enabled_count = sum(1 for blog in blogs if blog.get('has_comments'))
        
        summary = f"""
        Research Summary:
        - Found {len(blogs)} qualified blogs
        - Average authority score: {avg_authority:.1f}
        - Top platform: {top_platform} ({platforms.get(top_platform, 0)} blogs)
        - Blogs with comments enabled: {comment_enabled_count}
        - All blogs meet minimum quality standards for engagement
        """
        
        return summary.strip()


# Export the agent class
__all__ = ['BlogResearcher']
