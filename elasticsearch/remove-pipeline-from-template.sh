#!/bin/bash
# Remove default pipeline from existing index template
# This is needed if you previously ran setup-pipelines.sh

set -e

ELASTIC_CLOUD_ENDPOINT="${ELASTIC_CLOUD_ENDPOINT:-}"
ELASTIC_API_KEY="${ELASTIC_API_KEY:-}"

if [ -z "$ELASTIC_CLOUD_ENDPOINT" ] || [ -z "$ELASTIC_API_KEY" ]; then
    echo "Error: ELASTIC_CLOUD_ENDPOINT and ELASTIC_API_KEY must be set"
    exit 1
fi

echo "Updating index template to remove default pipeline..."

curl -X PUT "${ELASTIC_CLOUD_ENDPOINT}/_index_template/infra-raw-events-template" \
  -H "Authorization: ApiKey ${ELASTIC_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["infra-raw-events*"],
    "template": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
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
echo "✓ Index template updated (default pipeline removed)"


