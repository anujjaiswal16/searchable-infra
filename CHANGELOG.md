# Changelog

## [1.0.0] - 2024-01-XX

### Added
- Complete Terraform configuration using Docker provider
- Jenkins pipeline for running Terraform and capturing logs
- Python script for sending raw logs to Elasticsearch
- Elasticsearch ingest pipeline setup script
- OpenTelemetry Collector configuration
- Sample Flask application with OpenTelemetry instrumentation
- Docker Compose orchestration
- Comprehensive documentation (README, QUICKSTART, DEMO_GUIDE)

### Features
- Infrastructure changes captured from Terraform
- CI/CD metadata included in all events
- Application telemetry (traces, metrics, logs) via OpenTelemetry
- Correlation using common fields across all data sources
- Raw logs → Parsed via Elasticsearch ingest pipelines
- Unified timeline in Kibana for RCA

### Components
- **Terraform:** Docker provider, creates containers and networks
- **Jenkins:** Runs Terraform, captures logs, sends to Elasticsearch
- **OpenTelemetry Collector:** Receives and forwards telemetry
- **Application:** Flask app with full OpenTelemetry instrumentation
- **Elasticsearch:** Ingest pipelines for parsing and enrichment

### Documentation
- README.md: Complete setup and usage guide
- QUICKSTART.md: 5-minute quick start
- DEMO_GUIDE.md: Step-by-step presentation script
- SUMMARY.md: Solution overview

