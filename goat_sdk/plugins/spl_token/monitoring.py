"""Monitoring utilities for SPL Token Service."""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast
from solders.rpc.responses import GetHealthResp, GetVersionResp
from solders.rpc import errors as rpc_errors
from prometheus_client import Counter, Histogram
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
import functools

from goat_sdk.plugins.spl_token.parameters import ModeConfig
from goat_sdk.plugins.spl_token.exceptions import TokenNotFoundError, TokenTransferError, InvalidTokenAddressError

logger = logging.getLogger(__name__)

# Prometheus metrics
TOKEN_OPERATION_DURATION = Histogram(
    "spl_token_operation_duration_seconds",
    "Duration of SPL token operations",
    ["operation", "network", "mode_enabled"],
)

TOKEN_OPERATION_ERRORS = Counter(
    "spl_token_operation_errors_total",
    "Total number of SPL token operation errors",
    ["operation", "network", "mode_enabled"],
)

MODE_VALIDATION_DURATION = Histogram(
    "spl_token_validation_duration_seconds",
    "Duration of Mode-specific validations",
    ["validation_type", "network", "mode_enabled"],
)

MODE_VALIDATION_FAILURES = Counter(
    "spl_token_validation_failures_total",
    "Total number of Mode-specific validation failures",
    ["validation_type", "network", "mode_enabled"],
)

# Type variables for function decorators
F = TypeVar("F", bound=Callable[..., Any])

def log_decorator_error(decorator_name: str, operation_name: str, error: Exception, context: str = "") -> None:
    """Helper function to log decorator errors."""
    logger.error(f"[{operation_name}][{decorator_name}] Error in {context}")
    logger.error(f"[{operation_name}][{decorator_name}] Error type: {type(error)}")
    logger.error(f"[{operation_name}][{decorator_name}] Error message: {str(error)}")
    logger.error(f"[{operation_name}][{decorator_name}] Error attributes: {vars(error) if hasattr(error, '__dict__') else str(error)}")
    if hasattr(error, '__cause__'):
        logger.error(f"[{operation_name}][{decorator_name}] Caused by: {error.__cause__}")
    if hasattr(error, '__context__'):
        logger.error(f"[{operation_name}][{decorator_name}] Context: {error.__context__}")
    logger.error(f"[{operation_name}][{decorator_name}] Error traceback:", exc_info=True)

def trace_operation(operation_name: str) -> Callable[[F], F]:
    """Decorator to trace SPL token operations."""
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = trace.get_tracer(__name__)
            logger.info(f"[{operation_name}][trace_operation] Starting operation")
            logger.debug(f"[{operation_name}][trace_operation] Function: {func.__name__}")
            logger.debug(f"[{operation_name}][trace_operation] Args: {args}")
            logger.debug(f"[{operation_name}][trace_operation] Kwargs: {kwargs}")
            
            with tracer.start_as_current_span(operation_name) as span:
                try:
                    logger.debug(f"[{operation_name}][trace_operation] Executing function")
                    result = await func(*args, **kwargs)
                    logger.debug(f"[{operation_name}][trace_operation] Function completed successfully")
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    log_decorator_error("trace_operation", operation_name, e, "function execution")
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise

        return cast(F, wrapper)
    return decorator

