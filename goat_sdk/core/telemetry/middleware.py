"""Telemetry middleware for GOAT SDK."""

import time
import functools
from typing import Callable, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from . import track_transaction, track_error

def trace_transaction(chain: str) -> Callable:
    """Decorator to trace blockchain transactions.
    
    Args:
        chain: The blockchain network
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(
                name=f"{chain}_{func.__name__}",
                kind=trace.SpanKind.CLIENT,
            ) as span:
                try:
                    # Execute transaction
                    result = await func(*args, **kwargs)
                    
                    # Record success
                    span.set_status(Status(StatusCode.OK))
                    latency = (time.time() - start_time) * 1000
                    track_transaction(chain, "success", latency)
                    
                    return result
                    
                except Exception as e:
                    # Record error
                    span.set_status(
                        Status(StatusCode.ERROR, str(e))
                    )
                    span.record_exception(e)
                    
                    latency = (time.time() - start_time) * 1000
                    track_transaction(chain, "failure", latency)
                    track_error(type(e).__name__, str(e))
                    
                    raise
                    
        return wrapper
    return decorator
