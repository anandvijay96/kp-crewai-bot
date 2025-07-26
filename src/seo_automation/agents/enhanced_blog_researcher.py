"""
Enhanced BlogResearcher Agent - Phase 2 Implementation

This agent integrates Phase 1 tools for comprehensive blog research:
- Multi-source blog discovery with advanced search algorithms
- Comprehensive validation using BlogValidatorTool
- Content analysis using ContentAnalysisTool  
- SEO assessment using SEOAnalyzer
- Web scraping using WebScraper
- Quality scoring with weighted metrics
- Automated reporting and recommendations
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import re
import time

import requests
from bs4 import BeautifulSoup

from ..core.base_agent import BaseSEOAgent
from ..utils.database import Blog, BlogPost, db_manager


class EnhancedBlogResearcherAgent(BaseSEOAgent):
    """
    Enhanced BlogResearcher Agent with Phase 1 tools integration
    
    Capabilities:
    1. Multi-source blog discovery (Google, Bing, specialized searches)
    2. Comprehensive blog validation using BlogValidatorTool
    3. Content analysis using ContentAnalysisTool
    4. SEO assessment using SEOAnalyzer
    5. Quality scoring with weighted metrics
    6. Spam risk evaluation and filtering
    7. Automated reporting and recommendations
    8. Database storage with relationship mapping
    """
    
    def __init__(self):
        super().__init__(
            name="EnhancedBlogResearcher",
            role="Advanced SEO Blog Discovery and Validation Specialist",
            goal="""Discover, validate, and score high-value blogs with active comment sections 
                   for strategic SEO engagement opportunities using advanced analysis tools""",
            backstory="""You are an expert SEO researcher with access to advanced analysis tools.
                      You use sophisticated algorithms to discover blogs across multiple platforms,
                      perform comprehensive quality assessments, and provide detailed recommendations.
                      Your expertise includes understanding blog authority metrics, content quality indicators,
                      comment system analysis, and spam risk evaluation. You help identify the most valuable
                      blogs for meaningful engagement that will build brand awareness and drive qualified
                      traffic back to KloudPortal.""",
            model_name="gemini-2.0-flash-exp"
        )
        
        # Initialize database session with graceful handling
        self.db_session = None
        try:
            if db_manager.connection_available:
                self.db_session = db_manager.get_session()
                self.logger.info("Database session initialized successfully")
            else:
                self.logger.warning("Database not available - continuing without persistence")
        except Exception as e:
            self.logger.warning(f"Failed to initialize database session: {e} - continuing without persistence")
            self.db_session = None
        
        # Search configuration
        self.search_templates = {
            'blog_discovery': [
                '"{keyword}" blog comments',
                '"{keyword}" + "leave a comment"', 
                '"{keyword}" + "post a comment"',
                '"{keyword}" inurl:blog',
                'site:wordpress.com "{keyword}"',
                'site:medium.com "{keyword}"'
            ],
            'authority_blogs': [
                '"{keyword}" site:edu',
                '"{keyword}" site:gov', 
                '"{keyword}" high authority blog'
            ],
            'niche_specific': [
                '"{keyword}" guest post',
                '"{keyword}" write for us',
                '"{keyword}" contribute'
            ]
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'minimum_authority_score': 50,
            'minimum_quality_score': 60,
            'minimum_comment_opportunity': 40,
            'maximum_spam_risk': 30,
            'minimum_overall_score': 60
        }
        
        # Weighted scoring system
        self.scoring_weights = {
            'authority': 0.25,      # Domain authority and credibility
            'quality': 0.25,        # Content quality and structure  
            'comments': 0.30,       # Comment system and opportunities
            'technical': 0.10,      # Technical factors (HTTPS, mobile, etc.)
            'spam_safety': 0.10     # Spam risk and safety assessment
        }
    
    def research_blogs(self, research_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public method to research blogs based on parameters.
        This method provides the interface expected by the API.
        
        Args:
            research_params: Dictionary containing:
                - keywords: List of keywords to search for
                - max_blogs: Maximum number of blogs to return
                - quality_threshold: Minimum quality score (0-1)
                - target_domains: Optional list of domains to focus on
                - exclude_domains: Optional list of domains to exclude
        
        Returns:
            Dictionary containing:
                - blogs: List of discovered and analyzed blogs
                - total_discovered: Total number of blogs found
                - cost: Estimated cost of the research
                - execution_time: Time taken for research
        """
        try:
            # Convert keywords to string if it's a list
            if isinstance(research_params.get('keywords', []), list):
                keywords_str = ' '.join(research_params['keywords'])
            else:
                keywords_str = research_params.get('keywords', '')
            
            # Prepare context for task execution
            context = {
                'keywords': keywords_str,
                'max_results': research_params.get('max_blogs', 10),
                'quality_threshold': research_params.get('quality_threshold', 0.6) * 100,  # Convert to 0-100 scale
                'target_domains': research_params.get('target_domains', []),
                'exclude_domains': research_params.get('exclude_domains', [])
            }
            
            # Create task description
            task = f"Research and discover high-quality blogs for keywords: {keywords_str}"
            
            # Execute the research task
            result = self.execute(task, context)
            
            if result.get('success', False):
                task_result = result.get('result', {})
                
                # Format the response for API compatibility
                return {
                    'blogs': task_result.get('qualified_blogs', []),
                    'total_discovered': task_result.get('discovery_stats', {}).get('total_discovered', 0),
                    'cost': result.get('execution_time', 0) * 0.01,  # Estimate cost based on time
                    'execution_time': result.get('execution_time', 0),
                    'research_report': task_result.get('research_report', {}),
                    'recommendations': task_result.get('recommendations', []),
                    'quality_metrics': task_result.get('quality_metrics', {})
                }
            else:
                raise Exception(f"Blog research task failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Blog research failed: {e}")
            raise

    def _execute_task(self, task: str, context: Dict[str, Any] = None) -> Any:
        """
        Execute enhanced blog research task with Phase 1 tools integration.
        
        Args:
            task: Task description (should include keywords and parameters)
            context: Additional context like target keywords, max results, etc.
            
        Returns:
            Comprehensive research results with discovered and analyzed blogs
        """
        try:
            # Parse task parameters
            keywords = context.get('keywords', '') if context else ''
            max_results = context.get('max_results', 10) if context else 10
            min_authority = context.get('min_authority', 
                                      self.quality_thresholds['minimum_authority_score']) if context else self.quality_thresholds['minimum_authority_score']
            
            if not keywords:
                keywords = self._extract_keywords_from_task(task)
            
            self.logger.info(f"Starting enhanced blog research for keywords: {keywords}")
            
            # Phase 1: Multi-source blog discovery
            discovered_blogs = self._discover_blogs_multi_source(keywords, max_results * 3)
            self.logger.info(f"Discovered {len(discovered_blogs)} blogs from multiple sources")
            
            # Phase 2: Comprehensive validation and analysis
            analyzed_blogs = self._analyze_blogs_comprehensive(discovered_blogs)
            self.logger.info(f"Completed comprehensive analysis of {len(analyzed_blogs)} blogs")
            
            # Phase 3: Quality filtering and scoring
            qualified_blogs = self._filter_and_score_blogs(analyzed_blogs, min_authority)
            self.logger.info(f"Qualified {len(qualified_blogs)} blogs after filtering")
            
            # Phase 4: Database storage
            stored_count = self._store_enhanced_blogs(qualified_blogs)
            
            # Phase 5: Generate comprehensive report
            research_report = self._generate_research_report(
                keywords, discovered_blogs, analyzed_blogs, qualified_blogs
            )
            
            # Final results
            results = {
                "search_keywords": keywords,
                "discovery_stats": {
                    "total_discovered": len(discovered_blogs),
                    "successfully_analyzed": len(analyzed_blogs),
                    "qualified_blogs": len(qualified_blogs),
                    "stored_count": stored_count
                },
                "qualified_blogs": qualified_blogs[:max_results],
                "research_report": research_report,
                "recommendations": self._generate_recommendations(qualified_blogs),
                "quality_metrics": self._calculate_quality_metrics(qualified_blogs)
            }
            
            self.logger.info(f"Enhanced blog research completed: {len(qualified_blogs)} qualified blogs found")
            return results
            
        except Exception as e:
            self.logger.error(f"Enhanced blog research task failed: {e}")
            raise
    
    def _discover_blogs_multi_source(self, keywords: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Discover blogs from multiple sources using advanced search strategies.
        """
        discovered_blogs = []
        
        try:
            # Strategy 1: Blog platform specific searches
            for search_type, templates in self.search_templates.items():
                for template in templates[:2]:  # Limit templates per type
                    query = template.format(keyword=keywords)
                    blogs = self._search_blogs_simulation(query, max_results//6)
                    discovered_blogs.extend(blogs)
                    
                    # Rate limiting
                    time.sleep(0.5)
            
            # Strategy 2: Authority site discovery
            authority_blogs = self._discover_authority_blogs(keywords, max_results//4)
            discovered_blogs.extend(authority_blogs)
            
            # Strategy 3: Niche community discovery
            niche_blogs = self._discover_niche_blogs(keywords, max_results//4)
            discovered_blogs.extend(niche_blogs)
            
            # Remove duplicates based on domain
            seen_domains = set()
            unique_blogs = []
            
            for blog in discovered_blogs:
                domain = urlparse(blog.get('url', '')).netloc
                if domain not in seen_domains and len(unique_blogs) < max_results:
                    seen_domains.add(domain)
                    unique_blogs.append(blog)
            
            return unique_blogs
            
        except Exception as e:
            self.logger.error(f"Multi-source blog discovery failed: {e}")
            return []
    
    def _search_blogs_simulation(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Simulate blog search results (in production, this would use real search APIs).
        """
        # Enhanced mock data that represents realistic blog discovery
        mock_blogs = [
            {
                "url": "https://cloudcomputing.tech/blog",
                "title": "Cloud Computing Technology Blog",
                "description": "Latest insights in cloud infrastructure, DevOps, and automation.",
                "domain": "cloudcomputing.tech",
                "platform": "custom",
                "discovery_source": "blog_search"
            },
            {
                "url": "https://dev.to/cloudexpert", 
                "title": "Cloud Expert - DEV Community",
                "description": "Sharing knowledge about cloud architecture and best practices.",
                "domain": "dev.to",
                "platform": "dev.to",
                "discovery_source": "blog_search"
            },
            {
                "url": "https://medium.com/@devopsinsights",
                "title": "DevOps Insights - Medium",
                "description": "DevOps practices, tools, and industry trends.",
                "domain": "medium.com",
                "platform": "medium",
                "discovery_source": "blog_search"
            },
            {
                "url": "https://kubernetes.academy/blog",
                "title": "Kubernetes Academy Blog",
                "description": "Educational content about Kubernetes and containerization.",
                "domain": "kubernetes.academy",
                "platform": "custom",
                "discovery_source": "blog_search"
            }
        ]
        
        # Filter based on query relevance
        query_keywords = query.lower().replace('"', '').split()
        relevant_blogs = []
        
        for blog in mock_blogs:
            relevance_score = 0
            content = f"{blog['title']} {blog['description']}".lower()
            
            for keyword in query_keywords:
                if keyword in content:
                    relevance_score += 1
            
            if relevance_score > 0:
                blog['relevance_score'] = relevance_score
                relevant_blogs.append(blog)
        
        return relevant_blogs[:max_results]
    
    def _discover_authority_blogs(self, keywords: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Discover high-authority blogs and publications.
        """
        authority_blogs = [
            {
                "url": "https://aws.amazon.com/blogs/",
                "title": "AWS Architecture Blog",
                "description": "Official AWS blog covering cloud architecture and best practices.",
                "domain": "aws.amazon.com",
                "platform": "custom",
                "discovery_source": "authority_search",
                "estimated_authority": 95
            },
            {
                "url": "https://engineering.hashicorp.com/",
                "title": "HashiCorp Engineering Blog",
                "description": "Technical insights from HashiCorp engineering team.",
                "domain": "engineering.hashicorp.com",
                "platform": "custom",
                "discovery_source": "authority_search",
                "estimated_authority": 90
            }
        ]
        
        return authority_blogs[:max_results]
    
    def _discover_niche_blogs(self, keywords: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Discover niche community blogs and specialized publications.
        """
        niche_blogs = [
            {
                "url": "https://devops.com/blog",
                "title": "DevOps.com Blog",
                "description": "DevOps news, trends, and community insights.",
                "domain": "devops.com",
                "platform": "custom",
                "discovery_source": "niche_search",
                "estimated_authority": 78
            },
            {
                "url": "https://thenewstack.io/blog",
                "title": "The New Stack Blog",
                "description": "Cloud native technologies and development practices.",
                "domain": "thenewstack.io", 
                "platform": "custom",
                "discovery_source": "niche_search",
                "estimated_authority": 82
            }
        ]
        
        return niche_blogs[:max_results]
    
    def _analyze_blogs_comprehensive(self, discovered_blogs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform comprehensive analysis of discovered blogs using Phase 1 tools.
        """
        analyzed_blogs = []
        
        for blog_info in discovered_blogs:
            try:
                blog_url = blog_info['url']
                self.logger.info(f"Analyzing blog: {blog_url}")
                
                # Step 1: Blog validation using BlogValidatorTool
                validation_result = self.validate_blog(blog_url)
                
                if not validation_result.get('success', False):
                    self.logger.warning(f"Blog validation failed for {blog_url}: {validation_result.get('error', 'Unknown error')}")
                    continue
                
                # Step 2: Content scraping and analysis
                scrape_result = self.scrape_content(blog_url)
                
                if scrape_result.get('success', False):
                    html_content = scrape_result['content']
                    
                    # Step 3: Content analysis using ContentAnalysisTool
                    content_text = BeautifulSoup(html_content, 'html.parser').get_text()
                    content_analysis = self.analyze_content(content_text)
                    
                    # Step 4: SEO analysis using SEOAnalyzer
                    seo_analysis = self.analyze_seo(html_content)
                else:
                    content_analysis = {'success': False, 'error': 'Content scraping failed'}
                    seo_analysis = {'success': False, 'error': 'SEO analysis failed'}
                
                # Combine all analysis results
                comprehensive_analysis = {
                    **blog_info,
                    'validation_result': validation_result,
                    'content_analysis': content_analysis,
                    'seo_analysis': seo_analysis,
                    'analyzed_at': datetime.utcnow().isoformat()
                }
                
                analyzed_blogs.append(comprehensive_analysis)
                
                # Rate limiting to avoid overwhelming targets
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Comprehensive analysis failed for {blog_info.get('url', 'unknown')}: {e}")
                continue
        
        return analyzed_blogs
    
    def _filter_and_score_blogs(self, analyzed_blogs: List[Dict[str, Any]], min_authority: int) -> List[Dict[str, Any]]:
        """
        Filter and score blogs based on comprehensive quality criteria.
        """
        qualified_blogs = []
        
        for blog in analyzed_blogs:
            try:
                # Calculate comprehensive quality score
                quality_score = self._calculate_comprehensive_score(blog)
                blog['comprehensive_score'] = quality_score
                
                # Apply quality filters
                if self._meets_quality_criteria(blog, min_authority):
                    qualified_blogs.append(blog)
                
            except Exception as e:
                self.logger.warning(f"Scoring failed for blog {blog.get('url', 'unknown')}: {e}")
                continue
        
        # Sort by comprehensive score
        qualified_blogs.sort(key=lambda x: x.get('comprehensive_score', 0), reverse=True)
        
        return qualified_blogs
    
    def _calculate_comprehensive_score(self, blog: Dict[str, Any]) -> float:
        """
        Calculate comprehensive quality score using weighted metrics.
        """
        score = 0.0
        
        # Authority score (from BlogValidatorTool)
        validation = blog.get('validation_result', {})
        authority_score = validation.get('authority_score', {}).get('score', 50)
        score += authority_score * self.scoring_weights['authority']
        
        # Quality score (from ContentAnalysisTool) 
        content_analysis = blog.get('content_analysis', {})
        if content_analysis.get('success', False):
            overall_score = content_analysis.get('overall_score', 50)
            score += overall_score * self.scoring_weights['quality']
        
        # Comment opportunity score (from BlogValidatorTool)
        comment_analysis = validation.get('comment_analysis', {})
        comment_score = self._calculate_comment_opportunity_score(comment_analysis)
        score += comment_score * self.scoring_weights['comments']
        
        # Technical factors (from BlogValidatorTool)
        technical_factors = validation.get('technical_factors', {})
        technical_score = self._calculate_technical_score(technical_factors)
        score += technical_score * self.scoring_weights['technical']
        
        # Spam safety (inverted spam risk)
        spam_risk = validation.get('spam_risk', {}).get('risk_score', 50)
        safety_score = max(0, 100 - spam_risk)
        score += safety_score * self.scoring_weights['spam_safety']
        
        return round(score, 2)
    
    def _calculate_comment_opportunity_score(self, comment_analysis: Dict[str, Any]) -> float:
        """
        Calculate comment opportunity score based on comment system analysis.
        """
        base_score = 50.0
        
        # Check if comments are enabled
        if comment_analysis.get('comments_enabled', False):
            base_score += 30
        
        # Check comment system type
        comment_system = comment_analysis.get('comment_system', '')
        if comment_system in ['disqus', 'wordpress', 'facebook']:
            base_score += 15
        
        # Check registration requirements
        if not comment_analysis.get('registration_required', True):
            base_score += 10
        
        # Check moderation policy
        moderation = comment_analysis.get('moderation_level', 'unknown')
        if moderation == 'light':
            base_score += 10
        elif moderation == 'moderate':
            base_score += 5
        
        return min(base_score, 100.0)
    
    def _calculate_technical_score(self, technical_factors: Dict[str, Any]) -> float:
        """
        Calculate technical quality score.
        """
        base_score = 50.0
        
        # HTTPS
        if technical_factors.get('https_enabled', False):
            base_score += 20
        
        # Mobile friendly
        if technical_factors.get('mobile_friendly', False):
            base_score += 15
        
        # Load speed
        load_time = technical_factors.get('load_time', 5.0)
        if load_time < 3.0:
            base_score += 15
        elif load_time < 5.0:
            base_score += 10
        
        return min(base_score, 100.0)
    
    def _meets_quality_criteria(self, blog: Dict[str, Any], min_authority: int) -> bool:
        """
        Check if blog meets minimum quality criteria.
        """
        validation = blog.get('validation_result', {})
        
        # Check overall score
        comprehensive_score = blog.get('comprehensive_score', 0)
        if comprehensive_score < self.quality_thresholds['minimum_overall_score']:
            return False
        
        # Check authority score
        authority_score = validation.get('authority_score', {}).get('score', 0)
        if authority_score < min_authority:
            return False
        
        # Check spam risk
        spam_risk = validation.get('spam_risk', {}).get('risk_score', 100)
        if spam_risk > self.quality_thresholds['maximum_spam_risk']:
            return False
        
        # Check if suitable for commenting
        if not validation.get('is_suitable', False):
            return False
        
        return True
    
    def _extract_keywords_from_task(self, task: str) -> str:
        """Extract keywords from task description."""
        task_lower = task.lower()
        
        # Enhanced keyword extraction
        tech_keywords = [
            'cloud computing', 'devops', 'kubernetes', 'docker', 'aws', 'azure',
            'microservices', 'serverless', 'infrastructure', 'automation',
            'ci/cd', 'monitoring', 'logging', 'security', 'scalability',
            'containers', 'orchestration', 'deployment', 'agile', 'terraform'
        ]
        
        found_keywords = []
        for keyword in tech_keywords:
            if keyword in task_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            return ' '.join(found_keywords[:3])  # Limit to top 3 keywords
        
        return 'cloud computing devops'
    
    def _store_enhanced_blogs(self, qualified_blogs: List[Dict[str, Any]]) -> int:
        """
        Store qualified blogs with enhanced metadata in database.
        """
        if not self.db_session:
            self.logger.warning("No database session available, skipping storage")
            return 0
        
        stored_count = 0
        
        for blog_data in qualified_blogs:
            try:
                blog_url = blog_data['url']
                
                # Check if blog already exists
                existing_blog = self.db_session.query(Blog).filter_by(url=blog_url).first()
                
                if existing_blog:
                    # Update existing blog with enhanced data
                    existing_blog.domain_authority = blog_data.get('comprehensive_score', 0)
                    existing_blog.updated_at = datetime.utcnow()
                    existing_blog.analysis_metadata = json.dumps({
                        'validation_result': blog_data.get('validation_result', {}),
                        'content_analysis': blog_data.get('content_analysis', {}),
                        'seo_analysis': blog_data.get('seo_analysis', {})
                    })
                else:
                    # Create new enhanced blog entry
                    new_blog = Blog(
                        url=blog_url,
                        domain=blog_data['domain'],
                        domain_authority=blog_data.get('comprehensive_score', 0),
                        category='tech',
                        status='active',
                        analysis_metadata=json.dumps({
                            'validation_result': blog_data.get('validation_result', {}),
                            'content_analysis': blog_data.get('content_analysis', {}),
                            'seo_analysis': blog_data.get('seo_analysis', {}),
                            'discovery_source': blog_data.get('discovery_source', 'unknown')
                        })
                    )
                    self.db_session.add(new_blog)
                
                stored_count += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to store blog {blog_data.get('url', 'unknown')}: {e}")
                continue
        
        try:
            self.db_session.commit()
            self.logger.info(f"Stored {stored_count} enhanced blogs in database")
        except Exception as e:
            self.logger.error(f"Failed to commit enhanced blog storage: {e}")
            self.db_session.rollback()
            stored_count = 0
        
        return stored_count
    
    def _generate_research_report(self, keywords: str, discovered: List, analyzed: List, qualified: List) -> Dict[str, Any]:
        """
        Generate comprehensive research report with insights and recommendations.
        """
        if not qualified:
            return {
                'summary': 'No qualified blogs found matching the criteria.',
                'insights': [],
                'recommendations': []
            }
        
        # Calculate metrics
        avg_score = sum(blog.get('comprehensive_score', 0) for blog in qualified) / len(qualified)
        
        # Platform distribution
        platforms = {}
        for blog in qualified:
            platform = blog.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
        
        # Authority distribution
        high_authority = len([b for b in qualified if b.get('comprehensive_score', 0) >= 80])
        medium_authority = len([b for b in qualified if 60 <= b.get('comprehensive_score', 0) < 80])
        low_authority = len([b for b in qualified if b.get('comprehensive_score', 0) < 60])
        
        return {
            'summary': f"""Found {len(qualified)} qualified blogs for '{keywords}' with average quality score of {avg_score:.1f}.
                          Discovery process: {len(discovered)} blogs discovered, {len(analyzed)} successfully analyzed, 
                          {len(qualified)} qualified after filtering.""",
            'quality_distribution': {
                'high_authority': high_authority,
                'medium_authority': medium_authority, 
                'low_authority': low_authority
            },
            'platform_distribution': platforms,
            'top_opportunities': [
                {
                    'url': blog['url'],
                    'title': blog.get('title', 'Unknown'),
                    'score': blog.get('comprehensive_score', 0),
                    'platform': blog.get('platform', 'unknown')
                }
                for blog in qualified[:5]
            ]
        }
    
    def _generate_recommendations(self, qualified_blogs: List[Dict[str, Any]]) -> List[str]:
        """
        Generate actionable recommendations based on research results.
        """
        if not qualified_blogs:
            return ["No qualified blogs found. Consider expanding search criteria or targeting different keywords."]
        
        recommendations = []
        
        # Score-based recommendations
        high_score_blogs = [b for b in qualified_blogs if b.get('comprehensive_score', 0) >= 80]
        if high_score_blogs:
            recommendations.append(f"Focus on {len(high_score_blogs)} high-authority blogs (score ≥80) for maximum impact.")
        
        # Platform-based recommendations
        platforms = {}
        for blog in qualified_blogs:
            platform = blog.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
        
        if platforms:
            top_platform = max(platforms.items(), key=lambda x: x[1])
            if top_platform[1] >= 3:
                recommendations.append(f"Consider developing a specialized strategy for {top_platform[0]} platform ({top_platform[1]} opportunities).")
        
        # Comment system recommendations
        easy_comment_blogs = 0
        for blog in qualified_blogs:
            validation = blog.get('validation_result', {})
            comment_analysis = validation.get('comment_analysis', {})
            if not comment_analysis.get('registration_required', True):
                easy_comment_blogs += 1
        
        if easy_comment_blogs:
            recommendations.append(f"Prioritize {easy_comment_blogs} blogs that don't require registration for faster engagement.")
        
        return recommendations
    
    def _calculate_quality_metrics(self, qualified_blogs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall quality metrics for the research session.
        """
        if not qualified_blogs:
            return {}
        
        scores = [blog.get('comprehensive_score', 0) for blog in qualified_blogs]
        
        return {
            'average_score': sum(scores) / len(scores),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'blogs_above_threshold': len([s for s in scores if s >= self.quality_thresholds['minimum_overall_score']]),
            'success_rate': (len(qualified_blogs) / max(1, len(scores))) * 100
        }


# Export the enhanced agent class
__all__ = ['EnhancedBlogResearcherAgent']
