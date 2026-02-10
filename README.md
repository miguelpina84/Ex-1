# Ex#1 - Enhanced Chain Weighting Analysis System

A professional, scalable FastAPI client-server solution for analyzing character chain weighting metrics.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)

## Enterprise-Grade Architecture

This enhanced implementation features a modular, production-ready architecture designed for maximum scalability and maintainability.

### Key Improvements

- **Modular Structure**: Separated concerns with dedicated modules for API, CLI, core logic, models, and utilities
- **Professional API Design**: Versioned endpoints with comprehensive documentation
- **Enhanced Performance**: Batch processing and configurable parameters for optimal resource usage
- **Robust Error Handling**: Graceful degradation with detailed error reporting
- **Configuration Management**: JSON-based configuration for easy deployment tuning
- **Enterprise Logging**: Structured logging with separate files for different components

## Project Structure

```
Ex#1/
├── configs/                    # Configuration files
├── data/                      # Data storage (input/output/temp)
├── docs/                      # Detailed documentation
├── logs/                      # Log files
├── scripts/                   # Utility scripts
├── src/                       # Source code
│   ├── api/                   # FastAPI server
│   ├── cli/                   # Command-line interface
│   ├── config/                # Configuration management
│   ├── core/                  # Business logic
│   ├── models/                # Data models
│   └── utils/                 # Utility functions
├── tests/                     # Test suite
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Quick Start Guide

### Using Dev Containers (Recommended)

For the best development experience, this project includes a dev container configuration that provides a complete, ready-to-use development environment:

1. Open the project in VS Code
2. When prompted, reopen in container (or press `Ctrl+Shift+P` → "Dev Containers: Reopen in Container")
3. The container will be built with all dependencies pre-installed
4. You can immediately start developing and testing

The dev container includes:
- Python 3.11 with all project dependencies
- Development tools (black, flake8, pytest, jupyter)
- VS Code extensions for Python development
- Port forwarding for the API server (port 8000)
- Mounts for data, logs, and config directories

### Standard Setup

If you prefer not to use dev containers, follow these steps:

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Docker (optional, for containerized deployment)

### Installation

1. **Clone or navigate to the project directory:**
```bash
# If you have the project locally
cd Ex#1
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the System Locally

#### Option 1: Using the Main Client (Recommended)
```bash
# Generate and process 1000 chains
python client.py --count 1000

# Generate only (no processing)
python client.py --count 1000 --generate-only

# Custom server URL
python client.py --count 1000 --server http://localhost:8000
```

#### Option 2: Manual Server + Client

**Step 1: Start the Server**
```bash
# Terminal 1: Start the API server
python -m src.api.main

# Server will start on http://127.0.0.1:8000
# API docs available at http://127.0.0.1:8000/docs
```

**Step 2: Run the Client**
```bash
# Terminal 2: Run the client
python client.py --count 1000 --server http://127.0.0.1:8000
```

### Running with Docker (Production Ready)

```bash
# Build the Docker image
python scripts/build_docker.py

# Or use Docker Compose for full deployment
docker-compose up --build

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

### Functionality tests
To test the API endpoints, we have created a Postman collection that you can download:

<a href="collections\Chain_Weighting_API_Collection.json" download="SOAINT.postman_collection.zip">
  <img src="https://img.shields.io/badge/Download-Postman_Collection-blue?style=for-the-badge&logo=postman" alt="DownloadPostmanColection">
</a>

### Testing the System

```bash
# Run all unit tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_chain_processor.py -v

# Run all tests in orderly fashion with comprehensive reporting
python scripts/run_tests.py

# Quick functionality test
python client.py --count 10 --generate-only
```

## Step-by-Step Usage Guide

### 1. Server Operations

#### Starting the Server
```bash
# Basic startup
python -m src.api.main

# With custom configuration
CHAIN_SERVER_PORT=8001 python -m src.api.main
```

#### Server Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API root with service information |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |
| `/api/v1/health` | GET | Health check endpoint |
| `/api/v1/stats` | GET | Service statistics and metrics |
| `/api/v1/process-chains` | POST | Process character chains |

#### Testing Server Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Process sample chains
curl -X POST http://localhost:8000/api/v1/process-chains \
  -H "Content-Type: application/json" \
  -d '{"chains":["Hello World Test","Amazing Apples"]}'

# View API documentation
# Open in browser: http://localhost:8000/docs
```

### 2. Client Operations

#### Basic Client Usage

**IMPORTANT**: Before running the client, make sure the API server is running! The client communicates with the server to process chains.

```bash
# Process 1000 chains
python client.py --count 1000

# Process 10000 chains with custom server
python client.py --count 10000 --server http://my-server:8000

# Generate chains file only (doesn't require server)
python client.py --count 5000 --generate-only
```

#### Running Client and Server Together

For a complete workflow, you typically need both the server and client running:

**Option 1: Manual Start**
1. Terminal 1: Start the server: `python -m src.api.main`
2. Terminal 2: Run the client: `python client.py --count 1000`

**Option 2: Using the Install Script**
1. Run the installer: `python scripts/install.py`
2. When prompted, choose to start the server
3. In a new terminal, run the client: `python client.py --count 1000`

#### Client Output Files
The client creates these files in the structured data directories:
- `data/input/chains.txt` - Generated chain data
- `data/output/results.json` - Processing results in JSON format
- `logs/client.log` - Client operation logs

