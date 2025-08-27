# 🐳 Docker Deployment Guide

This guide helps you run the Tools Dashboard using Docker for easy deployment and consistent environments.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

### One-Command Startup
```bash
docker-compose up
```

That's it! The application will be available at `http://localhost:5002`

## 📋 Available Commands

### Start the Application
```bash
# Start with Docker Compose (recommended)
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# Build and start (for first time or after changes)
docker-compose up --build

# Use the convenience script
./docker-start.sh
```

### Stop the Application
```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove everything (containers, networks, images)
docker-compose down --rmi all -v
```

### View Logs
```bash
# View real-time logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f tools-dashboard
```

### Development Commands
```bash
# Rebuild image
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Access container shell
docker-compose exec tools-dashboard /bin/bash
```

## 🏗️ Docker Configuration

### Dockerfile Features
- **Base Image**: Python 3.13 slim for optimal size
- **Security**: Non-root user for container execution
- **Health Checks**: Built-in health monitoring
- **Optimized Build**: Multi-stage approach for smaller images
- **Dependencies**: UV package manager for fast installs

### Docker Compose Features
- **Port Mapping**: Container port 5002 → Host port 5002
- **Health Checks**: Automatic container health monitoring
- **Restart Policy**: Automatically restart on failure
- **Networks**: Isolated network for security
- **Volumes**: Persistent storage for temporary files

## 🔧 Configuration

### Environment Variables
The following environment variables can be customized:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment mode |
| `FLASK_APP` | `main.py` | Flask application entry point |
| `PORT` | `5002` | Application port |
| `PYTHONPATH` | `/app` | Python module search path |

### Custom Port
To run on a different port, modify `docker-compose.yml`:
```yaml
ports:
  - "8080:5002"  # Run on port 8080
```

### Development Mode
For development with live code reloading:
```yaml
environment:
  - FLASK_ENV=development
volumes:
  - .:/app  # Mount current directory
```

## 📊 Monitoring

### Health Checks
The container includes health checks that verify the application is running:
- **Endpoint**: `http://localhost:5002/`
- **Interval**: Every 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts

### Container Status
```bash
# Check container status
docker-compose ps

# View container resource usage
docker stats

# Check health status
docker inspect tools-dashboard | grep Health -A 10
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port 5002
lsof -i :5002

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

**Permission Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Rebuild container
docker-compose build --no-cache
```

**Image Build Fails**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

**Container Won't Start**
```bash
# Check logs
docker-compose logs tools-dashboard

# Check container status
docker-compose ps

# Remove and recreate
docker-compose down
docker-compose up --build
```

### Debugging
```bash
# Access running container
docker-compose exec tools-dashboard /bin/bash

# Check Python packages
docker-compose exec tools-dashboard .venv/bin/pip list

# Test application manually
docker-compose exec tools-dashboard .venv/bin/python -c "import main; print('OK')"
```

## 🔒 Security

### Container Security
- **Non-root user**: Application runs as `app` user
- **Minimal base image**: Python slim reduces attack surface
- **No unnecessary packages**: Only required dependencies installed
- **Health monitoring**: Automatic failure detection

### Network Security
- **Isolated network**: Container runs in dedicated network
- **Port exposure**: Only necessary port (5002) exposed
- **No privileged access**: Container runs without elevated permissions

## 🚀 Production Deployment

### Production Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  tools-dashboard:
    build: .
    restart: always
    environment:
      - FLASK_ENV=production
    ports:
      - "80:5002"
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

### Scaling
```bash
# Run multiple instances
docker-compose up --scale tools-dashboard=3

# Use with load balancer (nginx, traefik, etc.)
```

## 📈 Performance

### Resource Usage
- **Memory**: ~150MB per container
- **CPU**: Minimal usage for typical workloads
- **Disk**: ~200MB for image

### Optimization Tips
1. **Use Docker BuildKit** for faster builds
2. **Multi-stage builds** for smaller images
3. **Layer caching** for faster rebuilds
4. **Resource limits** to prevent resource exhaustion

## 🔄 Updates

### Updating the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up --build

# Zero-downtime update (advanced)
docker-compose up --scale tools-dashboard=2
docker-compose up --scale tools-dashboard=1
```

---

**🐳 Happy Dockerizing!** Your Tools Dashboard is now containerized and ready for any environment.
