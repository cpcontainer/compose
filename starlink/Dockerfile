FROM python:3.9-slim
LABEL maintainer="neurocis <neurocis@neurocis.me>"

# Create non-root user for security
RUN groupadd -r starlink && useradd -r -g starlink starlink

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Expose port for web interface
EXPOSE 8000

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies using requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY dish_*.py loop_util.py starlink_*.py entrypoint.sh ./
COPY cp.py cp_dish_status.py ./
COPY web_interface.py ./
COPY templates/ ./templates/
COPY docker_entrypoint.sh ./

# Change ownership to non-root user
RUN chown -R starlink:starlink /app

# Switch to non-root user
USER starlink

# Use entrypoint script to start both web interface and status monitoring
ENTRYPOINT ["./docker_entrypoint.sh"]
