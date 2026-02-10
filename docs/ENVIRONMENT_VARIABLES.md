# Environment Variables Configuration

This document describes all environment variables that can be used to configure the Enhanced Chain Weighting System.

## Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAIN_SERVER_HOST` | `127.0.0.1` | Server host address |
| `CHAIN_SERVER_PORT` | `8000` | Server port number |
| `CHAIN_SERVER_RELOAD` | `true` | Enable auto-reload in development |
| `CHAIN_SERVER_WORKERS` | `1` | Number of worker processes |
| `CHAIN_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Processing Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAIN_BATCH_SIZE` | `10000` | Default batch size for processing |
| `CHAIN_MAX_CONCURRENT` | `100` | Maximum concurrent requests |
| `CHAIN_TIMEOUT_SECONDS` | `300` | Request timeout in seconds |
| `CHAIN_MAX_LENGTH` | `100` | Maximum chain length |
| `CHAIN_MIN_LENGTH` | `50` | Minimum chain length |
| `CHAIN_MAX_SPACES` | `5` | Maximum spaces per chain |
| `CHAIN_MIN_SPACES` | `3` | Minimum spaces per chain |

## Path Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAIN_INPUT_DIR` | `data/input` | Input files directory |
| `CHAIN_OUTPUT_DIR` | `data/output` | Output files directory |
| `CHAIN_TEMP_DIR` | `data/temp` | Temporary files directory |
| `CHAIN_LOGS_DIR` | `logs` | Logs directory |
| `CHAIN_CONFIG_FILE` | `configs/config.json` | Configuration file path |

## Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAIN_LOG_LEVEL` | `INFO` | Global logging level |
| `CHAIN_LOG_FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format |
| `CHAIN_SERVER_LOG_FILE` | `server_enhanced.log` | Server log filename |
| `CHAIN_CLIENT_LOG_FILE` | `client_enhanced.log` | Client log filename |

## Environment Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHAIN_ENVIRONMENT` | `development` | Environment mode (development/production) |
| `CHAIN_DATABASE_URL` | *(unset)* | Database connection URL (optional) |
| `CHAIN_REDIS_URL` | *(unset)* | Redis connection URL (optional) |

## Usage Examples

### Development Environment
```bash
export CHAIN_ENVIRONMENT=development
export CHAIN_SERVER_HOST=localhost
export CHAIN_SERVER_PORT=8000
export CHAIN_LOG_LEVEL=DEBUG
```

### Production Environment
```bash
export CHAIN_ENVIRONMENT=production
export CHAIN_SERVER_HOST=0.0.0.0
export CHAIN_SERVER_PORT=80
export CHAIN_SERVER_WORKERS=4
export CHAIN_LOG_LEVEL=WARNING
```

### High-Performance Processing
```bash
export CHAIN_BATCH_SIZE=50000
export CHAIN_MAX_CONCURRENT=200
export CHAIN_TIMEOUT_SECONDS=600
```

### Custom Paths
```bash
export CHAIN_INPUT_DIR=/var/data/chains/input
export CHAIN_OUTPUT_DIR=/var/data/chains/output
export CHAIN_LOGS_DIR=/var/log/chains
```

### Flexible Chain Generation
```bash
export CHAIN_MIN_LENGTH=20
export CHAIN_MAX_LENGTH=200
export CHAIN_MIN_SPACES=1
export CHAIN_MAX_SPACES=10
```

## Quick Start Script

Create a `.env` file with your configuration:

```bash
# .env
CHAIN_ENVIRONMENT=development
CHAIN_SERVER_PORT=8000
CHAIN_BATCH_SIZE=10000
CHAIN_LOG_LEVEL=INFO
CHAIN_INPUT_DIR=data/input
CHAIN_OUTPUT_DIR=data/output
```

Then load it in your shell:
```bash
source .env
python -m src.api.main
```

## 🛠️ Docker Example

```dockerfile
FROM python:3.11-slim

ENV CHAIN_ENVIRONMENT=production
ENV CHAIN_SERVER_HOST=0.0.0.0
ENV CHAIN_SERVER_PORT=8000
ENV CHAIN_SERVER_WORKERS=4

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python", "-m", "src.api.main"]
```

## Configuration Precedence

1. Environment variables (highest priority)
2. Configuration files
3. Built-in defaults (lowest priority)

The system will always fall back to sensible defaults if environment variables are not set.