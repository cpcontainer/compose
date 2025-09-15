#!/bin/bash

# Docker entrypoint script for Starlink tools
# Starts both the web interface and status monitoring

echo "Starting Starlink tools..."

# Start the web interface in the background
echo "Starting web interface on port 8000..."
python3 web_interface.py &
WEB_PID=$!

# Wait a moment for web interface to start
sleep 2

# Start the status monitoring script
echo "Starting status monitoring..."
python3 cp_dish_status.py &
STATUS_PID=$!

# Function to handle shutdown
cleanup() {
    echo "Shutting down..."
    kill $WEB_PID $STATUS_PID 2>/dev/null
    wait $WEB_PID $STATUS_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for background processes
wait $WEB_PID $STATUS_PID
