"""
Client for Chain Weighting Analysis
Generates character chains and communicates with the server for processing.
"""

import argparse
import asyncio
import logging
import os
import random
import socket
import string
import time
from typing import List
import json

# Get configuration and create required directories
from src.config.environment import get_config
config = get_config()
os.makedirs(config.paths.logs_directory, exist_ok=True)
os.makedirs(config.paths.input_directory, exist_ok=True)
os.makedirs(config.paths.output_directory, exist_ok=True)

# Configure logging using configuration
# Get the root logger and add handlers to it
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create and add file handler
file_handler = logging.FileHandler(os.path.join(config.paths.logs_directory, config.logging.client_log_file))
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)
logger = logging.getLogger(__name__)

def generate_random_chain() -> str:
    """
    Generate a random chain according to specifications:
    - Length between 50-100 characters
    - Contains only a-zA-Z0-9 and spaces
    - Has 3-5 non-consecutive spaces
    - No spaces at beginning or end
    
    Returns:
        Generated chain string
    """
    # Define allowed characters
    allowed_chars = string.ascii_letters + string.digits
    
    # Random length between 50-100
    length = random.randint(50, 100)
    
    # Number of spaces (3-5)
    space_count = random.randint(3, 5)
    
    # Generate base characters without spaces
    char_count = length - space_count
    chain_chars = [random.choice(allowed_chars) for _ in range(char_count)]
    
    # Insert spaces at random positions (non-consecutive, not at start/end)
    positions = []
    max_attempts = 100
    attempts = 0
    
    while len(positions) < space_count and attempts < max_attempts:
        pos = random.randint(1, len(chain_chars) - 1)  # Avoid start/end
        # Ensure spaces are not consecutive
        if pos not in positions and (pos - 1) not in positions and (pos + 1) not in positions:
            positions.append(pos)
        attempts += 1
    
    # Insert spaces
    for pos in sorted(positions, reverse=True):
        chain_chars.insert(pos, ' ')
    
    return ''.join(chain_chars)

def generate_chains_file(filename: str = None, count: int = 1000000) -> None:
    """
    Generate a file containing random chains.
    
    Args:
        filename: Output filename (defaults to data/input/chains.txt)
        count: Number of chains to generate
    """
    # Use default path if not specified
    if filename is None:
        from src.config.environment import get_config
        config = get_config()
        filename = os.path.join(config.paths.input_directory, "chains.txt")
    
    logger.info(f"Generating {count} chains to {filename}")
    start_time = time.time()
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(count):
            chain = generate_random_chain()
            f.write(chain + '\n')
            
            # Progress indicator
            if (i + 1) % 100000 == 0:
                logger.info(f"Generated {i + 1}/{count} chains")
    
    generation_time = time.time() - start_time
    logger.info(f"Chain generation completed in {generation_time:.2f} seconds")

def read_chains_from_file(filename: str = None) -> List[str]:
    """
    Read chains from file.
    
    Args:
        filename: Input filename (defaults to data/input/chains.txt)
        
    Returns:
        List of chain strings
    """
    # Use default path if not specified
    if filename is None:
        from src.config.environment import get_config
        config = get_config()
        filename = os.path.join(config.paths.input_directory, "chains.txt")
    
    logger.info(f"Reading chains from {filename}")
    chains = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            chains = [line.strip() for line in f if line.strip()]
        logger.info(f"Read {len(chains)} chains from file")
    except FileNotFoundError:
        logger.error(f"File {filename} not found")
        raise
    
    return chains

def send_chains_to_server(chains: List[str], server_address: str = "127.0.0.1:8888") -> dict:
    """
    Send chains to server for processing via socket connection.
    
    Args:
        chains: List of chain strings
        server_address: Server address in format 'host:port' (default: 127.0.0.1:8888)
        
    Returns:
        Dictionary with results containing weights
    """
    # Parse server address
    if ':' in server_address:
        host, port = server_address.split(':')
        port = int(port)
    else:
        host = server_address
        port = 8888
    
    logger.info(f"Connecting to socket server at {host}:{port}")
    logger.info(f"Sending {len(chains)} chains to server")
    start_time = time.time()
    
    try:
        # Create socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # Send chains as newline-separated text
        chains_data = '\n'.join(chains) + '\n'
        client_socket.sendall(chains_data.encode('utf-8'))
        
        # Receive results
        results_data = b''
        while True:
            chunk = client_socket.recv(65536)
            if not chunk:
                break
            results_data += chunk
        
        client_socket.close()
        
        # Parse results
        results_text = results_data.decode('utf-8').strip()
        weights = [float(w) for w in results_text.split('\n') if w.strip()]
        
        # Format response similar to HTTP API
        result = {
            "status": "success",
            "chains_processed": len(chains),
            "weights": weights,
            "summary": {
                "min": min(weights) if weights else 0,
                "max": max(weights) if weights else 0,
                "average": sum(weights) / len(weights) if weights else 0
            }
        }
        
        processing_time = time.time() - start_time
        logger.info(f"Server response received in {processing_time:.2f} seconds")
        return result
        
    except Exception as e:
        logger.error(f"Failed to communicate with server: {str(e)}")
        raise

def save_results_to_file(results: dict, filename: str = None) -> None:
    """
    Save processing results to file.
    
    Args:
        results: Results dictionary from server
        filename: Output filename (defaults to data/output/results.json)
    """
    # Use default path if not specified
    if filename is None:
        from src.config.environment import get_config
        config = get_config()
        filename = os.path.join(config.paths.output_directory, "results.json")
    
    logger.info(f"Saving results to {filename}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved successfully")

async def main():
    """Main client function"""
    parser = argparse.ArgumentParser(description="Chain Weighting Client")
    parser.add_argument("--count", type=int, default=1000000, 
                       help="Number of chains to generate (default: 1000000)")
    parser.add_argument("--input", type=str, default=None,
                       help="Input file name (default: data/input/chains.txt)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output file name (default: data/output/results.json)")
    parser.add_argument("--server", type=str, default="127.0.0.1:8888",
                       help="Server address in format 'host:port' (default: 127.0.0.1:8888)")
    parser.add_argument("--generate-only", action="store_true",
                       help="Only generate chains file, don't process")
    
    args = parser.parse_args()
    
    total_start_time = time.time()
    
    try:
        # Generate chains file
        generate_chains_file(args.input, args.count)
        
        if args.generate_only:
            logger.info("Chain generation completed. Exiting.")
            return
        
        # Read chains from file
        chains = read_chains_from_file(args.input)
        
        # Send to server for processing using executor to run synchronous socket code
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, send_chains_to_server, chains, args.server)
        
        # Save results
        save_results_to_file(results, args.output)
        
        total_time = time.time() - total_start_time
        logger.info(f"Client operation completed in {total_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Client operation failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())