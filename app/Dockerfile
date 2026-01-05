FROM python:3.11-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies directly (no requirements.txt needed)
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    opentelemetry-api==1.21.0 \
    opentelemetry-sdk==1.21.0 \
    opentelemetry-exporter-otlp==1.21.0 \
    opentelemetry-instrumentation==0.42b0 \
    opentelemetry-instrumentation-flask==0.42b0

# Copy application
COPY app.py .
COPY templates templates/

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
