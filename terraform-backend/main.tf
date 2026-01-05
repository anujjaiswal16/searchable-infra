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

variable "app_version" { default = "v1.0.0" }
variable "build_id" { default = "manual" }
variable "environment" { default = "production" }
variable "service_name" { default = "backend-service" }
variable "simulated_latency" { default = 0 }
variable "simulated_error_rate" { default = 0 }

data "docker_network" "demo_network" {
  name = "demo-network"
}

resource "docker_image" "backend_image" {
  name = "backend-service:${var.app_version}"
  build {
    context    = "../backend"
    dockerfile = "Dockerfile"
    tag        = ["backend-service:${var.app_version}", "backend-service:latest"]
  }
  triggers = {
    app_version = var.app_version
    dockerfile_hash = filemd5("../backend/Dockerfile")
  }
}

resource "docker_container" "backend" {
  image = docker_image.backend_image.image_id
  name  = "backend-service"
  
  networks_advanced {
    name = data.docker_network.demo_network.name
  }
  
  env = [
    "OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318",
    "OTEL_SERVICE_NAME=${var.service_name}",
    "APP_VERSION=${var.app_version}",
    "ENVIRONMENT=${var.environment}",
    "SIMULATED_LATENCY=${var.simulated_latency}",
    "SIMULATED_ERROR_RATE=${var.simulated_error_rate}"
  ]
  
  ports {
    internal = 5000
    external = 5001 # Use 5001 for backend
  }
  
  restart = "unless-stopped"
}

output "change_summary" {
  value = {
    action = "apply"
    service = var.service_name
    version = var.app_version
    latency = var.simulated_latency
    error_rate = var.simulated_error_rate
  }
}
