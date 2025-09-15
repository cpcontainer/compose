#!/bin/bash

# Starlink Web Interface Startup Script

echo "Starting Starlink Dish Web Interface..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the web interface
echo "Starting web interface on http://localhost:8000"
echo "Press Ctrl+C to stop"
python web_interface.py
