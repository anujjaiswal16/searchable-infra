# Troubleshooting Guide

## Common Errors and Solutions

### Error: "pip install --no-cache-dir -r requirements.txt" failed (exit code 1)

**Problem:** Docker build fails when installing Python dependencies.

**Possible Causes:**
1. Network connectivity issues during build
2. Missing system dependencies for compiling Python packages
3. Package version conflicts
4. Outdated pip/setuptools

**Solutions:**

1. **Check the build logs** - The error message should show which package failed
2. **Try building manually** to see full error:
   ```bash
   cd app
   docker build -t demo-app:test . 2>&1 | tee build.log
   ```
3. **Check network connectivity** - The build needs internet to download packages
4. **Verify Dockerfile** - Make sure it includes:
   - `gcc`, `g++`, `make` for compiling packages
   - `libffi-dev`, `libssl-dev` for SSL support
   - `pip install --upgrade pip` before installing packages

5. **Try installing packages individually** to find the problematic one:
   ```bash
   docker run -it --rm python:3.10-slim bash
   pip install flask
   pip install opentelemetry-api
   # etc.
   ```

6. **Use a simpler requirements.txt** - Remove version constraints temporarily:
   ```txt
   flask
   opentelemetry-api
   opentelemetry-sdk
   opentelemetry-exporter-otlp
   opentelemetry-instrumentation
   opentelemetry-instrumentation-flask
   elasticsearch
   ```

### Error: "permission denied while trying to connect to the Docker daemon socket"

**Problem:** Jenkins container doesn't have permission to access the Docker socket.

**Solution:** The docker-compose.yml is configured to run Jenkins as root to access Docker. If you prefer not to run as root:

1. **Option 1: Fix Docker socket permissions (recommended for production)**
   ```bash
   # On the host, check docker group GID
   getent group docker
   
   # Update Jenkins Dockerfile to use the same GID
   # Then rebuild: docker-compose build jenkins
   ```

2. **Option 2: Use Docker-in-Docker (DinD)**
   - Mount a Docker-in-Docker container
   - More complex but more secure

3. **Option 3: Keep running as root (current setup - fine for demo)**
   - The docker-compose.yml already sets `user: root`
   - This works for local demos

**Current Setup:** Jenkins runs as root in the container, which allows access to the Docker socket. This is acceptable for local demos.

### Error: "pipeline with id [terraform-logs-parser] does not exist"

**Problem:** The Elasticsearch ingest pipeline hasn't been created yet.

**Solution:**
1. Make sure you've set your Elasticsearch credentials:
   ```bash
   export ELASTIC_CLOUD_ENDPOINT="https://your-deployment.es.us-east-1.aws.cloud.es.io:443"
   export ELASTIC_API_KEY="your-api-key-here"
   ```

2. Run the setup script to create index template (no pipeline needed):
   ```bash
   ./elasticsearch/setup-index-template.sh
   ```

3. If you previously ran `setup-pipelines.sh`, remove the default pipeline:
   ```bash
   ./elasticsearch/remove-pipeline-from-template.sh
   ```

**Note:** The updated `send_raw_logs.py` script will now handle this gracefully by indexing to `infra-raw-events-raw` if the main index has pipeline issues.

### Error: "Bad substitution" in Jenkins Pipeline

**Problem:** Jenkins is using `/bin/sh` which doesn't support bash-specific syntax.

**Solution:** This has been fixed in the latest Jenkinsfile. Make sure you're using the updated version that:
- Captures output first, then sends to Elasticsearch
- Uses Python module imports instead of shell pipes
- Properly handles variable interpolation

### Error: "No credentials specified" for Git

**Problem:** Jenkins is trying to checkout from Git but the repository isn't configured.

**Solution:** 
- The Jenkinsfile now handles this gracefully
- If using mounted volumes, the pipeline will continue without Git checkout
- If using Git SCM, make sure your repository is properly configured

### Error: Terraform can't find Docker network

**Problem:** Terraform is trying to use `demo-network` but it doesn't exist yet.

**Solution:**
1. Make sure Docker Compose has started:
   ```bash
   docker-compose up -d
   ```

2. Verify the network exists:
   ```bash
   docker network ls | grep demo-network
   ```

3. If it doesn't exist, create it:
   ```bash
   docker network create demo-network
   ```

### Error: Application container can't connect to OpenTelemetry Collector

**Problem:** The application container is on a different network than the collector.

**Solution:**
- Make sure Terraform creates the container on the `demo-network`
- Verify the container can resolve `otel-collector` hostname:
  ```bash
  docker exec <app-container> ping otel-collector
  ```

### No data appearing in Elasticsearch

**Checklist:**
1. ✅ Elasticsearch credentials are set in Jenkins
2. ✅ Index template is created (`./elasticsearch/setup-index-template.sh`)
3. ✅ Pipeline is running successfully
4. ✅ Check Elasticsearch connection:
   ```bash
   curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
        "$ELASTIC_CLOUD_ENDPOINT/_cluster/health"
   ```
5. ✅ Check if data is being indexed:
   ```bash
   curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
        "$ELASTIC_CLOUD_ENDPOINT/infra-raw-events-raw*/_search?size=1"
   ```

### Application not sending telemetry

**Checklist:**
1. ✅ Application container is running
2. ✅ OpenTelemetry Collector is running
3. ✅ Check collector logs:
   ```bash
   docker logs otel-collector
   ```
4. ✅ Verify environment variables in app container:
   ```bash
   docker exec <app-container> env | grep OTEL
   ```
5. ✅ Check application logs:
   ```bash
   docker logs <app-container>
   ```

## Getting Help

If you encounter other issues:
1. Check the Jenkins pipeline console output
2. Check Docker container logs
3. Verify all environment variables are set
4. Review the README.md for setup instructions
