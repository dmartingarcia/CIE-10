#!/usr/bin/env bash

curl -X PUT http://localhost:9200/_ingest/pipeline/cie10-processor -H 'Content-Type: application/json' -d @1-create-pipeline.json
