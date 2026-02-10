# Enhanced Chain Weighting Analysis System

## Professional Project Structure

This enhanced version features a scalable, modular architecture designed for enterprise-level deployment.

### Directory Structure

```
Ex#1/
├── configs/                    # Configuration files
│   └── config.json            # Main configuration
├── data/                      # Data storage
│   ├── input/                 # Input chain files
│   ├── output/                # Processing results
│   └── temp/                  # Temporary files
├── docs/                      # Documentation
├── logs/                      # Log files
├── src/                       # Source code (modular structure)
│   ├── api/                   # FastAPI server implementation
│   │   ├── __init__.py
│   │   └── main.py           # Enhanced API server
│   ├── cli/                   # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py           # Enhanced client CLI
│   ├── core/                  # Business logic
│   │   ├── __init__.py
│   │   └── chain_processor.py # Core processing logic
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   └── chain_models.py   # Pydantic models
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── helpers.py        # Helper classes
├── tests/                     # Test suite
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Enhanced Features

#### API Server (`src/api/main.py`)
- **Modular FastAPI implementation** with proper routing
- **Enhanced endpoints** with versioning (`/api/v1/`)
- **CORS support** for cross-origin requests
- **Interactive documentation** at `/docs` and `/redoc`
- **Health check endpoint** with service information
- **Statistics endpoint** for monitoring
- **Structured logging** with separate log files

#### Client CLI (`src/cli/main.py`)
- **Batch processing** for memory efficiency
- **Configurable timeouts** and batch sizes
- **Progress tracking** and detailed logging
- **Enhanced error handling** with proper exceptions
- **Async context managers** for resource management
- **Metadata-rich output** with processing statistics

#### Core Logic (`src/core/chain_processor.py`)
- **Separation of concerns** - pure business logic
- **Class-based design** for extensibility
- **Comprehensive error handling**
- **Type hints** for better code quality

#### Utilities (`src/utils/helpers.py`)
- **ChainGenerator class** for flexible chain creation
- **FileManager class** for robust file operations
- **Reusable components** for different use cases

#### Data Models (`src/models/chain_models.py`)
- **Pydantic models** with validation
- **Structured responses** with metadata
- **Extensible design** for future enhancements

### Configuration Management

The system uses `configs/config.json` for:
- Server settings (host, port, workers)
- Processing parameters (batch sizes, timeouts)
- Logging configuration
- Path definitions

### Scalability Features

1. **Modular Architecture**: Each component is independently testable and deployable
2. **Batch Processing**: Handles large datasets efficiently
3. **Configurable Parameters**: Easy tuning for different environments
4. **Proper Error Handling**: Graceful degradation and informative errors
5. **Structured Logging**: Centralized logging with rotation support
6. **Versioned API**: Backward compatibility maintained

### Usage Examples

#### Start Server
```bash
python -m src.api.main
```

#### Run Client (Basic)
```bash
python -m src.cli.main --count 1000000
```

#### Run Client (Advanced)
```bash
python -m src.cli.main \
  --count 5000000 \
  --input data/input/large_dataset.txt \
  --output data/output/results.json \
  --batch-size 50000 \
  --timeout 600 \
  --verbose
```

#### Generate Only
```bash
python -m src.cli.main --generate-only --count 100000
```

### Performance Optimizations

- **Async I/O** for non-blocking operations
- **Batch processing** to manage memory usage
- **Connection pooling** in HTTP clients
- **Efficient data structures** for chain processing
- **Configurable timeouts** to prevent hanging

### Development Features

- **Type hints** throughout the codebase
- **Comprehensive docstrings**
- **Modular testing structure** (tests/)
- **Configuration-driven** behavior
- **Environment-aware** logging levels