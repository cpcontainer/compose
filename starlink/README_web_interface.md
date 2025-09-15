# Starlink Dish Web Interface

A modern web interface for monitoring and controlling your Starlink dish, built with Flask.

## Features

- **Real-time Status Monitoring**: View comprehensive dish status including connection state, performance metrics, and dish positioning
- **Dish Control**: Stow, unstow, and reboot your Starlink dish with simple button clicks
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Auto-refresh**: Status updates automatically every 30 seconds
- **Modern UI**: Clean, intuitive interface with real-time status indicators

## Installation

### Option 1: Local Installation

1. Ensure you have the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure your Starlink dish is accessible at `192.168.100.1:9200` (default)

### Option 2: Docker Installation

1. Build and run using Docker:
   ```bash
   ./run_docker.sh
   ```

   Or manually:
   ```bash
   docker build -t starlink-tools .
   docker run -p 8000:8000 starlink-tools
   ```

2. The web interface will be available at `http://localhost:8000`

## Usage

### Starting the Web Interface

#### Local Installation
```bash
python web_interface.py
```

#### Docker Installation
```bash
./run_docker.sh
```

The web interface will be available at `http://localhost:8000`

### Accessing from Other Devices

The web interface runs on port 8000 and is accessible from any device on your local network. Simply navigate to:
```
http://[YOUR_COMPUTER_IP]:8000
```

### Features

#### Status Monitoring
- **Connection Status**: Real-time connection state with visual indicators
- **Performance Metrics**: Download/upload speeds, latency, and packet loss
- **Dish Information**: Azimuth, elevation, obstruction data, and GPS satellite count
- **System Information**: Hardware/software versions and uptime

#### Dish Controls
- **Stow**: Safely stow the dish (useful for maintenance or storms)
- **Unstow**: Restore the dish to operational position
- **Reboot**: Restart the dish (use with caution)

## API Endpoints

The web interface also provides REST API endpoints:

- `GET /api/status` - Get current dish status
- `POST /api/command` - Execute dish commands (stow, unstow, reboot)
- `GET /api/refresh` - Manually refresh status

### Example API Usage

```bash
# Get status
curl http://localhost:8000/api/status

# Stow dish
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "stow"}'

# Unstow dish
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "unstow"}'

# Reboot dish
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "reboot"}'
```

## Docker Features

When running in Docker, the container automatically starts both:
- **Web Interface**: Available on port 8000
- **Status Monitoring**: Background process that continuously monitors dish status

The container includes:
- Automatic startup of both services
- Proper signal handling for graceful shutdown
- Non-root user for security
- Health monitoring and restart policies

## Security Notes

- The web interface is designed for local network use only
- No authentication is implemented - ensure your network is secure
- Dish control commands should be used carefully, especially reboot
- Consider using a reverse proxy with SSL for production use

## Troubleshooting

### Common Issues

1. **"Dish Unreachable" Error**
   - Ensure your computer is on the same network as the Starlink dish
   - Verify the dish is powered on and accessible at `192.168.100.1:9200`
   - Check firewall settings

2. **Command Execution Fails**
   - Ensure you have proper network connectivity to the dish
   - Some commands may take time to complete - wait before retrying
   - Check the dish's current state (e.g., can't unstow if already unstowed)

3. **Web Interface Won't Start**
   - Ensure Flask is installed: `pip install flask`
   - Check if port 8000 is already in use
   - Verify all dependencies are installed

4. **Docker Container Issues**
   - Ensure Docker is running: `docker --version`
   - Check container logs: `docker logs starlink-tools`
   - Verify port mapping: `docker ps`
   - Rebuild if needed: `docker-compose down && docker-compose up --build`

### Logs

The web interface will output status information to the console. Monitor these logs for troubleshooting:

```bash
python web_interface.py
```

## Integration

This web interface can be integrated with:
- Home automation systems
- Monitoring dashboards
- Network management tools
- Custom automation scripts

The API endpoints make it easy to integrate with other systems using standard HTTP requests.
