FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN pip install flask opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-flask

CMD ["python", "app.py"]
