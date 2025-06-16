"""OpenTelemetry tracing configuration for the TDP application."""

import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

logger = logging.getLogger(__name__)


def initialize_tracer():
    """Initialize the OpenTelemetry tracer with proper service name and configuration."""
    # Create a resource with service name
    resource = Resource.create({"service.name": "tdp-backend"})

    # Create a tracer provider with the resource
    tracer_provider = TracerProvider(resource=resource)

    # Configure the OTLP exporter to send traces to Tempo
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://tempo:4317",  # OTLP gRPC endpoint
        insecure=True,  # Don't use TLS for local development
    )

    # Add the exporter to the tracer provider
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Instrument Django
    DjangoInstrumentor().instrument()

    # Instrument PostgreSQL
    Psycopg2Instrumentor().instrument(
        tracer_provider=tracer_provider,
        # Add database-specific attributes to spans
        enable_commenter=True,
        # Include query parameters in spans (be careful with sensitive data)
        # Set to False in production if queries might contain sensitive information
        include_db_statement=True
    )

    # Instrument Redis
    RedisInstrumentor().instrument(tracer_provider=tracer_provider)

    # Instrument Celery
    CeleryInstrumentor().instrument(tracer_provider=tracer_provider)

    # Instrument boto3/botocore for S3
    BotocoreInstrumentor().instrument(tracer_provider=tracer_provider)

    # Instrument requests for external HTTP calls
    RequestsInstrumentor().instrument(tracer_provider=tracer_provider)

    logger.info("OpenTelemetry tracing initialized for tdp-backend.")
    return tracer_provider


class TracingMiddleware:
    """Middleware to extract trace context from incoming requests and create spans."""

    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response
        self.propagator = TraceContextTextMapPropagator()
        self.tracer = trace.get_tracer("tdp-backend.middleware")

    def __call__(self, request):
        """Process the request and extract trace context."""
        # Extract context from headers
        carrier = {}
        for header_name, header_value in request.headers.items():
            carrier[header_name] = header_value

        # Get the current context from the carrier
        context = self.propagator.extract(carrier=carrier)

        # Start a new span for this request
        with self.tracer.start_as_current_span(
            f"{request.method} {request.path}",
            context=context,
            kind=trace.SpanKind.SERVER,
        ) as span:
            # Add request details to the span
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", request.build_absolute_uri())
            span.set_attribute("http.target", request.path)
            span.set_attribute("http.host", request.get_host())

            # Preserve the original service name if it's provided in the request
            if 'x-service-name' in request.headers:
                span.set_attribute("service.name", request.headers['x-service-name'])
            else:
                span.set_attribute("service.name", "tdp-backend")

            # Add database context to help correlate database operations with this request
            span.set_attribute("db.system", "postgresql")

            # Add the endpoint path as an attribute to help identify which endpoints are making database queries
            span.set_attribute("http.route",
                               request.resolver_match.route if hasattr(request, 'resolver_match')
                               and request.resolver_match else request.path)

            # If user is authenticated, add user info
            if hasattr(request, "user") and request.user.is_authenticated:
                span.set_attribute("enduser.id", str(request.user.id))
                span.set_attribute("enduser.username", request.user.username)

            # Process the request
            response = self.get_response(request)

            # Add response details to the span
            span.set_attribute("http.status_code", response.status_code)

            return response
