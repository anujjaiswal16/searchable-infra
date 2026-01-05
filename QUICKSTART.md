# Quick Start Guide

Get the demo running in 5 minutes!

## Prerequisites

- Docker & Docker Compose
- Elastic Cloud account (or Elasticsearch cluster)

## Steps

### 1. Clone and Configure

```bash
git clone <repo-url>
cd elastic-hashicorp-searchable-infra-demo
```

### 2. Set Elasticsearch Credentials

```bash
cat > .env << EOF
ELASTIC_CLOUD_ENDPOINT=https://your-deployment.es.us-east-1.aws.cloud.es.io:443
ELASTIC_API_KEY=your-api-key-here
EOF
```

### 3. Setup Elasticsearch

```bash
export ELASTIC_CLOUD_ENDPOINT="https://your-deployment.es.us-east-1.aws.cloud.es.io:443"
export ELASTIC_API_KEY="your-api-key-here"
./elasticsearch/setup-index-template.sh
```

**Note:** This creates the index template without ingest pipelines. Raw data will be indexed, and you can use Elastic Stream feature to process it later.

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Configure Jenkins

1. Get initial password:
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```

2. Open `http://localhost:8080` and complete setup

3. Add credentials:
   - **Manage Jenkins** → **Credentials** → **Add**
   - Add `ELASTIC_CLOUD_ENDPOINT` (Secret text)
   - Add `ELASTIC_API_KEY` (Secret text)

4. Create pipeline:
   - **New Item** → **Pipeline**
   - Name: `infrastructure-pipeline`
   - **Important:** Select **Pipeline script** (NOT "Pipeline script from SCM")
   - Copy the entire contents of `cicd/Jenkinsfile` into the script text area
   - Click **Save**
   
   **Note:** Using "Pipeline script" directly allows Jenkins to use the mounted volume files without Git checkout. See `JENKINS_SETUP.md` for alternatives.

### 6. Run Pipeline

1. Click **Build Now**
2. Watch it create the application container
3. Access app at `http://localhost:5000`

### 7. View in Kibana

- **Discover:** `infra-raw-events*` or `infra-changes*`
- **APM:** Services → `demo-app`

## That's It! 🎉

See `README.md` for detailed documentation and `DEMO_GUIDE.md` for presentation tips.

