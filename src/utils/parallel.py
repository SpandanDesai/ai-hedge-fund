"""Parallel data fetching utilities for concurrent operations."""

import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Callable, TypeVar, Any, Optional, Union
import logging
from functools import partial
import time

from src.config import config

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ParallelExecutor:
    """Manager for parallel execution with configurable concurrency."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or config.max_concurrent_requests
        self._thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self._process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
    
    async def execute_async(self, tasks: List[Callable[[], T]]) -> List[T]:
        """Execute tasks asynchronously with thread pool."""
        loop = asyncio.get_event_loop()
        
        # Create futures for all tasks
        futures = [
            loop.run_in_executor(self._thread_pool, task)
            for task in tasks
        ]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*futures, return_exceptions=True)
        
        # Process results, handling exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Parallel task failed: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def execute_sync(self, tasks: List[Callable[[], T]]) -> List[T]:
        """Execute tasks synchronously with thread pool."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(task): task
                for task in tasks
            }
            
            # Collect results
            for future in future_to_task:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Parallel task failed: {e}")
                    results.append(None)
        
        return results
    
    async def execute_batch(
        self, 
        tasks: List[Callable[[], T]], 
        batch_size: Optional[int] = None
    ) -> List[T]:
        """Execute tasks in batches to avoid overwhelming the system."""
        batch_size = batch_size or self.max_workers
        all_results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await self.execute_async(batch)
            all_results.extend(batch_results)
            
            # Small delay between batches to be respectful of rate limits
            if i + batch_size < len(tasks):
                await asyncio.sleep(0.1)
        
        return all_results
    
    def map_async(self, func: Callable[[Any], T], items: List[Any]) -> List[T]:
        """Apply function to each item in parallel."""
        tasks = [partial(func, item) for item in items]
        return self.execute_sync(tasks)
    
    async def map_async_async(self, func: Callable[[Any], T], items: List[Any]) -> List[T]:
        """Apply async function to each item in parallel."""
        tasks = [partial(func, item) for item in items]
        return await self.execute_async(tasks)
    
    def close(self):
        """Clean up resources."""
        self._thread_pool.shutdown(wait=False)
        self._process_pool.shutdown(wait=False)


# Global executor instance
executor = ParallelExecutor()


def parallel_execute(tasks: List[Callable[[], T]]) -> List[T]:
    """Convenience function for parallel execution."""
    return executor.execute_sync(tasks)


async def parallel_execute_async(tasks: List[Callable[[], T]]) -> List[T]:
    """Convenience function for async parallel execution."""
    return await executor.execute_async(tasks)


def parallel_map(func: Callable[[Any], T], items: List[Any]) -> List[T]:
    """Convenience function for parallel mapping."""
    return executor.map_async(func, items)


async def parallel_map_async(func: Callable[[Any], T], items: List[Any]) -> List[T]:
    """Convenience function for async parallel mapping."""
    return await executor.map_async_async(func, items)


class RateLimiter:
    """Rate limiting utility for API calls."""
    
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    async def wait(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove calls older than the period
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.period]
        
        if len(self.calls) >= self.max_calls:
            # Calculate wait time
            oldest_call = self.calls[0]
            wait_time = self.period - (now - oldest_call)
            
            if wait_time > 0:
                logger.debug(f"Rate limit exceeded, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                
                # Update calls after waiting
                now = time.time()
                self.calls = [call_time for call_time in self.calls 
                             if now - call_time < self.period]
        
        # Add current call
        self.calls.append(now)


def retry_async(
    max_retries: int = 3, 
    delay: float = 1.0, 
    backoff: float = 2.0,
    exceptions: Union[Exception, tuple] = Exception
):
    """Decorator for retrying async functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} "
                        f"after error: {e}. Waiting {current_delay:.2f}s"
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


def retry_sync(
    max_retries: int = 3, 
    delay: float = 1.0, 
    backoff: float = 2.0,
    exceptions: Union[Exception, tuple] = Exception
):
    """Decorator for retrying sync functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} "
                        f"after error: {e}. Waiting {current_delay:.2f}s"
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


# Export utilities
__all__ = [
    'ParallelExecutor',
    'parallel_execute',
    'parallel_execute_async',
    'parallel_map',
    'parallel_map_async',
    'RateLimiter',
    'retry_async',
    'retry_sync',
    'executor'
]