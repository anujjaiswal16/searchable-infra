#!/bin/bash
# Force Terraform to rebuild the Docker image by clearing caches

echo "Clearing Terraform state and Docker image cache..."

# Remove any existing Docker images
docker rmi demo-app:latest 2>/dev/null || true
docker rmi demo-app:v* 2>/dev/null || true

# Remove Terraform's .terraform directory to force re-init
# (Don't remove .terraform.lock.hcl as it's needed)

echo "Done. Now run: terraform init && terraform plan"

