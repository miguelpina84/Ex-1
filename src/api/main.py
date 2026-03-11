"""
HTTP Server for Chain Weighting Analysis
Using ONLY built-in http.server and json (no external dependencies)
Supports both HTTP API and Socket server for chain processing.
"""

import json
import logging
import socket
import time
import os
import re
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from ..models.chain_models import ChainRequest, ChainResponse, ChainResult, HealthCheck
from ..core.chain_processor import ChainProcessor
from ..config.environment import get_config

# cargar confguracion general
config = get_config()
config.create_directories()

os.makedirs(config.paths.logs_directory, exist_ok=True)

root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, config.logging.level))

file_handler = logging.FileHandler(os.path.join(config.paths.logs_directory, config.logging.server_log_file))
file_formatter = logging.Formatter(config.logging.format)
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter(config.logging.format)
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

# Socket Server Configuration
SOCKET_HOST = config.socket.host
SOCKET_PORT = config.socket.port
SOCKET_BUFFER_SIZE = config.socket.buffer_size

def has_double_a(text):
    """Check if text contains double 'a' (case-insensitive)"""
    pattern = re.compile(r'[aA]{2}')
    return bool(pattern.search(text))

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
    """Start socket server in background thread"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    
    try:
        server_socket.bind((SOCKET_HOST, SOCKET_PORT))
        server_socket.listen(config.socket.max_connections)
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

class ChainWeightingHTTPHandler(BaseHTTPRequestHandler):
    """HTTP Request handler for chain weighting API"""
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/v1/process-chains':
            self._handle_process_chains()
        else:
            self._send_error(404, "Not Found")
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/v1/health':
            self._handle_health_check()
        elif self.path == '/api/v1/stats':
            self._handle_stats()
        elif self.path == '/' or self.path == '/docs':
            self._handle_root()
        else:
            self._send_error(404, "Not Found")
    
    def _handle_process_chains(self):
        """Process chains endpoint"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            data = json.loads(body)
            chains = data.get('chains', [])
            
            if not isinstance(chains, list):
                self._send_error(400, "chains must be a list")
                return
            
            logger.info(f"Processing {len(chains)} chains via API")
            start_time = time.time()
            
            results = []
            for idx, chain in enumerate(chains):
                try:
                    weight = calculate_weight(chain)
                    result = ChainResult(
                        index=idx,
                        chain=chain,
                        weight=weight,
                        error=None
                    )
                    results.append(result)
                except Exception as e:
                    result = ChainResult(
                        index=idx,
                        chain=chain,
                        weight=0.0,
                        error=str(e)
                    )
                    results.append(result)
            
            processing_time = time.time() - start_time
            
            response = ChainResponse(
                results=results,
                processing_time=round(processing_time, 3),
                total_chains=len(chains)
            )
            
            # Convert dataclass to dict for JSON serialization
            response_dict = {
                'results': [
                    {
                        'index': r.index,
                        'chain': r.chain,
                        'weight': r.weight,
                        'error': r.error
                    } for r in response.results
                ],
                'processing_time': response.processing_time,
                'total_chains': response.total_chains
            }
            
            self._send_json(200, response_dict)
            logger.info(f"Process completed in {processing_time:.3f} seconds")
            
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error processing chains: {str(e)}")
            self._send_error(500, f"Processing error: {str(e)}")
    
    def _handle_health_check(self):
        """Health check endpoint"""
        response = HealthCheck(
            status="healthy",
            service="Chain Weighting Analysis API",
            version="2.0.0"
        )
        response_dict = {
            'status': response.status,
            'service': response.service,
            'version': response.version
        }
        self._send_json(200, response_dict)
    
    def _handle_stats(self):
        """Statistics endpoint"""
        response = {
            "service": "Chain Weighting API",
            "version": "2.0.0",
            "uptime": "Running",
            "supported_operations": ["chain_processing", "health_check", "statistics"]
        }
        self._send_json(200, response)
    
    def _handle_root(self):
        """Root endpoint with API information"""
        response = {
            "message": "Welcome to Chain Weighting Analysis API",
            "version": "2.0.0",
            "documentation": "/docs",
            "health_check": "/api/v1/health",
            "endpoints": {
                "POST /api/v1/process-chains": "Process chains and calculate weights",
                "GET /api/v1/health": "Health check",
                "GET /api/v1/stats": "Service statistics"
            }
        }
        self._send_json(200, response)
    
    def _send_json(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        response_body = json.dumps(data, ensure_ascii=False)
        self.wfile.write(response_body.encode('utf-8'))
    
    def _send_error(self, status_code, error_message):
        """Send error response"""
        error_response = {
            "error": error_message,
            "status_code": status_code
        }
        self._send_json(status_code, error_response)
    
    def log_message(self, format, *args):
        """Override to use logger instead of print"""
        logger.info(format % args)

def start_http_server():
    """Start HTTP server on configured port"""
    server_address = (config.server.host, config.server.port)
    http_server = HTTPServer(server_address, ChainWeightingHTTPHandler)
    logger.info(f"HTTP server started on {config.server.host}:{config.server.port}")
    logger.info(f"API available at: http://{config.server.host}:{config.server.port}/")
    http_server.serve_forever()

if __name__ == "__main__":
    logger.info("Starting Chain Weighting Server (Built-in Only)...")
    
    # Start socket server in background thread if enabled
    if config.socket.enabled:
        socket_thread = Thread(target=start_socket_server)
        socket_thread.daemon = True
        socket_thread.start()
        logger.info("Socket server background thread started")
    
    # Start HTTP server only if not disabled
    http_enabled = os.getenv("CHAIN_HTTP_ENABLED", "true").lower() == "true"
    if http_enabled:
        try:
            start_http_server()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
    else:
        # Keep main thread alive
        logger.info("HTTP server disabled. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
