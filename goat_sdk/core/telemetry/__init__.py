"""Telemetry module for GOAT SDK."""

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode

# Create resource for identifying the service
resource = Resource.create({
    "service.name": "goat-sdk",
    "service.version": "0.1.0",
})

# Initialize tracer provider with resource
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Initialize meter provider with resource
meter_provider = MeterProvider(resource=resource)
metrics.set_meter_provider(meter_provider)

# Create tracer and meter instances
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create metrics
transaction_counter = meter.create_counter(
    "goat_sdk_transactions",
    description="Number of blockchain transactions",
    unit="1",
)

transaction_latency = meter.create_histogram(
    "goat_sdk_transaction_latency",
    description="Latency of blockchain transactions",
    unit="ms",
)

error_counter = meter.create_counter(
    "goat_sdk_errors",
    description="Number of errors",
    unit="1",
)

def track_transaction(chain: str, status: str, latency: float):
    """Track a blockchain transaction.
    
    Args:
        chain: The blockchain network
        status: Transaction status (success/failure)
        latency: Transaction latency in milliseconds
    """
    transaction_counter.add(1, {"chain": chain, "status": status})
    transaction_latency.record(latency, {"chain": chain})

def track_error(error_type: str, error_message: str):
    """Track an error.
    
    Args:
        error_type: Type of error
        error_message: Error message
    """
    error_counter.add(1, {
        "error_type": error_type,
        "error_message": error_message
    })
