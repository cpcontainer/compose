#!/usr/bin/env python3
"""
Starlink Dish Web Interface
Provides a web interface to view dish status and control dish operations.
"""

import json
import time
import threading
from datetime import datetime, timezone
from collections import deque
from flask import Flask, render_template, jsonify, request, redirect, url_for
import starlink_grpc
import dish_control
import grpc
from yagrc import reflector as yagrc_reflector

app = Flask(__name__)

# Global variables to store status and control functions
dish_status = {}
status_lock = threading.Lock()
last_update = None

# Historical data storage (24 hours of data, 1 sample per minute = 1440 samples)
MAX_HISTORY_SAMPLES = 1440
historical_data = deque(maxlen=MAX_HISTORY_SAMPLES)
history_lock = threading.Lock()

def get_dish_status():
    """Get current dish status from starlink_grpc"""
    global dish_status, last_update
    
    try:
        # Get parsed status data as dictionary
        status_dict, obstruction_dict, alert_dict = starlink_grpc.status_data()
        
        # Merge all dictionaries
        status_dict.update(obstruction_dict)
        status_dict.update(alert_dict)
        
        # Add timestamp
        status_dict['_updated_at'] = datetime.now(timezone.utc).isoformat() + 'Z'
        

        
        # Store historical data
        with history_lock:
            historical_data.append({
                'timestamp': int(time.time()),
                'download_mbps': status_dict.get('downlink_throughput_bps', 0) / 1000000,
                'upload_mbps': status_dict.get('uplink_throughput_bps', 0) / 1000000,
                'latency_ms': status_dict.get('pop_ping_latency_ms'),
                'packet_loss_percent': status_dict.get('pop_ping_drop_rate', 0) * 100,
                'state': status_dict.get('state'),
                'azimuth': status_dict.get('direction_azimuth'),
                'elevation': status_dict.get('direction_elevation'),
                'obstruction_percent': status_dict.get('fraction_obstructed', 0) * 100,
                'gps_satellites': status_dict.get('gps_sats')
            })
        
        with status_lock:
            dish_status = status_dict
            last_update = datetime.now(timezone.utc)
            
    except Exception as e:
        with status_lock:
            dish_status = {
                'error': str(e),
                'state': 'ERROR',
                '_updated_at': datetime.now(timezone.utc).isoformat() + 'Z'
            }
            last_update = datetime.now(timezone.utc)



def execute_dish_command(command):
    """Execute a dish control command using dish_control.py functions"""
    try:
        # Create a mock options object for dish_control
        class MockOptions:
            def __init__(self, command, target="192.168.100.1:9200"):
                self.command = command
                self.target = target
        
        opts = MockOptions(command)
        
        # Execute the command
        reflector = yagrc_reflector.GrpcReflectionClient()
        with grpc.insecure_channel(opts.target) as channel:
            reflector.load_protocols(channel, symbols=["SpaceX.API.Device.Device"])
            stub = reflector.service_stub_class("SpaceX.API.Device.Device")(channel)
            request_class = reflector.message_class("SpaceX.API.Device.Request")
            
            if command == "reboot":
                request = request_class(reboot={})
            elif command == "stow":
                request = request_class(dish_stow={})
            elif command == "unstow":
                request = request_class(dish_stow={"unstow": True})
            else:
                return False, f"Unknown command: {command}"
            
            response = stub.Handle(request, timeout=10)
            return True, f"Command {command} executed successfully"
            
    except Exception as e:
        return False, f"Error executing {command}: {str(e)}"

def status_updater():
    """Background thread to update status every 30 seconds"""
    while True:
        get_dish_status()
        time.sleep(30)

@app.route('/')
def index():
    """Main page showing dish status and controls"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint to get current status"""
    with status_lock:
        return jsonify(dish_status)

@app.route('/api/command', methods=['POST'])
def api_command():
    """API endpoint to execute dish commands"""
    data = request.get_json()
    command = data.get('command')
    
    if command not in ['stow', 'unstow', 'reboot']:
        return jsonify({'success': False, 'message': 'Invalid command'}), 400
    
    success, message = execute_dish_command(command)
    return jsonify({'success': success, 'message': message})

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to manually refresh status"""
    get_dish_status()
    with status_lock:
        return jsonify(dish_status)

@app.route('/api/history')
def api_history():
    """API endpoint to get historical data for charts"""
    hours = request.args.get('hours', 24, type=int)
    cutoff_time = int(time.time()) - (hours * 3600)
    
    with history_lock:
        # Filter data for the requested time period
        filtered_data = [
            data for data in historical_data 
            if data['timestamp'] >= cutoff_time
        ]
    
    return jsonify({
        'data': filtered_data,
        'hours': hours,
        'count': len(filtered_data)
    })

@app.route('/api/charts')
def api_charts():
    """API endpoint to get formatted data for charts"""
    hours = request.args.get('hours', 24, type=int)
    cutoff_time = int(time.time()) - (hours * 3600)
    
    with history_lock:
        # Filter data for the requested time period
        filtered_data = [
            data for data in historical_data 
            if data['timestamp'] >= cutoff_time
        ]
    
    # Format data for Chart.js
    labels = []
    download_data = []
    upload_data = []
    latency_data = []
    packet_loss_data = []
    
    for data in filtered_data:
        # Convert timestamp to readable time
        dt = datetime.fromtimestamp(data['timestamp'], tz=timezone.utc)
        labels.append(dt.strftime('%H:%M'))
        
        download_data.append(round(data['download_mbps'], 2))
        upload_data.append(round(data['upload_mbps'], 2))
        latency_data.append(round(data['latency_ms'], 1) if data['latency_ms'] else None)
        packet_loss_data.append(round(data['packet_loss_percent'], 2))
    
    return jsonify({
        'labels': labels,
        'datasets': {
            'download': download_data,
            'upload': upload_data,
            'latency': latency_data,
            'packet_loss': packet_loss_data
        },
        'hours': hours,
        'count': len(filtered_data)
    })

@app.route('/api/add_sample_data')
def api_add_sample_data():
    """API endpoint to add sample data for testing charts"""
    import random
    
    # Generate 24 hours of sample data (one sample per hour)
    current_time = int(time.time()) - (24 * 3600)  # Start 24 hours ago
    
    with history_lock:
        for i in range(24):
            # Simulate realistic Starlink data
            download_speed = random.uniform(50, 200)  # 50-200 Mbps
            upload_speed = random.uniform(10, 50)     # 10-50 Mbps
            latency = random.uniform(20, 50)          # 20-50 ms
            packet_loss = random.uniform(0, 2)        # 0-2%
            
            historical_data.append({
                'timestamp': current_time + (i * 3600),
                'download_mbps': download_speed,
                'upload_mbps': upload_speed,
                'latency_ms': latency,
                'packet_loss_percent': packet_loss,
                'state': 'CONNECTED',
                'azimuth': random.uniform(180, 220),
                'elevation': random.uniform(45, 65),
                'obstruction_percent': random.uniform(0, 5),
                'gps_satellites': random.randint(8, 12)
            })
    
    return jsonify({
        'success': True,
        'message': f'Added {24} sample data points',
        'data_count': len(historical_data)
    })

if __name__ == '__main__':
    # Start background status updater
    status_thread = threading.Thread(target=status_updater, daemon=True)
    status_thread.start()
    
    # Get initial status
    get_dish_status()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=False)
