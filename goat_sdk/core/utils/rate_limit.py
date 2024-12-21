"""Rate limiting utilities for GOAT SDK."""

import time
import asyncio
from typing import Dict, Callable, Any
from functools import wraps

class RateLimiter:
    """Rate limiter implementation using token bucket algorithm."""
    
    def __init__(self, rate: float, burst: int):
        """Initialize rate limiter.
        
        Args:
            rate: Rate limit in tokens per second
            burst: Maximum burst size (token bucket capacity)
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_time = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire a token from the bucket.
        
        Returns:
            True if token was acquired, False otherwise
        """
        async with self._lock:
            now = time.monotonic()
            time_passed = now - self.last_time
            self.tokens = min(
                self.burst,
                self.tokens + time_passed * self.rate
            )
            
            if self.tokens >= 1:
                self.tokens -= 1
                self.last_time = now
                return True
            return False

def rate_limit(
    rate: float,
    burst: int,
    key_func: Callable[..., str] = None
) -> Callable:
    """Decorator to apply rate limiting to a function.
    
    Args:
        rate: Rate limit in calls per second
        burst: Maximum burst size
        key_func: Optional function to generate rate limit key from arguments
        
    Returns:
        Decorator function that applies rate limiting
    """
    limiters: Dict[str, RateLimiter] = {}
    
    def get_limiter(key: str) -> RateLimiter:
        if key not in limiters:
            limiters[key] = RateLimiter(rate, burst)
        return limiters[key]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get rate limit key
            key = "default"
            if key_func:
                key = key_func(*args, **kwargs)
            
            # Get or create limiter for this key
            limiter = get_limiter(key)
            
            # Try to acquire token
            while not await limiter.acquire():
                await asyncio.sleep(1.0 / rate)
            
            # Execute function
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
