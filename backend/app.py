
import logging
import random
import time
import os
from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import extract

# Logging imports
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# Setup OTel
otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")
service_name = os.getenv("OTEL_SERVICE_NAME", "backend-service")
app_version = os.getenv("APP_VERSION", "v1.0.0")
environment = os.getenv("ENVIRONMENT", "production")

resource = Resource.create({
    "service.name": service_name,
    "service.version": app_version,
    "deployment.environment": environment,
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otel_endpoint}/v1/traces"))
)

# Setup OTLP Logging
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{otel_endpoint}/v1/logs"))
)
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/data')
def get_data():
    # Simulate latency
    latency = float(os.getenv("SIMULATED_LATENCY", "0"))
    if latency > 0:
        time.sleep(latency)
        
    # Simulate errors
    error_rate = float(os.getenv("SIMULATED_ERROR_RATE", "0"))
    if random.random() * 100 < error_rate:
        logger.error("Simulated backend error")
        return jsonify({"error": "Simulated backend failure"}), 500
        
    return jsonify({
        "data": "Important backend data",
        "service": service_name,
        "version": app_version
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
