"""
Socket Server for Chain Weighting Analysis
Using ONLY built-in libraries
"""

import logging
import socket
import time
import os
import re
from threading import Thread

from ..config.environment import (
    SOCKET_HOST, SOCKET_PORT, SOCKET_BUFFER_SIZE, SOCKET_MAX_CONNECTIONS,
    LOG_LEVEL, LOG_FORMAT, SERVER_LOG_FILE, LOG_DIR,
    create_directories
)

create_directories()

root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, LOG_LEVEL))

file_handler = logging.FileHandler(os.path.join(LOG_DIR, SERVER_LOG_FILE))
file_formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter(LOG_FORMAT)
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)


def has_double_a(text):
    """Check if text contains double 'a' (case-insensitive)"""
    return bool(re.search(r'[aA]{2}', text))


def calculate_weight(text):
    """Calculate weight for a single chain"""
    if has_double_a(text):
        logger.warning(f"Double 'a' rule detected >> '{text}'")
        return 1000.0
    
    letters = sum(1 for c in text if c.isalpha())
    numbers = sum(1 for c in text if c.isdigit())
    spaces = text.count(' ')
    
    if spaces == 0:
        return 0.0
    
    return (letters * 1.5 + numbers * 2) / spaces


def handle_socket_client(client_socket, address):
    """Handle incoming socket client connection"""
    logger.info(f"New socket connection from {address}")
    
    try:
        start_time = time.time()
        chains_received = 0
        
        while True:
            data = client_socket.recv(SOCKET_BUFFER_SIZE)
            if not data:
                break
            
            chains = data.decode('utf-8').strip().split('\n')
            results = []
            
            for chain in chains:
                if chain.strip():
                    weight = calculate_weight(chain.strip())
                    results.append(f"{weight:.2f}")
                    chains_received += 1
            
            if results:
                response = '\n'.join(results) + '\n'
                client_socket.sendall(response.encode('utf-8'))
        
        processing_time = time.time() - start_time
        logger.info(f"Processed {chains_received} chains from {address} in {processing_time:.2f} seconds")
        logger.info(f"Process completed in {processing_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error handling socket client {address}: {e}")
    finally:
        client_socket.close()
        logger.info(f"Socket connection closed from {address}")


def start_socket_server():
    """Start socket server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    
    try:
        server_socket.bind((SOCKET_HOST, SOCKET_PORT))
        server_socket.listen(SOCKET_MAX_CONNECTIONS)
        logger.info(f"Socket server started on {SOCKET_HOST}:{SOCKET_PORT}")
        
        while True:
            client_socket, address = server_socket.accept()
            client_thread = Thread(target=handle_socket_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
            
    except Exception as e:
        logger.error(f"Socket server error: {e}")
    finally:
        server_socket.close()
        logger.info("Socket server closed")


if __name__ == "__main__":
    logger.info("Starting Chain Weighting Socket Server...")
    start_socket_server()
