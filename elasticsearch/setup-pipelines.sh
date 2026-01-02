#!/bin/bash
# Setup Elasticsearch ingest pipelines for parsing infrastructure logs

set -e

ELASTIC_CLOUD_ENDPOINT="${ELASTIC_CLOUD_ENDPOINT:-}"
ELASTIC_API_KEY="${ELASTIC_API_KEY:-}"

if [ -z "$ELASTIC_CLOUD_ENDPOINT" ] || [ -z "$ELASTIC_API_KEY" ]; then
    echo "Error: ELASTIC_CLOUD_ENDPOINT and ELASTIC_API_KEY must be set"
    exit 1
fi

echo "Setting up Elasticsearch ingest pipelines..."

# Create the terraform-logs-parser pipeline
curl -X PUT "${ELASTIC_CLOUD_ENDPOINT}/_ingest/pipeline/terraform-logs-parser" \
  -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Parse Terraform command output logs from infra-raw-events",
    "processors": [
      {
        "grok": {
          "field": "log.raw",
          "patterns": [
            "%{TIMESTAMP_ISO8601:@timestamp} %{GREEDYDATA:message}",
            "Terraform will perform the following actions:%{GREEDYDATA:plan_summary}",
            "%{WORD:resource_action} %{DATA:resource_type}\\.%{DATA:resource_name}",
            "Plan: %{NUMBER:plan_add} to add, %{NUMBER:plan_change} to change, %{NUMBER:plan_destroy} to destroy"
          ],
          "pattern_definitions": {
            "TIMESTAMP_ISO8601": "%{YEAR}-%{MONTHNUM}-%{MONTHDAY}[T ]%{HOUR}:?%{MINUTE}(?::?%{SECOND})?%{ISO8601_TIMEZONE}?"
          }
        }
      },
      {
        "json": {
          "field": "log.raw",
          "target_field": "terraform.plan",
          "if": "ctx.log.type == '\''terraform_plan_json'\''"
        }
      },
      {
        "script": {
          "source": "if (ctx['log.type'] == '\''terraform_plan_json'\'' && ctx['terraform.plan'] != null) { def plan = ctx['terraform.plan']; if (plan.resource_changes != null) { ctx['terraform.resource_changes_count'] = plan.resource_changes.size(); def changes = []; for (def change : plan.resource_changes) { def changeInfo = ['address': change.address, 'type': change.type, 'actions': change.change?.actions ?: []]; changes.add(changeInfo); } ctx['terraform.resource_changes'] = changes; } if (plan.variables != null) { ctx['terraform.variables.app_version'] = plan.variables.app_version?.value; ctx['terraform.variables.build_id'] = plan.variables.build_id?.value; ctx['terraform.variables.environment'] = plan.variables.environment?.value; ctx['terraform.variables.service_name'] = plan.variables.service_name?.value; } }",
          "lang": "painless"
        }
      },
      {
        "set": {
          "field": "event.category",
          "value": "infrastructure"
        }
      },
      {
        "set": {
          "field": "event.type",
          "value": "{{log.type}}"
        }
      },
      {
        "set": {
          "field": "infra.change_id",
          "value": "{{ci.pipeline.id}}-{{ci.build.number}}"
        }
      },
      {
        "set": {
          "field": "service.name",
          "value": "{{terraform.variables.service_name}}",
          "if": "ctx['terraform.variables.service_name'] != null"
        }
      },
      {
        "set": {
          "field": "service.version",
          "value": "{{terraform.variables.app_version}}",
          "if": "ctx['terraform.variables.app_version'] != null"
        }
      },
      {
        "set": {
          "field": "environment",
          "value": "{{terraform.variables.environment}}",
          "if": "ctx['terraform.variables.environment'] != null"
        }
      },
      {
        "set": {
          "field": "region",
          "value": "local"
        }
      },
      {
        "rename": {
          "field": "ci.pipeline.id",
          "target_field": "ci.pipeline_id"
        }
      }
    ]
  }'

echo ""
echo "✓ Ingest pipeline 'terraform-logs-parser' created successfully"

# Create index template for infra-raw-events
echo ""
echo "Creating index template for infra-raw-events..."

curl -X PUT "${ELASTIC_CLOUD_ENDPOINT}/_index_template/infra-raw-events-template" \
  -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["infra-raw-events*"],
    "template": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "default_pipeline": "terraform-logs-parser"
      },
      "mappings": {
        "properties": {
          "@timestamp": { "type": "date" },
          "log.type": { "type": "keyword" },
          "log.raw": { "type": "text" },
          "log.source": { "type": "keyword" },
          "ci.pipeline.name": { "type": "keyword" },
          "ci.pipeline.id": { "type": "keyword" },
          "ci.pipeline_id": { "type": "keyword" },
          "ci.build.id": { "type": "keyword" },
          "ci.build.number": { "type": "keyword" },
          "ci.build.url": { "type": "keyword" },
          "vcs.revision": { "type": "keyword" },
          "vcs.branch": { "type": "keyword" },
          "infra.change_id": { "type": "keyword" },
          "service.name": { "type": "keyword" },
          "service.version": { "type": "keyword" },
          "environment": { "type": "keyword" },
          "region": { "type": "keyword" },
          "terraform.resource_changes": { "type": "object", "enabled": true },
          "terraform.variables": { "type": "object", "enabled": true },
          "event.category": { "type": "keyword" },
          "event.type": { "type": "keyword" }
        }
      }
    }
  }'

echo ""
echo "✓ Index template created successfully"

# Create index template for parsed infra-changes
echo ""
echo "Creating index template for infra-changes..."

curl -X PUT "${ELASTIC_CLOUD_ENDPOINT}/_index_template/infra-changes-template" \
  -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["infra-changes*"],
    "template": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
      },
      "mappings": {
        "properties": {
          "@timestamp": { "type": "date" },
          "infra.change_id": { "type": "keyword" },
          "ci.pipeline_id": { "type": "keyword" },
          "ci.build.id": { "type": "keyword" },
          "service.name": { "type": "keyword" },
          "service.version": { "type": "keyword" },
          "environment": { "type": "keyword" },
          "region": { "type": "keyword" },
          "terraform.resource_changes": { "type": "object", "enabled": true },
          "terraform.action": { "type": "keyword" },
          "event.category": { "type": "keyword" },
          "event.type": { "type": "keyword" }
        }
      }
    }
  }'

echo ""
echo "✓ Index template for infra-changes created successfully"
echo ""
echo "Setup complete! You can now ingest logs to infra-raw-events-* and they will be automatically parsed."

