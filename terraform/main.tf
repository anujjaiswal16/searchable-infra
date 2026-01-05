terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

variable "app_version" {
  description = "Application version"
  type        = string
  default     = "v1.0.0"
}

variable "build_id" {
  description = "CI/CD Build ID"
  type        = string
  default     = "manual"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "service_name" {
  description = "Service name for correlation"
  type        = string
  default     = "demo-app"
}

# Use existing Docker network (created by docker-compose)
# Try to use the demo-network, fallback to creating a new one
data "docker_network" "demo_network" {
  name = "demo-network"
}

locals {
  network_name = data.docker_network.demo_network.name
}

# Pull the application image
resource "docker_image" "app_image" {
  name = "demo-app:${var.app_version}"
  
  build {
    context    = "../app"
    dockerfile = "Dockerfile"
    tag        = ["demo-app:${var.app_version}", "demo-app:latest"]
  }
  
  triggers = {
    app_version = var.app_version
  }
}

# Create the application container
resource "docker_container" "app" {
  image = docker_image.app_image.image_id
  name  = "demo-app-${var.build_id}"
  
  networks_advanced {
    name = local.network_name
  }
  
  env = [
    "OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318",
    "OTEL_SERVICE_NAME=${var.service_name}",
    "OTEL_SERVICE_VERSION=${var.app_version}",
    "OTEL_RESOURCE_ATTRIBUTES=deployment.environment=${var.environment},ci.build.id=${var.build_id},service.name=${var.service_name}",
    "FLASK_ENV=production",
    "APP_VERSION=${var.app_version}",
    "BUILD_ID=${var.build_id}",
    "ENVIRONMENT=${var.environment}"
  ]
  
  ports {
    internal = 5000
    external = 5000
  }
  
  restart = "unless-stopped"
  
  # Labels for Docker container metadata (optional - correlation is via env vars)
  # In Docker provider v3.x, use map syntax without quotes on keys
  labels = {
    "service.name"             = var.service_name
    "service.version"          = var.app_version
    "ci.build.id"              = var.build_id
    "deployment.environment"   = var.environment
    "managed_by"               = "terraform"
  }
}

# Outputs for correlation
output "app_container_id" {
  value       = docker_container.app.id
  description = "Application container ID"
}

output "app_container_name" {
  value       = docker_container.app.name
  description = "Application container name"
}

output "network_id" {
  value       = data.docker_network.demo_network.id
  description = "Docker network ID"
}

output "change_summary" {
  value = {
    action          = "apply"
    service_name    = var.service_name
    app_version     = var.app_version
    build_id        = var.build_id
    environment     = var.environment
    container_name  = docker_container.app.name
    network_name    = local.network_name
  }
  description = "Summary of infrastructure changes"
}