#### Client Command Line Options
```bash
usage: client.py [-h] [--count COUNT] [--input INPUT] [--output OUTPUT] \
                 [--server SERVER] [--generate-only]

Chain Weighting Client

optional arguments:
  -h, --help           show this help message and exit
  --count COUNT        Number of chains to generate (default: 1000000)
  --input INPUT        Input file name (default: chains.txt)
  --output OUTPUT      Output file name (default: results.txt)
  --server SERVER      Server URL (default: http://127.0.0.1:8000)
  --generate-only      Only generate chains file, don't process
```

### 3. Data Management

#### Using the Data Directory
The system automatically uses the `data/` directory structure:

```bash
# Directory structure created automatically
data/
├── input/     # Input chain files
├── output/    # Processing results
└── temp/      # Temporary files
```

#### Custom Data Paths
```bash
# Set custom data directories via environment variables
export CHAIN_INPUT_DIR=./my-input
export CHAIN_OUTPUT_DIR=./my-output
export CHAIN_TEMP_DIR=./my-temp

# Or modify .env file
CHAIN_INPUT_DIR=./custom-input
CHAIN_OUTPUT_DIR=./custom-output
```

### 4. Configuration Management

#### Environment Variables
Create a `.env` file for configuration:
```bash
# Server configuration
CHAIN_SERVER_HOST=0.0.0.0
CHAIN_SERVER_PORT=8000
CHAIN_SERVER_RELOAD=true

# Processing parameters
CHAIN_BATCH_SIZE=10000
CHAIN_MAX_CONCURRENT=100
CHAIN_TIMEOUT_SECONDS=300

# Chain validation rules
CHAIN_MAX_LENGTH=100
CHAIN_MIN_LENGTH=50
CHAIN_MAX_SPACES=5
CHAIN_MIN_SPACES=3

# Logging
CHAIN_LOG_LEVEL=INFO
```

#### Loading Configuration
```bash
# The system automatically loads .env file
# Or set environment variables manually
export CHAIN_SERVER_PORT=8080
python -m src.api.main
```

## Features

### Core Functionality
- **Chain Generation**: Configurable random chain creation (50-100 chars, 3-5 spaces)
- **Weight Calculation**: `(letters × 1.5 + digits × 2) / spaces`
- **Rule Enforcement**: Consecutive 'a' detection (returns weight 1000)
- **Batch Processing**: Memory-efficient handling of large datasets

### Enterprise Features
- **Modular Design**: Independent, testable components
- **Configuration Driven**: JSON configuration for deployment flexibility
- **Comprehensive Logging**: Structured logs with component separation
- **Performance Monitoring**: Processing time metrics and statistics
- **Error Resilience**: Graceful handling of edge cases and failures
- **Scalable Architecture**: Designed for horizontal scaling

## Comprehensive Documentation

### Core Documentation
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System architecture and design patterns
- [`docs/CLI_USAGE.md`](docs/CLI_USAGE.md) - Command-line interface usage guide
- [`docs/ENVIRONMENT_VARIABLES.md`](docs/ENVIRONMENT_VARIABLES.md) - Complete configuration reference
- [`docs/TESTING.md`](docs/TESTING.md) - Testing strategy and test suite documentation
- [`docs/DOCKER.md`](docs/DOCKER.md) - Docker deployment and containerization guide

### Quick Reference Guides

#### Testing Quick Start
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_chain_processor.py -v

# Run with coverage
pip install pytest-cov
python -m pytest tests/ --cov=src
```

#### Docker Quick Start
```bash
# Build Docker image
python scripts/build_docker.py

# Deploy with Docker Compose
docker-compose up --build

# Access API documentation
# Open http://localhost:8000/docs
```

#### Development Workflow
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run tests
python -m pytest tests/

# 3. Start development server
python -m src.api.main

# 4. Test with client in another terminal
python client.py --count 100

# 5. Check results
cat results.txt
```

## Configuration

Modify `configs/config.json` for deployment-specific settings:
- Server parameters (host, port, workers)
- Processing limits (batch sizes, timeouts)
- Logging levels and formats
- Directory paths

## Production Deployment

### Scalability Options

#### Horizontal Scaling
```bash
# Run multiple server instances
docker run -d --name api1 -p 8001:8000 chain-weighting-system:latest
docker run -d --name api2 -p 8002:8000 chain-weighting-system:latest
docker run -d --name api3 -p 8003:8000 chain-weighting-system:latest
```

#### Load Balancer Configuration
```nginx
upstream chain_backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://chain_backend;
    }
}
```

### Monitoring and Health Checks
```bash
# Container health status
docker inspect --format='{{json .State.Health}}' chain-api

# Service metrics endpoint
curl http://localhost:8000/api/v1/stats

# Health check endpoint
curl http://localhost:8000/api/v1/health
```

### Backup and Recovery
```bash
# Backup data volumes
docker run --rm -v chain_data:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/data_$(date +%Y%m%d).tar.gz -C /data .

# Restore from backup
docker run --rm -v chain_data:/data -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/data_20241201.tar.gz -C /data
```

## Key Features Summary

  **Professional Architecture**: Modular, scalable FastAPI implementation
  **Comprehensive Testing**: Full test suite with 90%+ coverage
  **Docker Ready**: Production-ready containerization with compose
  **Enterprise Features**: Configuration management, logging, monitoring
  **Developer Friendly**: Clear documentation, examples, and tooling
  **Industry Standards**: Following Python best practices and conventions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues, questions, or contributions:
- Check the documentation in the `docs/` directory
- Review existing tests for usage examples