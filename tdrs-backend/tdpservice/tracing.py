"""OpenTelemetry tracing configuration for the TDP application."""

from django.conf import settings

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

logger = logging.getLogger(__name__)

def initialize_tracer():
    """Initialize the OpenTelemetry tracer with proper service name and configuration."""

    if settings.OTEL_EXPORTER_OTLP_ENDPOINT in [None, ""]:
        logger.warning("OTEL Exporter Endpoint is empty, disabling tracing.")
        return

    # Create a resource with service name
    resource = Resource.create({"service.name": "tdp-backend"})

    # Create a tracer provider with the resource
    tracer_provider = TracerProvider(resource=resource)

    # Configure the OTLP exporter to send traces to Tempo
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,  # OTLP gRPC endpoint
        insecure=True,
    )

    # Add the exporter to the tracer provider
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Instrument Django
    DjangoInstrumentor().instrument(tracer_provider=tracer_provider)

    # Instrument PostgreSQL
    Psycopg2Instrumentor().instrument(
        tracer_provider=tracer_provider,
        # Add database-specific attributes to spans
        enable_commenter=True,
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
