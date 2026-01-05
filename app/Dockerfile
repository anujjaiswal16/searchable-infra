FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install Python packages - install in separate steps for better error visibility
RUN pip install --no-cache-dir flask || (echo "Failed to install flask" && exit 1)

RUN pip install --no-cache-dir opentelemetry-api opentelemetry-sdk || (echo "Failed to install opentelemetry-api/sdk" && exit 1)

RUN pip install --no-cache-dir opentelemetry-exporter-otlp || (echo "Failed to install opentelemetry-exporter-otlp" && exit 1)

RUN pip install --no-cache-dir opentelemetry-instrumentation opentelemetry-instrumentation-flask || (echo "Failed to install opentelemetry-instrumentation" && exit 1)

RUN pip install --no-cache-dir elasticsearch || (echo "Failed to install elasticsearch" && exit 1)

# Copy application code
COPY . .

CMD ["python", "app.py"]
