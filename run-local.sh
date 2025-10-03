#!/bin/bash

# Build and run the Docker container locally
echo "🐳 Building Docker image..."
docker build -t autofill-api .

echo "🚀 Starting container..."
docker run -p 8000:8000 \
  -v $(pwd)/templates:/app/templates \
  -v $(pwd)/outputs:/app/outputs \
  -e CORS_ORIGINS="*" \
  autofill-api
