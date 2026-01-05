# From Infrastructure as Code to Searchable Truth

A complete demo showcasing how infrastructure changes (Terraform), CI/CD pipeline metadata (Jenkins), and application telemetry (OpenTelemetry) can be correlated in Elasticsearch to reduce MTTR and improve root-cause analysis.

## 🎯 Demo Objective

Demonstrate that infrastructure changes are one of the biggest causes of incidents, and show how:

- **Terraform-driven infrastructure changes** → Indexed in Elasticsearch
- **CI/CD pipeline metadata** → Captured and correlated
- **Application telemetry** (logs, metrics, traces) → Sent via OpenTelemetry

All data is correlated using common fields (`service.name`, `environment`, `app.version`, `@timestamp`, `infra.change_id`, `ci.pipeline_id`) to enable unified analysis in Kibana.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Step 1: Infrastructure Changes           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Terraform ──┐                                                │
│              ├──> Parse, Enrich & Format ──> infra-raw-events │
│  Jenkins ────┘                                                │
│                                                               │
│  Elasticsearch Ingest Pipeline ──> infra-changes-*           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Correlation Keys:
                          │ • @timestamp
                          │ • service.name
                          │ • environment
                          │ • region
                          │ • infra.change_id
                          │ • ci.pipeline_id
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Step 2: Observability Data                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  APM Traces ──┐                                               │
│  Metrics ─────┼──> OpenTelemetry Collector ──> Elasticsearch │
│  Logs ────────┘                                               │
│                                                               │
│  Unified Timeline • Correlate • AI Assistant Insights        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **Elastic Cloud** account (or Elasticsearch cluster) with:
  - Endpoint URL
  - API Key with write permissions
- **Git** (for cloning the repository)

## 🚀 Quick Start

### 1. Clone the Repository

    ```bash
git clone <repository-url>
    cd elastic-hashicorp-searchable-infra-demo
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```bash
cat > .env << EOF
ELASTIC_CLOUD_ENDPOINT=https://your-deployment.es.us-east-1.aws.cloud.es.io:443
ELASTIC_API_KEY=your-api-key-here
EOF
```

**Important:** Replace with your actual Elastic Cloud endpoint and API key.

### 3. Setup Elasticsearch

#### 3.1. Create Index Template (No Ingest Pipeline)

Since we're sending raw data and will use Elastic Stream feature later, we only need the index template:

```bash
export ELASTIC_CLOUD_ENDPOINT="https://your-deployment.es.us-east-1.aws.cloud.es.io:443"
export ELASTIC_API_KEY="your-api-key-here"

./elasticsearch/setup-index-template.sh
```

This script will:
- Create index template for `infra-raw-events*` without default pipeline
- Set up proper field mappings for correlation

**Note:** If you want to use ingest pipelines instead, you can run `./elasticsearch/setup-pipelines.sh` which creates both the pipeline and template.

### 4. Start the Demo Environment

```bash
docker-compose up -d
```

This will start:
- **Jenkins** on `http://localhost:8080`
- **OpenTelemetry Collector** (listening on ports 4317/4318)
- **Application** (will be created by Terraform via Jenkins)

### 5. Configure Jenkins

#### 5.1. Get Initial Admin Password

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### 5.2. Access Jenkins UI

1. Open `http://localhost:8080` in your browser
2. Enter the initial admin password
3. Install suggested plugins
4. Create an admin user (or skip)

#### 5.3. Configure Elasticsearch Credentials

1. Go to **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. Click **Add Credentials**
3. Add two **Secret text** credentials:
   - **ID:** `ELASTIC_CLOUD_ENDPOINT`
     - **Secret:** Your Elastic Cloud endpoint URL
   - **ID:** `ELASTIC_API_KEY`
     - **Secret:** Your Elastic API key

#### 5.4. Create Pipeline Job

