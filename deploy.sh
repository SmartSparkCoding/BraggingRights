#!/bin/bash

set -e

cd /root/braggingrights

echo "Pulling latest changes..."

git pull origin main

COMMIT=$(git rev-parse --short HEAD)
MESSAGE=$(git log -1 --pretty=%B | tr '\n' ' ')
TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Recording deployment..."

python3 <<EOF
import json

file = "/root/braggingrights/deployments.json"

with open(file, "r") as f:
    deployments = json.load(f)

deployments.insert(0, {
    "commit": "$COMMIT",
    "message": "$MESSAGE",
    "time": "$TIME"
})

deployments = deployments[:20]

with open(file, "w") as f:
    json.dump(deployments, f, indent=2)
EOF

echo "Restarting service..."

systemctl restart braggingrights

echo "Deployment complete!"