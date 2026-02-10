"""
Environment configuration management for the Chain Weighting System.
Handles all environment variables with defaults and validation.
Automatically loads .env files for convenience.
"""

import os
import json
from typing import Optional
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv():
        pass

@dataclass
class ServerConfig:
    """Server configuration from environment variables."""
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    log_level: str = "INFO"

@dataclass
class ProcessingConfig:
    """Processing configuration from environment variables."""
    default_batch_size: int = 10000
    max_concurrent_requests: int = 100
    timeout_seconds: int = 300
    max_chain_length: int = 100
    min_chain_length: int = 50
    max_spaces: int = 5
    min_spaces: int = 3

@dataclass
class PathConfig:
    """Path configuration from environment variables."""
    input_directory: str = "data/input"
    output_directory: str = "data/output"
    temp_directory: str = "data/temp"
    logs_directory: str = "logs"
    config_file: str = "configs/config.json"

@dataclass
class SocketConfig:
    """Socket server configuration from environment variables."""
    host: str = "localhost"
    port: int = 8888
    buffer_size: int = 65536
    max_connections: int = 5
    enabled: bool = True
    timeout_seconds: int = 300

@dataclass
class LoggingConfig:
    """Logging configuration from environment variables."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    server_log_file: str = "server.log"
    client_log_file: str = "client.log"

class EnvironmentConfig:
    """Main configuration class that loads all settings from environment variables."""
    
    def __init__(self):
        # Initialize _config_file_path to default before loading paths to avoid AttributeError
        self._config_file_path = 'configs/config.json'
        
        self.server = self._load_server_config()
        self.processing = self._load_processing_config()
        self.socket = self._load_socket_config()
        self.paths = self._load_path_config()
        self.logging = self._load_logging_config()
    
    def _get_config_value(self, env_var: str, json_path: str, default):
        """Get configuration value with precedence: environment variable → config.json → default value.
        
        Args:
            env_var: Environment variable name
            json_path: Dot notation path in config.json (e.g. 'server.host')
            default: Default value if neither environment nor config file has the value
        """
        # First check environment variable
        env_value = os.getenv(env_var)
        if env_value is not None:
            # Convert to appropriate type based on default
            try:
                if isinstance(default, bool):
                    return env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default, int):
                    return int(env_value)
                elif isinstance(default, float):
                    return float(env_value)
                else:
                    return env_value
            except (ValueError, TypeError):
                # If conversion fails, fall back to default
                pass
        
        # Then check config.json
        try:
            # Use default config file path if we're loading the config_file path itself
            if json_path == 'paths.config_file':
                config_file_path = 'configs/config.json'
            else:
                config_file_path = getattr(self, '_config_file_path', 'configs/config.json')
            
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Navigate the json path (e.g. 'server.host')
                keys = json_path.split('.')
                value = config_data
                for key in keys:
                    value = value[key]
                return value
        except (FileNotFoundError, KeyError, json.JSONDecodeError, TypeError):
            pass
        
        # Return default if neither environment nor config file has the value
        return default

    def _load_server_config(self) -> ServerConfig:
        """Load server configuration with precedence: environment → config.json → defaults."""
        return ServerConfig(
            host=self._get_config_value("CHAIN_SERVER_HOST", "server.host", "127.0.0.1"),
            port=self._get_config_value("CHAIN_SERVER_PORT", "server.port", 8000),
            reload=self._get_config_value("CHAIN_SERVER_RELOAD", "server.reload", True),
            workers=self._get_config_value("CHAIN_SERVER_WORKERS", "server.workers", 1),
            log_level=self._get_config_value("CHAIN_LOG_LEVEL", "logging.level", "INFO")
        )
    
    def _load_processing_config(self) -> ProcessingConfig:
        """Load processing configuration with precedence: environment → config.json → defaults."""
        return ProcessingConfig(
            default_batch_size=self._get_config_value("CHAIN_BATCH_SIZE", "processing.default_batch_size", 10000),
            max_concurrent_requests=self._get_config_value("CHAIN_MAX_CONCURRENT", "processing.max_concurrent_requests", 100),
            timeout_seconds=self._get_config_value("CHAIN_TIMEOUT_SECONDS", "processing.timeout_seconds", 300),
            max_chain_length=self._get_config_value("CHAIN_MAX_LENGTH", "processing.max_chain_length", 100),
            min_chain_length=self._get_config_value("CHAIN_MIN_LENGTH", "processing.min_chain_length", 50),
            max_spaces=self._get_config_value("CHAIN_MAX_SPACES", "processing.max_spaces", 5),
            min_spaces=self._get_config_value("CHAIN_MIN_SPACES", "processing.min_spaces", 3)
        )
    
    def _load_socket_config(self) -> SocketConfig:
        """Load socket configuration with precedence: environment → config.json → defaults."""
        return SocketConfig(
            host=self._get_config_value("CHAIN_SOCKET_HOST", "socket.host", "localhost"),
            port=self._get_config_value("CHAIN_SOCKET_PORT", "socket.port", 8888),
            buffer_size=self._get_config_value("CHAIN_SOCKET_BUFFER_SIZE", "socket.buffer_size", 65536),
            max_connections=self._get_config_value("CHAIN_SOCKET_MAX_CONNECTIONS", "socket.max_connections", 5),
            enabled=self._get_config_value("CHAIN_SOCKET_ENABLED", "socket.enabled", True),
            timeout_seconds=self._get_config_value("CHAIN_SOCKET_TIMEOUT", "socket.timeout_seconds", 300)
        )
    
    def _load_path_config(self) -> PathConfig:
        """Load path configuration with precedence: environment → config.json → defaults."""
        # Load config file path first separately to avoid circular dependency
        config_file_val = self._get_config_value("CHAIN_CONFIG_FILE", "paths.config_file", "configs/config.json")
        # Store it as an instance attribute so other methods can access it
        self._config_file_path = config_file_val
        
        return PathConfig(
            input_directory=self._get_config_value("CHAIN_INPUT_DIR", "paths.input_directory", "data/input"),
            output_directory=self._get_config_value("CHAIN_OUTPUT_DIR", "paths.output_directory", "data/output"),
            temp_directory=self._get_config_value("CHAIN_TEMP_DIR", "paths.temp_directory", "data/temp"),
            logs_directory=self._get_config_value("CHAIN_LOGS_DIR", "paths.logs_directory", "logs"),
            config_file=config_file_val
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration with precedence: environment → config.json → defaults."""
        return LoggingConfig(
            level=self._get_config_value("CHAIN_LOG_LEVEL", "logging.level", "INFO"),
            format=self._get_config_value("CHAIN_LOG_FORMAT", "logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            server_log_file=self._get_config_value("CHAIN_SERVER_LOG_FILE", "logging.server_log_file", "server.log"),
            client_log_file=self._get_config_value("CHAIN_CLIENT_LOG_FILE", "logging.client_log_file", "client.log")
        )
    
    def create_directories(self):
        """Create all required directories based on configuration."""
        import os
        dirs = [
            self.paths.input_directory,
            self.paths.output_directory,
            self.paths.temp_directory,
            self.paths.logs_directory
        ]
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
    
    def get_database_url(self) -> Optional[str]:
        """Get database URL from environment (for future expansion)."""
        return os.getenv("CHAIN_DATABASE_URL")
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL from environment (for future expansion)."""
        return os.getenv("CHAIN_REDIS_URL")
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("CHAIN_ENVIRONMENT", "development").lower() == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return os.getenv("CHAIN_ENVIRONMENT", "development").lower() == "production"

# Global configuration instance
config = EnvironmentConfig()

def get_config() -> EnvironmentConfig:
    """Get the global configuration instance."""
    return config

def print_environment_summary():
    """Print a summary of current environment configuration."""
    cfg = get_config()
    
    print("ENVIRONMENT CONFIGURATION SUMMARY")
    print("=" * 50)
    print(f"Dotenv Support: {'Available' if DOTENV_AVAILABLE else '❌ Not Available (install python-dotenv)'}")
    print(f"Environment File: {'Loaded' if os.path.exists('.env') else '❌ Not Found'}")
    print()
    print("HTTP SERVER (FastAPI)")
    print(f"  Host: {cfg.server.host}")
    print(f"  Port: {cfg.server.port}")
    print(f"  Reload Mode: {cfg.server.reload}")
    print(f"  Workers: {cfg.server.workers}")
    print(f"  Log Level: {cfg.server.log_level}")
    print()
    print("SOCKET SERVER")
    print(f"  Enabled: {cfg.socket.enabled}")
    print(f"  Host: {cfg.socket.host}")
    print(f"  Port: {cfg.socket.port}")
    print(f"  Buffer Size: {cfg.socket.buffer_size} bytes")
    print(f"  Max Connections: {cfg.socket.max_connections}")
    print(f"  Timeout: {cfg.socket.timeout_seconds}s")
    print()
    print("PROCESSING")
    print(f"  Batch Size: {cfg.processing.default_batch_size}")
    print(f"  Max Concurrent: {cfg.processing.max_concurrent_requests}")
    print(f"  Timeout: {cfg.processing.timeout_seconds}s")
    print(f"  Chain Length: {cfg.processing.min_chain_length}-{cfg.processing.max_chain_length}")
    print(f"  Spaces: {cfg.processing.min_spaces}-{cfg.processing.max_spaces}")
    print()
    print("DIRECTORIES")
    print(f"  Input: {cfg.paths.input_directory}")
    print(f"  Output: {cfg.paths.output_directory}")
    print(f"  Temp: {cfg.paths.temp_directory}")
    print(f"  Logs: {cfg.paths.logs_directory}")
    print()
    print("ENVIRONMENT")
    print(f"  Mode: {os.getenv('CHAIN_ENVIRONMENT', 'development')}")
    print(f"  Database URL: {'SET' if cfg.get_database_url() else 'NOT SET'}")
    print(f"  Redis URL: {'SET' if cfg.get_redis_url() else 'NOT SET'}")

if __name__ == "__main__":
    print_environment_summary()