#!/bin/bash
# Verification script to check if the demo setup is correct

set -e

echo "🔍 Verifying demo setup..."
echo ""

# Check Docker
echo "✓ Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "✗ Docker is not installed"
    exit 1
fi
if ! command -v docker-compose &> /dev/null; then
    echo "✗ Docker Compose is not installed"
    exit 1
fi
echo "  Docker: $(docker --version)"
echo "  Docker Compose: $(docker-compose --version)"
echo ""

# Check required files
echo "✓ Checking required files..."
files=(
    "docker-compose.yml"
    "terraform/main.tf"
    "cicd/Jenkinsfile"
    "app/app.py"
    "app/Dockerfile"
    "app/requirements.txt"
    "otel/otel-collector.yaml"
    "utils/send_raw_logs.py"
    "elasticsearch/setup-pipelines.sh"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        exit 1
    fi
done
echo ""

# Check .env file
echo "✓ Checking environment configuration..."
if [ -f ".env" ]; then
    echo "  ✓ .env file exists"
    if grep -q "your-deployment" .env 2>/dev/null; then
        echo "  ⚠  .env file contains placeholder values - please update with your Elasticsearch credentials"
    else
        echo "  ✓ .env file appears configured"
    fi
else
    echo "  ⚠  .env file not found - create one from .env.example"
fi
echo ""

# Check if services are running
echo "✓ Checking Docker services..."
if docker ps | grep -q jenkins; then
    echo "  ✓ Jenkins is running"
else
    echo "  ⚠  Jenkins is not running (run: docker-compose up -d)"
fi

if docker ps | grep -q otel-collector; then
    echo "  ✓ OpenTelemetry Collector is running"
else
    echo "  ⚠  OpenTelemetry Collector is not running (run: docker-compose up -d)"
fi
echo ""

# Check network
echo "✓ Checking Docker network..."
if docker network ls | grep -q demo-network; then
    echo "  ✓ demo-network exists"
else
    echo "  ⚠  demo-network not found (will be created by docker-compose)"
fi
echo ""

echo "✅ Setup verification complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env with your Elasticsearch credentials"
echo "  2. Run: ./elasticsearch/setup-pipelines.sh"
echo "  3. Run: docker-compose up -d"
echo "  4. Configure Jenkins (see README.md)"

