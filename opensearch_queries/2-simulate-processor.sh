#!/usr/bin/env bash

curl -X POST http://localhost:9200/_ingest/pipeline/cie10-processor/_simulate -H 'Content-Type: application/json' -d @2-simulate-processor.json
