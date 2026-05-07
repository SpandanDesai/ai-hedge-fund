"""Performance monitoring and analytics system for AI Hedge Fund."""

import time
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import statistics
from collections import defaultdict, deque
from contextlib import contextmanager

from src.utils.logging import logger
from src.config import config


class PerformanceMetricType(str, Enum):
    """Types of performance metrics that can be tracked."""
    EXECUTION_TIME = "execution_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"


@dataclass
class PerformanceMetric:
    """Individual performance metric record."""
    operation: str
    metric_type: PerformanceMetricType
    value: float
    timestamp: datetime
    success: Optional[bool] = None
    error_type: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class PerformanceStats:
    """Statistical summary of performance metrics."""
    operation: str
    metric_type: PerformanceMetricType
    count: int
    total: float
    average: float
    median: float
    min: float
    max: float
    p95: float
    p99: float
    success_rate: Optional[float] = None
    error_rate: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(self, max_history: int = 1000):
        self.metrics: List[PerformanceMetric] = []
        self.max_history = max_history
        self.lock = threading.RLock()
        self.operation_stats: Dict[str, Dict[PerformanceMetricType, List[float]]] = defaultdict(lambda: defaultdict(list))
    
    def track(self, operation: str, metric_type: PerformanceMetricType, 
              value: float, success: Optional[bool] = None, 
              error_type: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Track a performance metric."""
        metric = PerformanceMetric(
            operation=operation,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            success=success,
            error_type=error_type,
            metadata=metadata
        )
        
        with self.lock:
            self.metrics.append(metric)
            # Keep only the most recent metrics
            if len(self.metrics) > self.max_history:
                self.metrics = self.metrics[-self.max_history:]
            
            # Update operation statistics
            self.operation_stats[operation][metric_type].append(value)
    
    @contextmanager
    def track_execution(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for tracking execution time of an operation."""
        start_time = time.time()
        success = True
        error_type = None
        
        try:
            yield
        except Exception as e:
            success = False
            error_type = type(e).__name__
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.track(
                operation=operation,
                metric_type=PerformanceMetricType.EXECUTION_TIME,
                value=duration_ms,
                success=success,
                error_type=error_type,
                metadata=metadata
            )
    
    def get_stats(self, operation: Optional[str] = None, 
                 metric_type: Optional[PerformanceMetricType] = None,
                 time_window: Optional[timedelta] = None) -> Dict[str, PerformanceStats]:
        """Get performance statistics for the specified criteria."""
        with self.lock:
            filtered_metrics = self.metrics
            
            # Filter by operation
            if operation:
                filtered_metrics = [m for m in filtered_metrics if m.operation == operation]
            
            # Filter by metric type
            if metric_type:
                filtered_metrics = [m for m in filtered_metrics if m.metric_type == metric_type]
            
            # Filter by time window
            if time_window:
                cutoff_time = datetime.now() - time_window
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= cutoff_time]
            
            # Group by operation and metric type
            grouped_metrics = defaultdict(lambda: defaultdict(list))
            for metric in filtered_metrics:
                grouped_metrics[metric.operation][metric.metric_type].append(metric.value)
            
            # Calculate statistics for each group
            stats = {}
            for op, metric_types in grouped_metrics.items():
                for mt, values in metric_types.items():
                    if values:
                        key = f"{op}:{mt.value}"
                        values_sorted = sorted(values)
                        n = len(values_sorted)
                        
                        stats[key] = PerformanceStats(
                            operation=op,
                            metric_type=mt,
                            count=n,
                            total=sum(values_sorted),
                            average=statistics.mean(values_sorted),
                            median=statistics.median(values_sorted),
                            min=min(values_sorted),
                            max=max(values_sorted),
                            p95=values_sorted[int(n * 0.95)] if n > 1 else values_sorted[0],
                            p99=values_sorted[int(n * 0.99)] if n > 20 else values_sorted[-1] if n > 0 else 0
                        )
            
            return stats
    
    def get_operation_stats(self, operation: str) -> Dict[PerformanceMetricType, PerformanceStats]:
        """Get detailed statistics for a specific operation."""
        return self.get_stats(operation=operation)
    
    def get_success_rate(self, operation: str, time_window: Optional[timedelta] = None) -> float:
        """Get success rate for an operation."""
        with self.lock:
            filtered_metrics = [m for m in self.metrics if m.operation == operation and m.success is not None]
            
            if time_window:
                cutoff_time = datetime.now() - time_window
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= cutoff_time]
            
            if not filtered_metrics:
                return 0.0
            
            success_count = sum(1 for m in filtered_metrics if m.success)
            return success_count / len(filtered_metrics)
    
    def get_average_execution_time(self, operation: str, time_window: Optional[timedelta] = None) -> float:
        """Get average execution time for an operation."""
        stats = self.get_stats(operation=operation, metric_type=PerformanceMetricType.EXECUTION_TIME, time_window=time_window)
        key = f"{operation}:{PerformanceMetricType.EXECUTION_TIME.value}"
        return stats[key].average if key in stats else 0.0
    
    def clear(self):
        """Clear all performance metrics."""
        with self.lock:
            self.metrics.clear()
            self.operation_stats.clear()
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in the specified format."""
        with self.lock:
            if format == "json":
                import json
                return json.dumps([m.to_dict() for m in self.metrics], indent=2)
            elif format == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow(["operation", "metric_type", "value", "timestamp", "success", "error_type"])
                
                # Write data
                for metric in self.metrics:
                    writer.writerow([
                        metric.operation,
                        metric.metric_type.value,
                        metric.value,
                        metric.timestamp.isoformat(),
                        metric.success,
                        metric.error_type
                    ])
                
                return output.getvalue()
            else:
                raise ValueError(f"Unsupported format: {format}")


class PerformanceTracker:
    """Decorator class for tracking function performance."""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: Optional[str] = None):
        self.monitor = monitor
        self.operation_name = operation_name
    
    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            operation = self.operation_name or func.__name__
            
            with self.monitor.track_execution(operation=operation, metadata={
                "function": func.__name__,
                "module": func.__module__,
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            }):
                return func(*args, **kwargs)
        
        return wrapper


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def track_performance(operation_name: Optional[str] = None):
    """Decorator for tracking function performance."""
    def decorator(func):
        return PerformanceTracker(performance_monitor, operation_name)(func)
    return decorator


@contextmanager
def performance_context(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for tracking performance of a code block."""
    with performance_monitor.track_execution(operation, metadata):
        yield


def get_performance_report() -> Dict[str, Any]:
    """Generate a comprehensive performance report."""
    stats = performance_monitor.get_stats()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_metrics": len(performance_monitor.metrics),
        "operations": {},
        "summary": {}
    }
    
    # Calculate overall statistics
    execution_times = [m.value for m in performance_monitor.metrics 
                      if m.metric_type == PerformanceMetricType.EXECUTION_TIME]
    
    if execution_times:
        report["summary"]["average_execution_time_ms"] = statistics.mean(execution_times)
        report["summary"]["max_execution_time_ms"] = max(execution_times)
        report["summary"]["min_execution_time_ms"] = min(execution_times)
    
    # Add operation-specific statistics
    for key, stat in stats.items():
        operation, metric_type = key.split(":")
        if operation not in report["operations"]:
            report["operations"][operation] = {}
        
        report["operations"][operation][metric_type] = stat.to_dict()
    
    return report


def log_performance_report():
    """Log a performance report using the structured logger."""
    report = get_performance_report()
    logger.info("Performance report generated", performance_report=report)
    return report