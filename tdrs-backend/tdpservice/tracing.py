"""OpenTelemetry tracing configuration for the TDP application."""

import logging
from django.conf import settings

# Import OpenTelemetry modules
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
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

    logger.info("OpenTelemetry tracing initialized for tdp-backend service")
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
            
            # If user is authenticated, add user info
            if hasattr(request, "user") and request.user.is_authenticated:
                span.set_attribute("enduser.id", str(request.user.id))
                span.set_attribute("enduser.username", request.user.username)
            
            # Process the request
            response = self.get_response(request)
            
            # Add response details to the span
            span.set_attribute("http.status_code", response.status_code)
            
            return response
