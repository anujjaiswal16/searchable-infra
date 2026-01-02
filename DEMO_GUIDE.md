# Live Demo Guide: From Infrastructure as Code to Searchable Truth

This guide provides a step-by-step script for presenting the demo at the Elastic + HashiCorp community event.

## 🎯 Demo Goals

1. Show infrastructure changes are a major cause of incidents
2. Demonstrate correlation between Terraform, CI/CD, and application telemetry
3. Highlight MTTR reduction through unified observability
4. Make the RCA story visual and obvious

## ⏱️ Timeline (30 minutes)

- **Setup & Introduction:** 5 min
- **Infrastructure Change:** 8 min
- **Application Telemetry:** 7 min
- **Correlation & RCA:** 8 min
- **Q&A:** 2 min

## 📋 Pre-Demo Checklist

- [ ] Docker and Docker Compose installed
- [ ] Elastic Cloud credentials ready
- [ ] `.env` file configured
- [ ] Elasticsearch ingest pipelines set up
- [ ] Docker Compose services running
- [ ] Jenkins configured with credentials
- [ ] Kibana dashboard prepared (optional)

## 🎬 Demo Script

### Part 1: Introduction & Setup (5 minutes)

**Slide 1: Problem Statement**
> "Infrastructure changes are one of the biggest causes of incidents. But how do we correlate infrastructure changes with application issues?"

**Slide 2: Architecture Overview**
> "Today I'll show you how we can:
> - Capture Terraform infrastructure changes
> - Index CI/CD pipeline metadata
> - Collect application telemetry via OpenTelemetry
> - Correlate everything in Elasticsearch using common fields"

**Live Demo:**
1. Show the repository structure
   ```bash
   tree -L 2 -I 'venv|__pycache__'
   ```

2. Show Docker Compose services running
   ```bash
   docker-compose ps
   ```

3. Open Jenkins UI (`http://localhost:8080`)
   - Show the pipeline job
   - Explain: "Terraform only runs via Jenkins - no manual runs"

### Part 2: Infrastructure Change (8 minutes)

**Narrative:**
> "Let's make an infrastructure change. We'll deploy a new version of our application using Terraform."

**Live Demo:**

1. **Show Terraform Code**
   ```bash
   cat terraform/main.tf | head -50
   ```
   - Highlight: Docker provider, correlation fields

2. **Run Jenkins Pipeline**
   - Click "Build Now" in Jenkins
   - Show console output
   - Point out: "Terraform plan is running"
   - Point out: "Logs are being sent to Elasticsearch"

3. **Show Raw Logs in Kibana**
   - Open Kibana → Discover
   - Select index: `infra-raw-events*`
   - Filter: `log.type: terraform_plan`
   - Show: Raw log content
   - Explain: "Raw logs go here first, no parsing in the pipeline"

4. **Show Parsed Logs**
   - Switch to `infra-changes*` (if using separate index)
   - Or show fields extracted by ingest pipeline
   - Highlight correlation fields:
     - `service.name: demo-app`
     - `ci.pipeline_id: <build-id>`
     - `infra.change_id: <build-id>-<build-number>`
     - `@timestamp`

5. **Terraform Apply Completes**
   - Show: "Container created"
   - Show: Application running at `http://localhost:5000`

**Key Points:**
- ✅ Infrastructure changes are captured
- ✅ CI/CD metadata is included
- ✅ Raw → Parsed via ingest pipelines
- ✅ Correlation fields are present

### Part 3: Application Telemetry (7 minutes)

**Narrative:**
> "Now let's see the application sending telemetry. The app is instrumented with OpenTelemetry and sends traces, metrics, and logs."

**Live Demo:**

1. **Show Application**
   - Open `http://localhost:5000`
   - Show the UI
   - Explain: "Simple Flask app with OpenTelemetry"

2. **Generate Normal Traffic**
   - Click "Simulate User Action" button 5-10 times
   - Or use curl:
     ```bash
     for i in {1..10}; do curl http://localhost:5000/action; sleep 0.5; done
     ```

