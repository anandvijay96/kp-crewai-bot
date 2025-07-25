"""
WebScraper Tool - Advanced web scraping and content extraction

This tool is designed for:
- Efficient and reliable web scraping
- Content extraction and data parsing
- Handling diverse web structures and formats
- Integrating with CrewAI agents for automated data collection
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any


class WebScraper:
    """
    A tool for scraping web pages and extracting content.
    
    Capabilities:
    - Fetch and parse HTML content
    - Extract specific data based on tags or attributes
    - Handle various web layouts and content types
    """
    
    def __init__(self, user_agent: Optional[str] = None):
        self.headers = {'User-Agent': user_agent or 'CrewAIWebScraper/1.0'}
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch and return the HTML content of a web page.
        
        Args:
            url: The URL of the web page to fetch.
            
        Returns:
            The HTML content as a string, or None if fetch fails.
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch page: {e}")
            return None
    
    def parse_content(self, html: str) -> BeautifulSoup:
        """
        Parse the HTML content with BeautifulSoup.
        
        Args:
            html: The HTML content to parse.
            
        Returns:
            A BeautifulSoup object for navigation and extraction.
        """
        return BeautifulSoup(html, 'html.parser')
    
    def extract_data(self, soup: BeautifulSoup, selectors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from a parsed BeautifulSoup object.
        
        Args:
            soup: The BeautifulSoup object to extract from.
            selectors: A dictionary containing CSS selectors or attributes to extract specific data.
            
        Returns:
            A dictionary containing the extracted data.
        """
        extracted_data = {}
        
        for key, selector in selectors.items():
            if isinstance(selector, str):
                element = soup.select_one(selector)
                extracted_data[key] = element.get_text(strip=True) if element else None
            elif isinstance(selector, dict):  # Assume attribute-based extraction
                element = soup.find(attrs=selector)
                extracted_data[key] = element.get('content') if element else None
        
        return extracted_data

