"""Enhanced caching strategy with Redis integration and fallback to in-memory cache."""

import json
import time
from typing import Optional, Any, Dict, List
import logging
from datetime import datetime, timedelta

from src.config import config

logger = logging.getLogger(__name__)


class BaseCache:
    """Base cache interface."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError


class MemoryCache(BaseCache):
    """In-memory cache implementation."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        cached = self._cache.get(key)
        if cached and cached['expires'] > time.time():
            return cached['value']
        elif cached:
            del self._cache[key]  # Remove expired entry
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        ttl = ttl or config.data_cache_ttl
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
        return True
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        cached = self._cache.get(key)
        return cached is not None and cached['expires'] > time.time()


class RedisCache(BaseCache):
    """Redis cache implementation."""
    
    def __init__(self):
        try:
            import redis
            self.redis = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                password=config.redis_password,
                db=config.redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
            logger.info("Redis cache connected successfully")
        except ImportError:
            logger.warning("Redis not installed, falling back to memory cache")
            raise
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, falling back to memory cache")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        try:
            cached = self.redis.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Error getting from Redis cache: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            ttl = ttl or config.data_cache_ttl
            serialized = json.dumps(value)
            if ttl > 0:
                self.redis.setex(key, timedelta(seconds=ttl), serialized)
            else:
                self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking Redis cache existence: {e}")
            return False


class CacheManager:
    """Unified cache manager with fallback strategy."""
    
    def __init__(self):
        self._cache: Optional[BaseCache] = None
        self._initialize_cache()
    
    def _initialize_cache(self):
        """Initialize the appropriate cache backend."""
        try:
            # Try Redis first if configured
            if (config.redis_host != "localhost" or 
                config.redis_port != 6379 or 
                config.redis_password):
                self._cache = RedisCache()
                logger.info("Using Redis cache")
            else:
                # Fall back to memory cache
                self._cache = MemoryCache()
                logger.info("Using memory cache")
        except Exception:
            # Fall back to memory cache if Redis fails
            self._cache = MemoryCache()
            logger.info("Using memory cache (Redis fallback)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not config.data_cache_enabled:
            return None
        
        try:
            return self._cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not config.data_cache_enabled:
            return False
        
        try:
            return self._cache.set(key, value, ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return self._cache.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not config.data_cache_enabled:
            return False
        
        try:
            return self._cache.exists(key)
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear entire cache (if supported)."""
        try:
            if isinstance(self._cache, MemoryCache):
                self._cache._cache.clear()
                return True
            elif isinstance(self._cache, RedisCache):
                self._cache.redis.flushdb()
                return True
            return False
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


# Global cache instance
cache = CacheManager()


def get_cache_key(operation: str, **kwargs) -> str:
    """Generate consistent cache key from operation and parameters."""
    key_parts = [operation]
    for k, v in sorted(kwargs.items()):
        if v is not None:
            key_parts.append(f"{k}_{v}")
    return "::".join(key_parts)


def cache_decorator(ttl: Optional[int] = None):
    """Decorator for caching function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not config.data_cache_enabled:
                return func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            cache_key = get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache set for {cache_key}")
            
            return result
        return wrapper
    return decorator


# Export the cache instance
__all__ = ['cache', 'get_cache_key', 'cache_decorator', 'BaseCache', 'MemoryCache', 'RedisCache', 'CacheManager']