FROM python:3.11-slim

WORKDIR /app

# Install only essential system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY templates templates/

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
