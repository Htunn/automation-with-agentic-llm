# Production Deployment Guide

This document provides detailed instructions for deploying the Ansible-TinyLlama Integration in a production environment.

## Table of Contents

- [System Requirements](#system-requirements)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Hardware Requirements

- **CPU**: 4+ cores (x86_64 architecture)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Disk**: 10GB for application, plus 2-10GB for model files

### Recommended Hardware Requirements

- **CPU**: 8+ cores
- **RAM**: 16GB+ (32GB for running multiple models)
- **Disk**: SSD with 20GB+ free space
- **GPU**: CUDA-compatible GPU with 4GB+ VRAM (optional but recommended)

### Software Requirements

- **OS**: Ubuntu 22.04 LTS or Rocky Linux 9+ (recommended)
- **Docker**: 20.10+ and Docker Compose 2.0+ (for containerized deployment)
- **Kubernetes**: 1.24+ (for Kubernetes deployment)
- **Python**: 3.12+ (for bare-metal deployment)

## Deployment Options

Choose the deployment option that best fits your environment:

1. **Docker Deployment**: Recommended for most environments
2. **Kubernetes Deployment**: For large-scale or managed cloud environments
3. **Bare-metal Deployment**: For specialized environments or edge computing

## Docker Deployment

### Prerequisites

- Docker and Docker Compose installed
- Git installed
- Access to Docker Hub or a private container registry

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/ansible-llm.git
   cd ansible-llm
   ```

2. **Configure Environment**

   Create a `.env` file with your configuration:

   ```bash
   cp .env.example .env
   nano .env
   ```

   Configure the following important settings:

   ```
   MODEL_NAME=TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T
   QUANTIZATION=4bit
   API_REQUIRE_AUTH=true
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   LOG_LEVEL=INFO
   ```

3. **Prepare the Production Configuration**

   ```bash
   cp config/config.prod.toml config/config.toml
   ```

   Edit if needed:

   ```bash
   nano config/config.toml
   ```

4. **Create Required Volumes**

   ```bash
   mkdir -p models logs config monitoring/prometheus/data monitoring/grafana/data
   chmod -R 777 logs monitoring/prometheus/data monitoring/grafana/data
   ```

5. **Deploy with Docker Compose**

   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

6. **Verify Deployment**

   ```bash
   curl http://localhost:8000/health
   ```

   You should see a JSON response with `"status": "ok"`.

### Updating the Deployment

To update to a new version:

```bash
git pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

For detailed Kubernetes deployment instructions, see [kubernetes/README.md](kubernetes/README.md).

## Configuration

### Configuration Hierarchy

The application loads configuration in this order (later sources override earlier ones):

1. Default internal configuration
2. `/app/config/config.toml` (in container)
3. Environment variables
4. Command-line arguments

### Key Configuration Options

| Setting | Description | Default | Environment Variable |
|---------|-------------|---------|---------------------|
| Model Path | Path to model files | `/app/models` | `MODEL_PATH` |
| Model Name | HuggingFace model identifier | `TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T` | `MODEL_NAME` |
| Quantization | Model quantization level | `4bit` | `QUANTIZATION` |
| API Host | API binding address | `0.0.0.0` | `API_HOST` |
| API Port | API listening port | `8000` | `API_PORT` |
| Authentication | Enable API authentication | `true` | `API_REQUIRE_AUTH` |
| Log Level | Logging verbosity | `INFO` | `LOG_LEVEL` |
| Secret Key | Encryption key for tokens | None (required) | `SECRET_KEY` |

## Security Considerations

### Network Security

- **Reverse Proxy**: Deploy behind Nginx or Traefik for SSL termination
- **Firewall**: Restrict access to administration ports (9090 for Prometheus, 3000 for Grafana)
- **Private Network**: Use private network for communication between components

### Authentication and Authorization

- Enable API authentication in production
- Generate a strong secret key: `openssl rand -hex 32`
- Use environment variables to pass sensitive information
- Secure Prometheus and Grafana with authentication

### Docker Security

- Use non-root user in containers
- Set read-only filesystem where possible
- Use explicit image tags, not `latest`
- Scan images for vulnerabilities with Trivy or Docker Scout

### Data Security

- Mount required volumes only
- Use read-only mounts where possible
- Regular backup of configuration and models

## Monitoring

### Prometheus Metrics

The application exposes metrics at the `/metrics` endpoint.

Key metrics:

- `ansible_llm_requests_total`: Total API requests by endpoint and status
- `ansible_llm_request_latency_seconds`: Request latency histograms
- `ansible_llm_model_inference_latency_seconds`: Model inference time
- `ansible_llm_active_requests`: Current active requests

### Grafana Dashboards

Pre-configured Grafana dashboards are available in the `monitoring/grafana/dashboards` directory.

Access Grafana at `http://your-server:3000` with default credentials `admin/admin`.

## Backup and Recovery

### Critical Data to Backup

1. **Configuration Files**:
   - `/app/config/config.toml`
   - `.env` file
   - Prometheus and Grafana configurations

2. **Model Files** (if customized):
   - `/app/models/`

3. **Custom Templates** (if any):
   - Custom prompt templates
   - Custom playbooks

### Backup Procedure

```bash
# Example backup script
#!/bin/bash
BACKUP_DIR="/backup/ansible-llm-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp .env "$BACKUP_DIR/"
cp -r config/ "$BACKUP_DIR/"

# Backup custom models (if needed)
# cp -r models/ "$BACKUP_DIR/"

# Backup monitoring configuration
cp -r monitoring/prometheus/prometheus.yml "$BACKUP_DIR/"
cp -r monitoring/grafana/provisioning "$BACKUP_DIR/"

# Compress backup
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"
```

## Scaling

### Vertical Scaling

Increase resources for the containers:

```yaml
services:
  ansible_llm_api:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

### Horizontal Scaling

For horizontal scaling:

1. Deploy multiple instances behind a load balancer
2. Use shared storage for models (NFS or cloud storage)
3. Configure a shared cache (Redis or Memcached)

## Troubleshooting

### Common Issues

#### API Startup Failures

Check logs:

```bash
docker-compose -f docker-compose.prod.yml logs ansible_llm_api
```

#### Model Loading Errors

Verify model path and permissions:

```bash
docker-compose -f docker-compose.prod.yml exec ansible_llm_api ls -la /app/models
```

#### Memory Issues

Check memory consumption:

```bash
docker stats
```

Consider using a smaller model or increasing quantization.

#### Authentication Failures

Verify secret key is properly set and consistent across instances.

### Support

For additional support:

- Open an issue on GitHub
- Check the FAQ section in the README
- Join the project's discussion forum
