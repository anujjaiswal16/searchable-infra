
import json
import os
import datetime
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
ELASTIC_CLOUD_ENDPOINT = os.getenv("ELASTIC_CLOUD_ENDPOINT")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

if not ELASTIC_CLOUD_ENDPOINT or not ELASTIC_API_KEY:
    print("Error: ELASTIC_CLOUD_ENDPOINT and ELASTIC_API_KEY must be set.")
    exit(1)

es = Elasticsearch(
    ELASTIC_CLOUD_ENDPOINT,
    api_key=ELASTIC_API_KEY
)

# Index name
INDEX_NAME = "terraform-plans"

def ingest_plan(plan_file):
    if not os.path.exists(plan_file):
        print(f"File {plan_file} not found.")
        return

    # Extract variables from Terraform Plan
    variables = plan_data.get("variables", {})
    build_id = variables.get("build_id", {}).get("value", "unknown")
    app_version = variables.get("app_version", {}).get("value", "unknown")

    # Extract Metadata from CI/CD Environment (Jenkins)
    ci_metadata = {
        "ci.job.name": os.getenv("JOB_NAME", "unknown-job"),
        "ci.build.url": os.getenv("BUILD_URL", "unknown-url"),
        "vcs.revision": os.getenv("GIT_COMMIT", "unknown-commit"),
        "ci.runner.name": "jenkins-local"
    }

    # Extract resource changes
    resource_changes = plan_data.get("resource_changes", [])
    
    timestamp = datetime.datetime.utcnow().isoformat()

    for change in resource_changes:
        doc = {
            "@timestamp": timestamp,
            "ci.build.id": build_id,
            "service.version": app_version,
            **ci_metadata, # Unpack CI metadata
            "terraform.resource.address": change.get("address"),
            "terraform.resource.type": change.get("type"),
            "terraform.resource.name": change.get("name"),
            "terraform.change.actions": change.get("change", {}).get("actions"),
            "terraform.change.reason": change.get("change", {}).get("before_sensitive", False), 
            "terraform_plan_json": json.dumps(change) 
        }
        
        # Index document
        resp = es.index(index=INDEX_NAME, document=doc)
        print(f"Indexed change for {change.get('address')}: {resp['result']}")

if __name__ == "__main__":
    ingest_plan("tfplan.json")
