#!/bin/bash

echo "🐳 Starting Tools Dashboard with Docker..."
echo ""
echo "📦 Building Docker image (first time may take a few minutes)..."

# Build and start the container
docker-compose up --build

echo ""
echo "🛑 Container stopped. Run 'docker-compose up' to start again."
