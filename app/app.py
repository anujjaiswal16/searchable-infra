"""
Simple demo application with OpenTelemetry instrumentation.
Sends traces, metrics, and logs to OpenTelemetry Collector.
"""

import logging
import random
import time
import os
from flask import Flask, render_template, jsonify

# OpenTelemetry imports - use minimal set
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    
    # Setup tracing
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")
    app_version = os.getenv("APP_VERSION", "v1.0.0")
    build_id = os.getenv("BUILD_ID", "unknown")
    environment = os.getenv("ENVIRONMENT", "production")
    service_name = os.getenv("OTEL_SERVICE_NAME", "demo-app")
    
    resource = Resource.create({
        "service.name": service_name,
        "service.version": app_version,
        "deployment.environment": environment,
        "ci.build.id": build_id,
        "region": "local",
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otel_endpoint}/v1/traces"))
    )
    
    OTEL_ENABLED = True
except ImportError as e:
    print(f"OpenTelemetry not available: {e}")
    OTEL_ENABLED = False
    tracer = None

# Create Flask app
app = Flask(__name__)

if OTEL_ENABLED:
    FlaskInstrumentor().instrument_app(app)

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Home page."""
    # Simulated latency from infrastructure config
    try:
        latency = float(os.getenv("SIMULATED_LATENCY", "0"))
        if latency > 0:
            time.sleep(latency)
    except ValueError:
        pass

    logger.info("Home page accessed", extra={
        "route": "/",
        "service.version": os.getenv("APP_VERSION", "v1.0.0"),
        "simulated_latency": latency if 'latency' in locals() else 0
    })
    return render_template('index.html',
                         app_version=os.getenv("APP_VERSION", "v1.0.0"),
                         # ... existing args ...
                         build_id=os.getenv("BUILD_ID", "unknown"),
                         environment=os.getenv("ENVIRONMENT", "production"))

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": os.getenv("OTEL_SERVICE_NAME", "demo-app"),
        "version": os.getenv("APP_VERSION", "v1.0.0"),
        "build_id": os.getenv("BUILD_ID", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "production")
    })

@app.route('/action')
def action():
    """Simulate a user action with tracing."""
    if OTEL_ENABLED and tracer:
        span = tracer.start_span("user-action")
        span.set_attribute("action.type", "button_click")
        span.set_attribute("service.version", os.getenv("APP_VERSION", "v1.0.0"))
    else:
        span = None
    
    try:
        logger.info("User triggered an action", extra={
            "action_type": "button_click",
            "service.version": os.getenv("APP_VERSION", "v1.0.0")
        })
        
        # Simulate some work
        time.sleep(random.uniform(0.1, 0.5))
        
        try:
            trace_id = format(span.get_span_context().trace_id, "032x") if span and span.get_span_context() else "no-trace"
        except:
            trace_id = "no-trace"
        
        return jsonify({
            "message": "Action processed successfully",
            "trace_id": trace_id,
            "service.version": os.getenv("APP_VERSION", "v1.0.0")
        })
    finally:
        if span:
            span.end()

@app.route('/error')
def error():
    """Simulate an error for demo purposes."""
    if OTEL_ENABLED and tracer:
        span = tracer.start_span("error-simulation")
        span.set_attribute("error.type", "simulated")
        try:
            from opentelemetry.trace import Status, StatusCode
            span.set_status(Status(StatusCode.ERROR, "Simulated error"))
        except ImportError:
            pass  # Status API might not be available
    else:
        span = None
    
    try:
        logger.error("Simulated error occurred", extra={
            "error_code": 500,
            "error_type": "simulated",
            "service.version": os.getenv("APP_VERSION", "v1.0.0")
        })
        
        raise Exception("Simulated application failure for demo")
    except Exception as e:
        if span:
            try:
                span.record_exception(e)
            except:
                pass
            span.end()
        return jsonify({
            "error": "Something went wrong",
            "error_type": "simulated",
            "service.version": os.getenv("APP_VERSION", "v1.0.0")
        }), 500

@app.route('/slow')
def slow():
    """Simulate a slow endpoint."""
    if OTEL_ENABLED and tracer:
        span = tracer.start_span("slow-operation")
        span.set_attribute("operation.type", "slow_query")
    else:
        span = None
    
    try:
        # Simulate slow operation
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)
        
        logger.warning("Slow operation completed", extra={
            "duration_seconds": delay,
            "threshold_exceeded": delay > 2.0
        })
        
        return jsonify({
            "message": "Slow operation completed",
            "duration_seconds": round(delay, 2)
        })
    finally:
        if span:
            span.end()

if __name__ == '__main__':
    logger.info(f"Starting {os.getenv('OTEL_SERVICE_NAME', 'demo-app')} v{os.getenv('APP_VERSION', 'v1.0.0')} (build: {os.getenv('BUILD_ID', 'unknown')})")
    app.run(host='0.0.0.0', port=5000, debug=False)