def with_retries(
    operation_name: str,
    max_attempts: Optional[int] = 3,
    initial_delay: float = 1.0,
    max_delay: float = 5.0,
    backoff_factor: float = 2.0,
    non_retryable_exceptions: tuple = (TokenTransferError, TokenNotFoundError, InvalidTokenAddressError)
) -> Callable[[F], F]:
    """Decorator that implements retry logic with exponential backoff."""
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"[{operation_name}][with_retries] Starting retry wrapper")
            logger.debug(f"[{operation_name}][with_retries] Max attempts: {max_attempts}")
            logger.debug(f"[{operation_name}][with_retries] Non-retryable exceptions: {non_retryable_exceptions}")
            
            delay = initial_delay
            last_exception = None
            attempts = max_attempts if isinstance(max_attempts, int) else 3

            for attempt in range(attempts):
                try:
                    logger.debug(f"[{operation_name}][with_retries] Attempt {attempt + 1}/{attempts}")
                    result = await func(*args, **kwargs)
                    logger.debug(f"[{operation_name}][with_retries] Attempt {attempt + 1} succeeded")
                    return result
                except non_retryable_exceptions as e:
                    log_decorator_error("with_retries", operation_name, e, "non-retryable error")
                    raise
                except Exception as e:
                    last_exception = e
                    log_decorator_error("with_retries", operation_name, e, f"attempt {attempt + 1}")
                    
                    if attempt < attempts - 1:
                        logger.warning(
                            f"[{operation_name}][with_retries] Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(f"[{operation_name}][with_retries] All {attempts} attempts failed")
                        raise last_exception

        return cast(F, wrapper)
    return decorator

def monitor_mode_performance(func: F) -> F:
    """Decorator to monitor Mode-specific performance metrics."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        operation_name = func.__name__
        logger.info(f"[{operation_name}][monitor_mode_performance] Starting monitoring")
        
        mode_config = kwargs.get("mode_config")
        network = getattr(args[0], "network", "unknown")
        logger.debug(f"[{operation_name}][monitor_mode_performance] Network: {network}")
        logger.debug(f"[{operation_name}][monitor_mode_performance] Mode config: {mode_config}")
        
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"[{operation_name}][monitor_mode_performance] Operation completed in {duration:.3f}s")
            
            if mode_config:
                TOKEN_OPERATION_DURATION.labels(
                    operation=operation_name,
                    network=str(network),
                    mode_enabled="true"
                ).observe(duration)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            log_decorator_error("monitor_mode_performance", operation_name, e, "performance monitoring")
            
            if mode_config:
                TOKEN_OPERATION_ERRORS.labels(
                    operation=operation_name,
                    network=str(network),
                    mode_enabled="true"
                ).inc()
                TOKEN_OPERATION_DURATION.labels(
                    operation=operation_name,
                    network=str(network),
                    mode_enabled="true"
                ).observe(duration)
            raise

    return cast(F, wrapper)

def monitor_mode_validation(func: F) -> F:
    """Decorator to monitor Mode-specific validation metrics.

    Args:
        func: Function to monitor

    Returns:
        Decorated function with validation monitoring
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        mode_config = kwargs.get("mode_config")
        if not mode_config:
            return await func(*args, **kwargs)

        validation_type = func.__name__
        network = getattr(args[0], "network", "unknown")

        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            MODE_VALIDATION_DURATION.labels(
                validation_type=validation_type,
                network=str(network),
                mode_enabled="true"
            ).observe(duration)

            return result
        except ValidationError as e:
            MODE_VALIDATION_FAILURES.labels(
                validation_type=e.validation_type,
                network=str(network),
                mode_enabled="true"
            ).inc()
            raise

    return cast(F, wrapper)

def log_mode_metrics(operation_name: str, metrics: Dict[str, Any]) -> None:
    """Log Mode-specific performance metrics.

    Args:
        operation_name: Name of the operation
        metrics: Dictionary of metrics to log
    """
    logger.info(
        f"Mode metrics for {operation_name}: "
        + ", ".join(f"{k}={v}" for k, v in metrics.items())
    )

class ValidationError(Exception):
    """Base class for validation errors."""

    def __init__(self, validation_type: str, *args: Any) -> None:
        self.validation_type = validation_type
        super().__init__(*args)

class NetworkValidationError(ValidationError):
    """Error raised when network validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__("network", message)

class MinTransferValidationError(ValidationError):
    """Error raised when minimum transfer validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__("min_transfer", message)

@monitor_mode_validation
async def _validate_network(network: Any, mode_config: Optional[ModeConfig] = None) -> None:
    """Validate network connection and health.

    Args:
        network: Network object containing connection details
        mode_config: Mode configuration for monitoring

    Raises:
        NetworkValidationError: If network validation fails
    """
    try:
        client = network.client
        if not client:
            raise NetworkValidationError("No client configured")

        # Check network health
        health = await client.get_health()
        if health != GetHealthResp("ok"):
            raise NetworkValidationError(f"Network health check failed: {health}")

        # Check network version
        try:
            version = await client.get_version()
            if not version:
                raise NetworkValidationError("Failed to get network version")
        except rpc_errors.NodeUnhealthy as e:
            raise NetworkValidationError(f"Network version check failed: {str(e)}")
        except Exception as e:
            raise NetworkValidationError(f"Network validation failed: {str(e)}")

    except Exception as e:
        if isinstance(e, NetworkValidationError):
            raise
        raise NetworkValidationError(f"Network validation failed: {str(e)}")

@monitor_mode_validation
async def validate_minimum_transfer(network: Any, amount: Optional[Union[int, float]] = None) -> None:
    """Validate minimum transfer amount.

    Args:
        network: Network object containing configuration
        amount: Transfer amount to validate

    Raises:
        MinTransferValidationError: If minimum transfer validation fails
    """
    if not amount:
        return

    min_transfer = getattr(network, "min_transfer_amount", None)
    if not min_transfer:
        return

    if amount < min_transfer:
        raise MinTransferValidationError(
            f"Transfer amount {amount} is below minimum {min_transfer}"
        )