1. Click **New Item**
2. Name it `infrastructure-pipeline`
3. Select **Pipeline**
4. In **Pipeline** section:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `file:///var/jenkins_home/workspace` (or your repo path)
   - **Script Path:** `cicd/Jenkinsfile`
5. Click **Save**

### 6. Run the Pipeline

1. Click on the `infrastructure-pipeline` job
2. Click **Build Now**
3. Watch the pipeline execute:
   - Terraform Init
   - Terraform Plan (logs sent to Elasticsearch)
   - Terraform Apply (creates Docker container)
   - Verify Deployment

### 7. Generate Application Telemetry

Once the application is running (after Terraform Apply):

```bash
# Access the application
curl http://localhost:5000/

# Generate some traffic
curl http://localhost:5000/action
curl http://localhost:5000/error
curl http://localhost:5000/slow
```

Or open `http://localhost:5000` in your browser and click the buttons.

## 📊 Viewing Data in Kibana

### 1. Access Kibana

1. Log into your Elastic Cloud deployment
2. Navigate to **Kibana**

### 2. Discover Infrastructure Changes

1. Go to **Discover**
2. Select index pattern: `infra-raw-events*` or `infra-changes*`
3. Filter by:
   - `log.type: terraform_plan` or `log.type: terraform_apply`
   - `service.name: demo-app`
   - `environment: production`

### 3. View Application Telemetry

1. Go to **APM** → **Services**
2. Select `demo-app`
3. View traces, metrics, and logs

### 4. Correlate Infrastructure Changes with Application Issues

**Example Query in Discover:**

```
service.name: demo-app AND 
(@timestamp >= now()-1h) AND 
(infra.change_id: * OR ci.pipeline_id: *)
```

**Create a Dashboard:**

1. Go to **Dashboard** → **Create Dashboard**
2. Add visualizations:
   - **Infrastructure Changes Timeline** (from `infra-changes*`)
   - **Application Errors** (from APM)
   - **Request Latency** (from APM metrics)
3. Correlate by:
   - `@timestamp`
   - `service.name`
   - `environment`
   - `infra.change_id` / `ci.pipeline_id`

### 5. Root Cause Analysis Story

**Scenario:** Application errors spike after infrastructure change

1. **Identify the incident:**
   - APM shows error rate increase at `2024-01-15 14:30:00`

2. **Find infrastructure changes:**
   - Search `infra-changes*` for changes around that time
   - Filter: `@timestamp:[2024-01-15T14:25:00 TO 2024-01-15T14:35:00]`

3. **Correlate:**
   - Match `service.name: demo-app`
   - Match `environment: production`
   - View the Terraform plan/apply logs

4. **Root cause:**
   - "Terraform applied container restart at 14:28:00"
   - "Application errors started at 14:30:00"
   - **Conclusion:** Container restart caused application instability

## 🔍 Correlation Fields

All data is correlated using these common fields:

| Field | Source | Purpose |
|-------|--------|---------|
| `@timestamp` | All | Time-based correlation |
| `service.name` | Terraform vars, OTel resource | Service identification |
| `service.version` | Terraform vars, OTel resource | Version tracking |
| `environment` | Terraform vars, OTel resource | Environment filtering |
| `region` | All | Geographic/contextual grouping |
| `infra.change_id` | CI/CD pipeline | Unique change identifier |
| `ci.pipeline_id` | Jenkins | Pipeline run identifier |
| `ci.build.id` | Jenkins | Build identifier |

## 📁 Repository Structure

```
.
├── app/                    # Sample Flask application
│   ├── app.py             # OpenTelemetry-instrumented app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── templates/
├── cicd/                   # CI/CD configurations
│   └── Jenkinsfile        # Jenkins pipeline
├── elasticsearch/         # Elasticsearch setup
│   ├── setup-pipelines.sh # Setup script
│   └── ingest-pipelines.json
├── jenkins/               # Jenkins Docker setup
│   ├── Dockerfile
│   └── plugins.txt
├── otel/                  # OpenTelemetry Collector
│   └── otel-collector.yaml
├── terraform/             # Infrastructure as Code
│   └── main.tf           # Docker provider Terraform
├── utils/                 # Utility scripts
│   └── send_raw_logs.py  # Send logs to Elasticsearch
├── docker-compose.yml     # Orchestration
└── README.md
```

