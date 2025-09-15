#!/bin/bash

# Script to build and run Starlink tools Docker container

echo "Building Starlink tools Docker image..."
docker build -t starlink-tools .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Starting container..."
    echo "Web interface will be available at http://localhost:8000"
    echo "Press Ctrl+C to stop"
    
    # Run with docker-compose for easier management
    docker-compose up
else
    echo "Build failed!"
    exit 1
fi
