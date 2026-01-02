.PHONY: help setup start stop clean logs test

help:
	@echo "Available commands:"
	@echo "  make setup    - Setup Elasticsearch ingest pipelines"
	@echo "  make start    - Start Docker Compose services"
	@echo "  make stop     - Stop Docker Compose services"
	@echo "  make clean    - Stop and remove all containers/volumes"
	@echo "  make logs     - View logs from all services"
	@echo "  make test     - Run test queries against the application"

setup:
	@echo "Setting up Elasticsearch ingest pipelines..."
	@if [ -z "$$ELASTIC_CLOUD_ENDPOINT" ] || [ -z "$$ELASTIC_API_KEY" ]; then \
		echo "Error: ELASTIC_CLOUD_ENDPOINT and ELASTIC_API_KEY must be set"; \
		exit 1; \
	fi
	@./elasticsearch/setup-pipelines.sh

start:
	@echo "Starting Docker Compose services..."
	@docker-compose up -d
	@echo "Jenkins: http://localhost:8080"
	@echo "Application: http://localhost:5000 (after Terraform apply)"
	@echo ""
	@echo "Get Jenkins initial admin password:"
	@echo "  docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"

stop:
	@echo "Stopping Docker Compose services..."
	@docker-compose stop

clean:
	@echo "Cleaning up containers and volumes..."
	@docker-compose down -v
	@echo "Removing Terraform-managed containers..."
	@docker ps -a --filter "label=managed_by=terraform" -q | xargs -r docker rm -f || true

logs:
	@docker-compose logs -f

test:
	@echo "Testing application endpoints..."
	@echo "Health check:"
	@curl -s http://localhost:5000/health | jq . || echo "App not running"
	@echo ""
	@echo "Triggering action:"
	@curl -s http://localhost:5000/action | jq . || echo "App not running"
	@echo ""
	@echo "Triggering error:"
	@curl -s http://localhost:5000/error || echo "App not running"

