"""
Search Engine Manager - Integration with Google, Bing, and DuckDuckGo APIs
Uses free tiers of search APIs to discover blogs and content
"""
import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs
import json
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class SearchEngineManager:
    """
    Manages search across multiple search engines using free APIs
    """
    
    def __init__(self):
        # API Keys (will be loaded from environment)
        self.google_api_key = None
        self.google_cse_id = None
        self.bing_api_key = None
        
        # Rate limiting
        self.last_google_request = 0
        self.last_bing_request = 0
        self.last_ddg_request = 0
        
        # Minimum delays between requests (seconds)
        self.google_delay = 1.0  # 1 second for free tier
        self.bing_delay = 0.5    # 0.5 seconds for free tier
        self.ddg_delay = 2.0     # 2 seconds to be respectful
        
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _load_api_keys(self):
        """Load API keys from environment variables"""
        import os
        
        # Google Custom Search API (100 free queries/day)
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_SEARCH_CSE_ID')
        
        # Bing Search API (3000 free queries/month)
        self.bing_api_key = os.getenv('BING_SEARCH_API_KEY')
        
        # Log configuration status (without exposing keys)
        if self.google_api_key and self.google_cse_id:
            logger.info("Google Custom Search API configured")
        else:
            logger.warning("Google Custom Search API not configured - set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CSE_ID")
        
        if self.bing_api_key:
            logger.info("Bing Search API configured")
        else:
            logger.warning("Bing Search API not configured - set BING_SEARCH_API_KEY")
    
    async def search_google(
        self,
        query: str,
        max_results: int = 10,
        region: str = "US",
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Search Google using Custom Search API (100 free queries/day)
        """
        if not self.google_api_key or not self.google_cse_id:
            self._load_api_keys()
        
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google Search API credentials not configured")
            return []
        
        results = []
        
        try:
            # Rate limiting
            await self._wait_for_rate_limit('google')
            
            # Build search query for blog content
            blog_query = f"{query} blog OR article OR post"
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': blog_query,
                'num': min(max_results, 10),  # Max 10 per request
                'gl': region.lower(),
                'hl': language.lower(),
                'safe': 'medium',
                'fileType': '',  # Exclude files
                'excludeTerms': 'pdf filetype:pdf'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    items = data.get('items', [])
                    for item in items:
                        result = self._parse_google_result(item)
                        if result and self._is_blog_content(result):
                            results.append(result)
                
                elif response.status == 429:
                    logger.warning("Google Search API rate limit exceeded")
                else:
                    logger.warning(f"Google Search API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Google search failed for query '{query}': {str(e)}")
        
        return results
    
    def _parse_google_result(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Google search result item"""
        try:
            url = item.get('link', '')
            if not url:
                return None
            
            domain = urlparse(url).netloc.lower()
            
            return {
                'url': url,
                'domain': domain,
                'title': item.get('title', ''),
                'description': item.get('snippet', ''),
                'source': 'google',
                'discovered_at': datetime.utcnow().isoformat()
            }
        except Exception:
            return None
    
    async def search_bing(
        self,
        query: str,
        max_results: int = 10,
        region: str = "US"
    ) -> List[Dict[str, Any]]:
        """
        Search Bing using Bing Search API (3000 free queries/month)
        """
        if not self.bing_api_key:
            self._load_api_keys()
        
        if not self.bing_api_key:
            logger.warning("Bing Search API credentials not configured")
            return []
        
        results = []
        
        try:
            # Rate limiting
            await self._wait_for_rate_limit('bing')
            
            # Build search query for blog content
            blog_query = f"{query} (blog OR article OR post)"
            
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {
                'Ocp-Apim-Subscription-Key': self.bing_api_key,
                'User-Agent': 'SEO-Blog-Research-Bot/1.0'
            }
            params = {
                'q': blog_query,
                'count': min(max_results, 50),  # Max 50 per request
                'mkt': f"{region.lower()}-{region.upper()}",  # e.g., en-US
                'safeSearch': 'Moderate',
                'responseFilter': 'Webpages',
                'textDecorations': False,
                'textFormat': 'Raw'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    webpages = data.get('webPages', {})
                    web_results = webpages.get('value', [])
                    
                    for item in web_results:
                        result = self._parse_bing_result(item)
                        if result and self._is_blog_content(result):
                            results.append(result)
                
                elif response.status == 429:
                    logger.warning("Bing Search API rate limit exceeded")
                else:
                    logger.warning(f"Bing Search API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Bing search failed for query '{query}': {str(e)}")
        
        return results
    
    def _parse_bing_result(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Bing search result item"""
        try:
            url = item.get('url', '')
            if not url:
                return None
            
            domain = urlparse(url).netloc.lower()
            
            return {
                'url': url,
                'domain': domain,
                'title': item.get('name', ''),
                'description': item.get('snippet', ''),
                'source': 'bing',
                'discovered_at': datetime.utcnow().isoformat()
            }
        except Exception:
            return None
    
    async def search_duckduckgo(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo using their unofficial API (free, unlimited)
        Note: This uses web scraping as DDG doesn't have an official API
        """
        results = []
        
        try:
            # Rate limiting
            await self._wait_for_rate_limit('ddg')
            
            # Build search query for blog content
            blog_query = f"{query} blog OR article OR post"
            
            # DuckDuckGo instant answers API (limited but free)
            url = "https://api.duckduckgo.com/"
            params = {
                'q': blog_query,
                'format': 'json',
                'no_redirect': '1',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # First try the instant answers API
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process related topics (limited results)
                    related_topics = data.get('RelatedTopics', [])
                    for topic in related_topics[:max_results]:
                        if isinstance(topic, dict) and 'FirstURL' in topic:
                            result = self._parse_ddg_result(topic)
                            if result and self._is_blog_content(result):
                                results.append(result)
            
            # If we need more results, try alternative approach
            if len(results) < max_results:
                additional_results = await self._search_ddg_html(blog_query, max_results - len(results))
                results.extend(additional_results)
        
        except Exception as e:
            logger.error(f"DuckDuckGo search failed for query '{query}': {str(e)}")
        
        return results
    
    async def _search_ddg_html(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Alternative DuckDuckGo search using HTML parsing
        This is more aggressive and should be used carefully
        """
        results = []
        
        try:
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'us-en'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    results = self._parse_ddg_html(html, max_results)
        
        except Exception as e:
            logger.warning(f"DuckDuckGo HTML search failed: {str(e)}")
        
        return results
    
    def _parse_ddg_html(self, html: str, max_results: int) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML results"""
        results = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find result links
            result_links = soup.find_all('a', class_='result__a')[:max_results]
            
            for link in result_links:
                href = link.get('href', '')
                if href.startswith('/l/?uddg='):
                    # Extract real URL from DuckDuckGo redirect
                    parsed = parse_qs(urlparse(href).query)
                    actual_url = parsed.get('uddg', [''])[0]
                    if actual_url:
                        href = actual_url
                
                if href and href.startswith('http'):
                    domain = urlparse(href).netloc.lower()
                    title = link.get_text(strip=True)
                    
                    # Find description
                    result_div = link.find_parent('div', class_='result')
                    description = ""
                    if result_div:
                        desc_elem = result_div.find('span', class_='result__snippet')
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)
                    
                    result = {
                        'url': href,
                        'domain': domain,
                        'title': title,
                        'description': description,
                        'source': 'duckduckgo',
                        'discovered_at': datetime.utcnow().isoformat()
                    }
                    
                    if self._is_blog_content(result):
                        results.append(result)
        
        except Exception as e:
            logger.warning(f"Failed to parse DuckDuckGo HTML: {str(e)}")
        
        return results
    
    def _parse_ddg_result(self, topic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse DuckDuckGo related topic result"""
        try:
            url = topic.get('FirstURL', '')
            if not url:
                return None
            
            domain = urlparse(url).netloc.lower()
            
            return {
                'url': url,
                'domain': domain,
                'title': topic.get('Text', '').split(' - ')[0] if topic.get('Text') else '',
                'description': topic.get('Text', ''),
                'source': 'duckduckgo',
                'discovered_at': datetime.utcnow().isoformat()
            }
        except Exception:
            return None
    
    def _is_blog_content(self, result: Dict[str, Any]) -> bool:
        """
        Determine if a search result is likely blog content
        """
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        description = result.get('description', '').lower()
        domain = result.get('domain', '').lower()
        
        # Skip common non-blog domains
        excluded_domains = {
            'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'linkedin.com', 'pinterest.com', 'reddit.com', 'stackoverflow.com',
            'github.com', 'wikipedia.org', 'amazon.com', 'ebay.com',
            'craigslist.org', 'indeed.com', 'glassdoor.com'
        }
        
        if any(excluded in domain for excluded in excluded_domains):
            return False
        
        # Skip file downloads
        file_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
        if any(ext in url for ext in file_extensions):
            return False
        
        # Look for blog indicators
        blog_indicators = [
            'blog', 'article', 'post', 'news', 'insights', 'guide',
            'tutorial', 'how-to', 'tips', 'advice', 'commentary',
            'opinion', 'review', 'analysis', 'case-study'
        ]
        
        text_to_check = f"{title} {description} {url}"
        
        # Must have at least one blog indicator
        has_blog_indicator = any(indicator in text_to_check for indicator in blog_indicators)
        
        # Additional quality checks
        has_meaningful_title = len(title.strip()) > 10
        has_meaningful_description = len(description.strip()) > 20
        
        return has_blog_indicator and has_meaningful_title and has_meaningful_description
    
    async def _wait_for_rate_limit(self, engine: str):
        """Wait for rate limiting if needed"""
        current_time = asyncio.get_event_loop().time()
        
        if engine == 'google':
            time_since_last = current_time - self.last_google_request
            if time_since_last < self.google_delay:
                await asyncio.sleep(self.google_delay - time_since_last)
            self.last_google_request = current_time
        
        elif engine == 'bing':
            time_since_last = current_time - self.last_bing_request
            if time_since_last < self.bing_delay:
                await asyncio.sleep(self.bing_delay - time_since_last)
            self.last_bing_request = current_time
        
        elif engine == 'ddg':
            time_since_last = current_time - self.last_ddg_request
            if time_since_last < self.ddg_delay:
                await asyncio.sleep(self.ddg_delay - time_since_last)
            self.last_ddg_request = current_time
    
    async def get_search_suggestions(self, query: str) -> List[str]:
        """
        Get search suggestions to expand keyword research
        """
        suggestions = []
        
        try:
            # Google suggestions
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': query
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if len(data) > 1 and isinstance(data[1], list):
                        suggestions.extend(data[1][:5])  # Take top 5
        
        except Exception as e:
            logger.warning(f"Failed to get search suggestions: {str(e)}")
        
        return suggestions
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine usage statistics"""
        return {
            'google_requests': getattr(self, '_google_requests', 0),
            'bing_requests': getattr(self, '_bing_requests', 0),
            'ddg_requests': getattr(self, '_ddg_requests', 0),
            'last_google_request': self.last_google_request,
            'last_bing_request': self.last_bing_request,
            'last_ddg_request': self.last_ddg_request
        }
