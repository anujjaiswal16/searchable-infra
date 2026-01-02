"""
Demo application with OpenTelemetry instrumentation.
Sends traces, metrics, and logs to OpenTelemetry Collector.
"""

import logging
import random
import time
import os
from flask import Flask, render_template, jsonify, request
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource

# Get configuration from environment
app_version = os.getenv("APP_VERSION", os.getenv("TF_VAR_app_version", "v1.0.0"))
build_id = os.getenv("BUILD_ID", os.getenv("TF_VAR_build_id", "unknown"))
environment = os.getenv("ENVIRONMENT", os.getenv("TF_VAR_environment", "production"))
service_name = os.getenv("OTEL_SERVICE_NAME", os.getenv("TF_VAR_service_name", "demo-app"))
otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")

# Configure OpenTelemetry Resource with correlation fields
resource = Resource.create({
    "service.name": service_name,
    "service.version": app_version,
    "deployment.environment": environment,
    "ci.build.id": build_id,
    "region": "local",
})

# Setup OTel Tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otel_endpoint}/v1/traces"))
)

# Setup OTel Metrics
reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f"{otel_endpoint}/v1/metrics"),
    export_interval_millis=5000
)
provider = MeterProvider(metric_readers=[reader], resource=resource)
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__)

# Create metrics
request_counter = meter.create_counter(
    "demo.requests.total",
    description="Total number of requests"
)
request_duration = meter.create_histogram(
    "demo.requests.duration",
    description="Request duration in milliseconds",
    unit="ms"
)
error_counter = meter.create_counter(
    "demo.errors.total",
    description="Total number of errors"
)

# Setup OTel Logging
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{otel_endpoint}/v1/logs"))
)
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route('/')
def index():
    """Home page."""
    logger.info("Home page accessed", extra={
        "route": "/",
        "service.version": app_version,
        "ci.build.id": build_id
    })
    return render_template('index.html', 
                         app_version=app_version,
                         build_id=build_id,
                         environment=environment)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": service_name,
        "version": app_version,
        "build_id": build_id,
        "environment": environment
    })

@app.route('/action')
def action():
    """Simulate a user action with tracing."""
    start_time = time.time()
    request_counter.add(1, attributes={"route": "/action"})
    
    with tracer.start_as_current_span("user-action") as span:
        span.set_attribute("action.type", "button_click")
        span.set_attribute("service.version", app_version)
        span.set_attribute("ci.build.id", build_id)
        
        logger.info("User triggered an action", extra={
            "action_type": "button_click",
            "service.version": app_version
        })
        
        # Simulate some work
        time.sleep(random.uniform(0.1, 0.5))
        
        duration_ms = (time.time() - start_time) * 1000
        request_duration.record(duration_ms, attributes={"route": "/action"})
        
        trace_id = format(span.get_span_context().trace_id, "032x")
        
        return jsonify({
            "message": "Action processed successfully",
            "trace_id": trace_id,
            "duration_ms": round(duration_ms, 2),
            "service.version": app_version
        })

@app.route('/error')
def error():
    """Simulate an error for demo purposes."""
    error_counter.add(1, attributes={"route": "/error", "error_type": "simulated"})
    
    with tracer.start_as_current_span("error-simulation") as span:
        span.set_attribute("error.type", "simulated")
        span.set_attribute("error.message", "Simulated application error")
        span.set_status(trace.Status(trace.StatusCode.ERROR, "Simulated error"))
        
        logger.error("Simulated error occurred", extra={
            "error_code": 500,
            "error_type": "simulated",
            "service.version": app_version,
            "ci.build.id": build_id
        })
        
        try:
            raise Exception("Simulated application failure for demo")
        except Exception as e:
            span.record_exception(e)
            return jsonify({
                "error": "Something went wrong",
                "error_type": "simulated",
                "service.version": app_version
            }), 500

@app.route('/slow')
def slow():
    """Simulate a slow endpoint."""
    start_time = time.time()
    
    with tracer.start_as_current_span("slow-operation") as span:
        span.set_attribute("operation.type", "slow_query")
        
        # Simulate slow operation
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
        
        duration_ms = (time.time() - start_time) * 1000
        request_duration.record(duration_ms, attributes={"route": "/slow"})
        request_counter.add(1, attributes={"route": "/slow"})
        
        logger.warning("Slow operation completed", extra={
            "duration_ms": duration_ms,
            "threshold_exceeded": duration_ms > 2000
        })
        
        return jsonify({
            "message": "Slow operation completed",
            "duration_ms": round(duration_ms, 2)
        })

if __name__ == '__main__':
    logger.info(f"Starting {service_name} v{app_version} (build: {build_id})")
    app.run(host='0.0.0.0', port=5000, debug=False)