3. **Show in Kibana APM**
   - Open Kibana → APM → Services
   - Select `demo-app`
   - Show:
     - **Traces:** Request traces with spans
     - **Metrics:** Request rate, latency
     - **Logs:** Application logs
   - Highlight correlation fields in traces:
     - `service.name: demo-app`
     - `service.version: <version>`
     - `deployment.environment: production`
     - `ci.build.id: <build-id>`

4. **Generate Errors**
   - Click "Simulate Error" button
   - Or: `curl http://localhost:5000/error`
   - Show error in APM:
     - Error rate spike
     - Error trace details
     - Exception stack trace

**Key Points:**
- ✅ Application telemetry is flowing
- ✅ Same correlation fields as infrastructure
- ✅ Errors are visible immediately

### Part 4: Correlation & Root Cause Analysis (8 minutes)

**Narrative:**
> "This is where it gets interesting. Let's correlate infrastructure changes with application issues."

**Live Demo:**

1. **Create Timeline Visualization**
   - Open Kibana → Discover
   - Search: `service.name: demo-app`
   - Time range: Last 15 minutes
   - Show:
     - Infrastructure change events (from `infra-changes*`)
     - Application traces (from APM)
     - Application errors (from APM)

2. **Tell the Story**
   > "At 14:28:00, Terraform applied a container restart.
   > At 14:30:00, we see application errors spike.
   > Let's correlate..."

3. **Correlation Query**
   ```kql
   service.name: demo-app AND 
   (@timestamp >= now()-15m) AND 
   (infra.change_id: * OR ci.pipeline_id: *)
   ```
   - Show unified timeline
   - Highlight: Infrastructure change → Application error

4. **Deep Dive into RCA**
   - Click on infrastructure change event
   - Show: Terraform plan details
   - Show: What changed (container restart)
   - Click on application error
   - Show: Error details, trace
   - **Conclusion:** "Container restart caused application instability"

5. **Show MTTR Improvement**
   > "Before: Hours to find root cause
   > After: Minutes - we can see exactly what changed and when"

**Key Points:**
- ✅ Unified timeline
- ✅ Clear correlation
- ✅ Obvious RCA story
- ✅ MTTR reduction

### Part 5: Q&A (2 minutes)

**Common Questions:**

**Q: What if I don't use Jenkins?**
> A: The same pattern works with GitHub Actions, GitLab CI, etc. The key is capturing CI/CD metadata and sending raw logs to Elasticsearch.

**Q: How do you handle large Terraform plans?**
> A: The ingest pipeline parses JSON efficiently. For very large plans, you might want to extract only resource changes.

**Q: What about security?**
> A: API keys are stored in Jenkins credentials. Terraform state is local. In production, use proper secrets management.

**Q: Can this work with cloud providers?**
> A: Absolutely! The same correlation strategy works. Just change the Terraform provider (AWS, GCP, Azure).

## 🎯 Key Messages to Emphasize

1. **Infrastructure changes are a major incident cause**
2. **Correlation is key** - use common fields across all data sources
3. **Raw → Parsed** - send raw logs, parse in Elasticsearch
4. **Unified observability** - one place to see everything
5. **MTTR reduction** - faster root cause analysis

## 🛠️ Troubleshooting During Demo

**If Jenkins pipeline fails:**
- Check Docker socket: `docker exec jenkins docker ps`
- Check Terraform: `docker exec jenkins terraform version`
- Show logs: `docker logs jenkins`

**If no data in Elasticsearch:**
- Verify credentials in Jenkins
- Check ingest pipeline: Show setup script output
- Verify connection: Show a test query

**If application not sending telemetry:**
- Check OpenTelemetry Collector: `docker logs otel-collector`
- Check app container: `docker logs <app-container>`
- Verify environment variables

## 📊 Demo Success Metrics

- ✅ Infrastructure change visible in Kibana
- ✅ Application telemetry visible in APM
- ✅ Correlation works (unified timeline)
- ✅ RCA story is clear
- ✅ Audience understands MTTR benefit

---

**Good luck with your demo! 🚀**

