"""
Rate Limiter - Manages API request throttling to avoid hitting rate limits
"""
import asyncio
import time
import logging
from typing import Dict, Any
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Manages rate limiting for different services to prevent API throttling
    """
    
    def __init__(self):
        # Service-specific rate limits (requests per time window)
        self.rate_limits = {
            'search_engines': {'requests': 10, 'window': 60},  # 10 requests per minute
            'authority_scoring': {'requests': 20, 'window': 60},  # 20 requests per minute
            'content_analysis': {'requests': 30, 'window': 60}   # 30 requests per minute
        }
        
        # Track request history for each service
        self.request_history: Dict[str, deque] = defaultdict(deque)
        
        # Minimum delays between requests (seconds)
        self.min_delays = {
            'search_engines': 1.0,
            'authority_scoring': 0.5,
            'content_analysis': 0.3
        }
        
        # Track last request times
        self.last_requests: Dict[str, float] = {}
    
    async def wait_if_needed(self, service: str):
        """
        Wait if necessary to respect rate limits for the service
        """
        current_time = time.time()
        
        # Check minimum delay since last request
        min_delay = self.min_delays.get(service, 1.0)
        last_request = self.last_requests.get(service, 0)
        
        time_since_last = current_time - last_request
        if time_since_last < min_delay:
            wait_time = min_delay - time_since_last
            logger.debug(f"Rate limiting {service}: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            current_time = time.time()
        
        # Check request count within time window
        if service in self.rate_limits:
            rate_limit = self.rate_limits[service]
            history = self.request_history[service]
            
            # Remove old requests outside the time window
            window_start = current_time - rate_limit['window']
            while history and history[0] < window_start:
                history.popleft()
            
            # Check if we're at the rate limit
            if len(history) >= rate_limit['requests']:
                # Calculate how long to wait until the oldest request expires
                oldest_request = history[0]
                wait_until = oldest_request + rate_limit['window']
                wait_time = wait_until - current_time
                
                if wait_time > 0:
                    logger.warning(f"Rate limit reached for {service}: waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    current_time = time.time()
            
            # Record this request
            history.append(current_time)
        
        # Update last request time
        self.last_requests[service] = current_time
    
    def get_rate_limit_status(self, service: str) -> Dict[str, Any]:
        """
        Get current rate limit status for a service
        """
        current_time = time.time()
        
        if service not in self.rate_limits:
            return {'error': f'Unknown service: {service}'}
        
        rate_limit = self.rate_limits[service]
        history = self.request_history[service]
        
        # Clean old requests
        window_start = current_time - rate_limit['window']
        while history and history[0] < window_start:
            history.popleft()
        
        requests_made = len(history)
        requests_remaining = max(0, rate_limit['requests'] - requests_made)
        
        # Calculate when next request is allowed
        last_request = self.last_requests.get(service, 0)
        min_delay = self.min_delays.get(service, 1.0)
        next_allowed = last_request + min_delay
        
        if requests_made >= rate_limit['requests'] and history:
            # If at rate limit, next allowed is when oldest request expires
            oldest_request = history[0]
            next_allowed = max(next_allowed, oldest_request + rate_limit['window'])
        
        return {
            'service': service,
            'requests_made': requests_made,
            'requests_remaining': requests_remaining,
            'rate_limit': rate_limit['requests'],
            'window_seconds': rate_limit['window'],
            'next_allowed_at': next_allowed,
            'seconds_until_next': max(0, next_allowed - current_time)
        }
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get rate limit status for all services
        """
        return {
            service: self.get_rate_limit_status(service)
            for service in self.rate_limits.keys()
        }
    
    def reset_service(self, service: str):
        """
        Reset rate limiting for a specific service (useful for testing)
        """
        if service in self.request_history:
            self.request_history[service].clear()
        if service in self.last_requests:
            del self.last_requests[service]
        logger.info(f"Reset rate limiting for service: {service}")
    
    def update_rate_limit(self, service: str, requests: int, window: int):
        """
        Update rate limit configuration for a service
        """
        self.rate_limits[service] = {'requests': requests, 'window': window}
        logger.info(f"Updated rate limit for {service}: {requests} requests per {window}s")
    
    def update_min_delay(self, service: str, delay: float):
        """
        Update minimum delay between requests for a service
        """
        self.min_delays[service] = delay
        logger.info(f"Updated minimum delay for {service}: {delay}s")
