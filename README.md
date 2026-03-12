# Chain Weighting Analysis System

A client-server solution for analyzing character chain weighting metrics.

## Requirements

- Python 3.8+
- No external dependencies required (uses built-in libraries only)

## Installation

```bash
# No installation needed - uses Python built-in only
```

## Running the System

### 1. Start the Server

```bash
python -m src.api.main
```

Server runs on `127.0.0.1:8888` (socket).

### 2. Run the Client

```bash
python client.py --count 1000
```

This will:
- Generate 1000 chains to `data/input/chains.txt`
- Send chains to server via socket
- Save results to `data/output/results.json`

## Command Options

### Client
| Option | Description | Default |
|--------|-------------|---------|
| `--count` | Number of chains to generate | 1000000 |
| `--input` | Input file path | data/input/chains.txt |
| `--output` | Output file path | data/output/results.json |
| `--server` | Server address (host:port) | 127.0.0.1:8888 |
| `--generate-only` | Only generate chains file | false |

## Testing

```bash
# Generate chains only (no server required)
python client.py --count 10 --generate-only

# Generate and process (requires server running)
python client.py --count 10
```
