# CLI Usage Guide

This document provides comprehensive documentation for the Enhanced Chain Weighting System command-line interface (CLI).

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Basic Usage](#basic-usage)
4. [Command-Line Arguments](#command-line-arguments)
5. [Advanced Usage](#advanced-usage)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)

## Overview

The Enhanced Chain Weighting System provides a command-line interface for generating and processing character chains. The CLI consists of two main components:

- **Client**: Generates and processes chains using the API server
- **Launcher**: Simplified interface for starting server and client operations

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Pip package manager

### Initial Setup
```bash
# Navigate to project directory
cd Ex#1

# Install dependencies
pip install -r requirements.txt

# Run the automated installer
python scripts/install.py
```

## Basic Usage

### Direct Client Usage

```bash
# Generate and process 1 million chains (default)
python -m src.cli.main

# Generate 100,000 chains
python -m src.cli.main --count 100000

# Generate chains only (no processing)
python -m src.cli.main --count 50000 --generate-only
```

## Command-Line Arguments

### Client Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--count` | Integer | 1,000,000 | Number of chains to generate |
| `--input` | String | `data/input/chains.txt` | Input file name |
| `--output` | String | `data/output/results.json` | Output file name |
| `--server` | String | `http://127.0.0.1:8000` | Server URL |
| `--generate-only` | Flag | N/A | Only generate chains, don't process |
| `--timeout` | Integer | 300 | Server request timeout in seconds |
| `--batch-size` | Integer | 10,000 | Process chains in batches |
| `--verbose` | Flag | N/A | Enable verbose logging |

### Launcher Arguments

| Subcommand | Description |
|------------|-------------|
| `server` | Start the API server |
| `client` | Run the client with arguments |
| `quick-start` | Run a demonstration |

## Advanced Usage

### Custom Server Configuration

Connect to a remote server:

```bash
python -m src.cli.main --count 50000 --server http://remote-server:8000
```

### Custom File Paths

Specify custom input and output files:

```bash
python -m src.cli.main \
  --input data/input/custom_input.txt \
  --output data/output/custom_results.json \
  --count 10000
```

### Batch Processing

Process large datasets efficiently:

```bash
python -m src.cli.main \
  --count 1000000 \
  --batch-size 50000 \
  --timeout 600
```

### Environment Configuration

Use environment variables to configure the system:

```bash
# Set server port
export CHAIN_SERVER_PORT=8080

# Set batch size
export CHAIN_BATCH_SIZE=50000

# Run with custom configuration
python -m src.cli.main --count 100000
```

### Configuration File

The system uses `configs/config.json` for default configuration:

```json
{
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": true,
        "workers": 1
    },
    "processing": {
        "default_batch_size": 10000,
        "max_concurrent_requests": 100,
        "timeout_seconds": 300
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "paths": {
        "input_directory": "data/input",
        "output_directory": "data/output",
        "temp_directory": "data/temp",
        "logs_directory": "logs"
    }
}
```

## Examples

### Running Tests
```bash
# Run all tests in an orderly fashion with comprehensive reporting
python scripts/run_tests.py

# Run specific test modules
python -m pytest tests/test_chain_processor.py -v
python -m pytest tests/ -v
```  
### Basic Processing
```bash
# Process 100,000 chains
python -m src.cli.main --count 100000
```

### Server and Client in Separate Terminals
Terminal 1:
```bash
# Start server
python -m src.api.main
```

Terminal 2:
```bash
# Process chains with custom server URL
python -m src.cli.main --count 50000 --server http://localhost:8000
```

### Generate Chains Only
```bash
# Generate chains file without processing
python -m src.cli.main --count 200000 --generate-only
```

### Verbose Output
```bash
# Enable detailed logging
python -m src.cli.main --count 10000 --verbose
```

### Custom Batch Size
```bash
# Process with smaller batches for memory efficiency
python -m src.cli.main --count 500000 --batch-size 5000
```

## Troubleshooting

### Important Note: Server Must Be Running
⚠️ **CRITICAL**: The client requires the API server to be running to process chains. If you're getting connection errors, make sure the server is started first:

1. Terminal 1: `python -m src.api.main` (start the server)
2. Terminal 2: Run your client command

### Common Issues

#### Server Not Responding
- Verify the server is running: `curl http://127.0.0.1:8000/api/v1/health`
- Check firewall settings
- Verify the correct port is being used

#### Out of Memory Errors
- Reduce batch size: `--batch-size 5000`
- Process smaller datasets
- Close other applications to free memory

#### Timeout Errors
- Increase timeout: `--timeout 600`
- Check network connectivity
- Verify server performance

#### Permission Errors
- Ensure write permissions to `data/` and `logs/` directories
- Run with appropriate user privileges

### Debugging Tips

#### Enable Verbose Logging
```bash
python -m src.cli.main --count 1000 --verbose
```

#### Check Server Logs
- Server logs: `logs/server_enhanced.log`
- Client logs: `logs/client_enhanced.log`

#### Test Server Endpoints
```bash
# Health check
curl http://127.0.0.1:8000/api/v1/health

# Process sample data
curl -X POST http://127.0.0.1:8000/api/v1/process-chains \
  -H "Content-Type: application/json" \
  -d '{"chains":["Hello World Test","Amazing Apples"]}'
```

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `CHAIN_SERVER_HOST` | Server host | `127.0.0.1` |
| `CHAIN_SERVER_PORT` | Server port | `8000` |
| `CHAIN_SERVER_RELOAD` | Enable auto-reload | `true` |
| `CHAIN_BATCH_SIZE` | Default batch size | `10000` |
| `CHAIN_TIMEOUT_SECONDS` | Request timeout | `300` |
| `CHAIN_INPUT_DIR` | Input directory | `data/input` |
| `CHAIN_OUTPUT_DIR` | Output directory | `data/output` |
| `CHAIN_LOG_LEVEL` | Logging level | `INFO` |