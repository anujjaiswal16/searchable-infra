#!/usr/bin/env python3
"""
Send raw Terraform logs and CI/CD metadata to Elasticsearch.
This script sends unparsed logs to the infra-raw-events-* index.
Parsing will be done by Elasticsearch ingest pipelines.
"""

import json
import os
import sys
import datetime
from elasticsearch import Elasticsearch

# Get Elasticsearch connection details
ELASTIC_CLOUD_ENDPOINT = os.getenv("ELASTIC_CLOUD_ENDPOINT")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

if not ELASTIC_CLOUD_ENDPOINT or not ELASTIC_API_KEY:
    print("Error: ELASTIC_CLOUD_ENDPOINT and ELASTIC_API_KEY must be set.", file=sys.stderr)
    sys.exit(1)

es = Elasticsearch(
    ELASTIC_CLOUD_ENDPOINT,
    api_key=ELASTIC_API_KEY,
    request_timeout=30
)

# Index name for raw events
INDEX_NAME = "infra-raw-events"

def send_raw_log(log_content, log_type, metadata=None):
    """
    Send raw log content to Elasticsearch.
    
    Args:
        log_content: The raw log text
        log_type: Type of log (terraform_plan, terraform_apply, terraform_init, etc.)
        metadata: Additional metadata dictionary
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Get CI/CD metadata from environment
    ci_metadata = {
        "ci.pipeline.name": os.getenv("JOB_NAME", "unknown"),
        "ci.pipeline.id": os.getenv("BUILD_ID", "unknown"),
        "ci.build.url": os.getenv("BUILD_URL", ""),
        "ci.build.number": os.getenv("BUILD_NUMBER", "unknown"),
        "vcs.revision": os.getenv("GIT_COMMIT", os.getenv("GIT_COMMIT_SHORT", "unknown")),
        "vcs.branch": os.getenv("GIT_BRANCH", "unknown"),
        "ci.runner.name": "jenkins-local",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }
    
    # Merge with provided metadata
    if metadata:
        ci_metadata.update(metadata)
    
    # Create document
    doc = {
        "@timestamp": timestamp,
        "log.type": log_type,
        "log.raw": log_content,
        "log.source": "jenkins-pipeline",
        **ci_metadata
    }
    
    try:
        # Use alternative index name to avoid default pipeline from index template
        # The index template pattern "infra-raw-events*" matches "infra-raw-events"
        # but we'll use "infra-raw-events-raw" which also matches but allows us to work around pipeline issues
        alt_index = f"{INDEX_NAME}-raw"
        
        # Try alternative index first (avoids any default pipeline issues)
        try:
            resp = es.index(index=alt_index, document=doc)
            print(f"✓ Indexed {log_type} log to {alt_index} (raw data, no pipeline): {resp['result']} (ID: {resp['_id']})")
            return resp
        except Exception as e_alt:
            # If alt index fails, try main index
            # The index template might have default_pipeline set, which causes errors
            # In that case, update the template: ./elasticsearch/remove-pipeline-from-template.sh
            try:
                resp = es.index(index=INDEX_NAME, document=doc)
                print(f"✓ Indexed {log_type} log (raw data): {resp['result']} (ID: {resp['_id']})")
                return resp
            except Exception as e_main:
                error_msg = str(e_main)
                if "pipeline" in error_msg.lower() and "does not exist" in error_msg.lower():
                    print(f"⚠ Index template has default pipeline that doesn't exist.", file=sys.stderr)
                    print(f"  Run: ./elasticsearch/remove-pipeline-from-template.sh", file=sys.stderr)
                    print(f"  Or: ./elasticsearch/setup-index-template.sh (creates template without pipeline)", file=sys.stderr)
                print(f"✗ Error indexing {log_type} log: {e_main}", file=sys.stderr)
                # Don't raise - allow pipeline to continue
                return None
    except Exception as e:
        print(f"✗ Error indexing {log_type} log: {e}", file=sys.stderr)
        # Don't raise - allow pipeline to continue
        return None

def send_terraform_plan_json(plan_json_path, metadata=None):
    """Send Terraform plan JSON to Elasticsearch as raw data."""
    if not os.path.exists(plan_json_path):
        print(f"Warning: Plan file {plan_json_path} not found.", file=sys.stderr)
        return
    
    with open(plan_json_path, 'r') as f:
        plan_data = json.load(f)
    
    # Send the entire plan as raw JSON string
    send_raw_log(
        log_content=json.dumps(plan_data, indent=2),
        log_type="terraform_plan_json",
        metadata=metadata
    )

def send_terraform_output(output_text, command_type, metadata=None):
    """Send Terraform command output to Elasticsearch."""
    send_raw_log(
        log_content=output_text,
        log_type=f"terraform_{command_type}",
        metadata=metadata
    )

if __name__ == "__main__":
    # This script can be called with arguments or used as a module
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "plan-json" and len(sys.argv) > 2:
            send_terraform_plan_json(sys.argv[2])
        elif command == "output" and len(sys.argv) > 3:
            log_type = sys.argv[2]
            # Read from stdin or file
            if len(sys.argv) > 4:
                with open(sys.argv[4], 'r') as f:
                    content = f.read()
            else:
                content = sys.stdin.read()
            send_terraform_output(content, log_type)
        else:
            print("Usage:")
            print("  python3 send_raw_logs.py plan-json <plan.json>")
            print("  python3 send_raw_logs.py output <type> [<file>]")
            sys.exit(1)

