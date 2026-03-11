"""
Simple configuration for Chain Weighting System.
Uses built-in libraries only.
"""

import os

SOCKET_HOST = "localhost"
SOCKET_PORT = 8888
SOCKET_BUFFER_SIZE = 65536
SOCKET_MAX_CONNECTIONS = 5

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
SERVER_LOG_FILE = "server.log"
CLIENT_LOG_FILE = "client.log"

INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
LOG_DIR = "logs"

def create_directories():
    """Create required directories."""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