## 🧪 Testing the Demo

### Test Infrastructure Changes

1. Modify `terraform/main.tf` (e.g., change container name)
2. Run Jenkins pipeline again
3. Verify new logs appear in `infra-raw-events*`

### Test Application Telemetry

```bash
# Generate normal traffic
for i in {1..10}; do
  curl http://localhost:5000/action
  sleep 0.5
done

# Generate errors
for i in {1..5}; do
  curl http://localhost:5000/error
  sleep 0.5
done

# Generate slow requests
for i in {1..3}; do
  curl http://localhost:5000/slow
done
```

### Verify Correlation

In Kibana Discover, search for:

```
service.name: demo-app AND 
@timestamp >= now()-15m
```

You should see:
- Infrastructure change events
- Application traces
- Application logs
- Application metrics

All correlated by `service.name`, `environment`, and `@timestamp`.

## 🛠️ Troubleshooting

### Jenkins can't access Docker

Ensure Docker socket is mounted:
```bash
docker-compose down
docker-compose up -d
```

Check Jenkins logs:
```bash
docker logs jenkins
```

### Terraform fails in Jenkins

Check Terraform is installed:
```bash
docker exec jenkins terraform version
```

### Application not receiving telemetry

Check OpenTelemetry Collector:
```bash
docker logs otel-collector
```

Verify environment variables:
```bash
docker exec <app-container> env | grep OTEL
```

### No data in Elasticsearch

1. Verify credentials in Jenkins
2. Check Elasticsearch connection:
   ```bash
   curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
        "$ELASTIC_CLOUD_ENDPOINT/_cluster/health"
   ```
3. Verify ingest pipeline:
   ```bash
   curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
        "$ELASTIC_CLOUD_ENDPOINT/_ingest/pipeline/terraform-logs-parser"
   ```

## 🎤 Demo Script

### Part 1: Setup (5 minutes)

1. Show the architecture diagram
2. Explain correlation strategy
3. Start Docker Compose
4. Show Jenkins pipeline

### Part 2: Infrastructure Change (5 minutes)

1. Run Jenkins pipeline
2. Show Terraform plan/apply in Jenkins console
3. Open Kibana Discover → `infra-raw-events*`
4. Show raw logs being ingested
5. Show parsed logs in `infra-changes*` (if using separate index)

### Part 3: Application Telemetry (5 minutes)

1. Show application running
2. Generate traffic (normal + errors)
3. Open Kibana APM → Services → `demo-app`
4. Show traces, metrics, logs

### Part 4: Correlation & RCA (10 minutes)

1. Create a timeline visualization
2. Show infrastructure change at time T
3. Show application error spike at time T+2min
4. Correlate using common fields
5. **Demo the RCA story:**
   - "Infrastructure change caused this incident"
   - "We can see the exact Terraform change"
   - "MTTR reduced from hours to minutes"

### Part 5: Q&A (5 minutes)

## 📝 Notes

- All infrastructure runs locally in Docker (no cloud resources)
- Elasticsearch is assumed to be Elastic Cloud (external)
- Terraform only runs via Jenkins pipeline (no manual runs)
- Raw logs go to `infra-raw-events*`, parsing done by ingest pipelines
- Correlation is key: ensure all components use the same field names

## 🔗 Resources

- [Terraform Docker Provider](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs)
- [OpenTelemetry](https://opentelemetry.io/)
- [Elasticsearch Ingest Pipelines](https://www.elastic.co/guide/en/elasticsearch/reference/current/ingest.html)
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)

## 📄 License

[Add your license here]

---

**Built for Elastic + HashiCorp Community Events**
