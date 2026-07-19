#!/bin/bash

set -e

cd ~/braggingrights

echo "Pulling latest changes..."
git pull origin main

echo "Restarting service..."
sudo systemctl restart braggingrights

echo "Deployment complete!"