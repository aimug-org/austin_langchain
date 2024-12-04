#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the pipelines directory relative to the script
PIPELINES_DIR="$SCRIPT_DIR/pipelines"

# Create the pipelines directory if it doesn't exist
if [ ! -d "$PIPELINES_DIR" ]; then
    echo "📂 Creating pipelines directory: $PIPELINES_DIR"
    mkdir -p "$PIPELINES_DIR"
fi

# Stop and remove existing pipelines container if it exists
docker rm -f pipelines >/dev/null 2>&1 || true

# Generate pipeline URLs using filenames and the mount point inside the container
PIPELINES_URLS=$(find "$PIPELINES_DIR" -maxdepth 1 -type f -name "*.py" -not -path "*/\.*" \
    -exec basename {} \; \
    | sed 's|^|file:///app/pipelines/|' \
    | tr '\n' ',' | sed 's/,$//')

# Log the PIPELINES_DIR and PIPELINES_URLS
echo "📂 PIPELINES_DIR: $PIPELINES_DIR"
echo "🔗 PIPELINES_URLS: $PIPELINES_URLS"

# Run the pipelines container
docker run -d \
  -p 9099:9099 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PIPELINES_DIR:/app/pipelines" \
  -v "$SCRIPT_DIR/requirements.txt:/app/requirements.txt" \
  --name pipelines \
  --restart always \
  -e PIPELINES_DIR=/app/pipelines \
  -e PIPELINES_REQUIREMENTS_PATH=/app/requirements.txt \
  -e PIPELINES_URLS="$PIPELINE_URLS" \
  ghcr.io/open-webui/pipelines:main

# Check if the container is running and healthy
echo -n "🔎 Checking container status..."
sleep 2  # Wait a moment for the container to initialize

if [ "$(docker inspect -f '{{.State.Running}}' pipelines 2>/dev/null)" = "true" ]; then
    echo " ✅ Container 'pipelines' is up and running!"
else
    echo " ❌ Container 'pipelines' is not running. Check logs for details."
    # Uncomment the following line to see the logs
    docker logs pipelines
fi
