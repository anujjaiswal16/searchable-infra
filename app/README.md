# Demo Application

A simple Flask application for the Elastic + HashiCorp demo.

## Features

- Minimal dependencies (only Flask and OpenTelemetry)
- Sends traces to OpenTelemetry Collector
- Simple endpoints for demo purposes
- No complex build requirements

## Endpoints

- `/` - Home page with UI
- `/health` - Health check
- `/action` - Simulates a user action (generates trace)
- `/error` - Simulates an error (generates error trace)
- `/slow` - Simulates a slow operation

## Environment Variables

- `OTEL_EXPORTER_OTLP_ENDPOINT` - OpenTelemetry Collector endpoint (default: http://otel-collector:4318)
- `OTEL_SERVICE_NAME` - Service name (default: demo-app)
- `APP_VERSION` - Application version
- `BUILD_ID` - Build ID from CI/CD
- `ENVIRONMENT` - Deployment environment

## Building

```bash
docker build -t demo-app:test .
docker run -p 5000:5000 demo-app:test
```

## Dependencies

- Flask 3.0.0 - Web framework
- OpenTelemetry packages - For observability

All dependencies are pure Python (no C extensions), so no build tools needed!

