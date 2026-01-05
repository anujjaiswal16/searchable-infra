# Troubleshooting Guide

## Common Errors and Solutions

### Error: "pipeline with id [terraform-logs-parser] does not exist"

**Problem:** The Elasticsearch ingest pipeline hasn't been created yet.

**Solution:**
1. Make sure you've set your Elasticsearch credentials:
   ```bash
   export ELASTIC_CLOUD_ENDPOINT="https://your-deployment.es.us-east-1.aws.cloud.es.io:443"
   export ELASTIC_API_KEY="your-api-key-here"
   ```

2. Run the setup script:
   ```bash
   ./elasticsearch/setup-pipelines.sh
   ```

3. Verify the pipeline was created:
   ```bash
   curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
        "$ELASTIC_CLOUD_ENDPOINT/_ingest/pipeline/terraform-logs-parser"
   ```

**Note:** The updated `send_raw_logs.py` script will now handle this gracefully by:
- Detecting the missing pipeline
- Indexing to an alternative index (`infra-raw-events-raw`) without the pipeline
- Providing clear instructions to run the setup script

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
2. ✅ Ingest pipelines are created (`./elasticsearch/setup-pipelines.sh`)
3. ✅ Pipeline is running successfully
4. ✅ Check Elasticsearch connection:
   ```bash
   curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
        "$ELASTIC_CLOUD_ENDPOINT/_cluster/health"
   ```
5. ✅ Check if data is being indexed:
   ```bash
   curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
        "$ELASTIC_CLOUD_ENDPOINT/infra-raw-events*/_search?size=1"
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

