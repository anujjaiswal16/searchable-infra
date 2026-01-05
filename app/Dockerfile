FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies with better error handling
RUN pip install --no-cache-dir flask && \
    pip install --no-cache-dir opentelemetry-api opentelemetry-sdk && \
    pip install --no-cache-dir opentelemetry-exporter-otlp && \
    pip install --no-cache-dir opentelemetry-instrumentation opentelemetry-instrumentation-flask && \
    pip install --no-cache-dir elasticsearch || \
    (echo "=== Installation failed, showing requirements ===" && cat requirements.txt && exit 1)

# Copy application code
COPY . .

CMD ["python", "app.py"]
