#!/usr/bin/env bash

response=$(curl -X POST http://localhost:9200/_plugins/_ml/models/_register -H 'Content-Type: application/json' -d @3-deploy-ml-model.json)
echo "${response}"
task_id=$(jq ."task_id" <<< "${response}")
echo "Task id: ${task_id}"
curl -X POST "http://localhost:9200/_plugins/_ml/models/${task_id}/_deploy"

