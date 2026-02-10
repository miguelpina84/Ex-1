"""
Unit tests for configuration functionality.
Tests environment configuration loading and validation.
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config.environment import get_config, EnvironmentConfig


class TestConfiguration:
    """Test suite for configuration functionality."""

    def test_get_config_returns_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_config_has_required_sections(self):
        """Test that configuration has all required sections."""
        config = get_config()
        
        # Check main sections exist
        assert hasattr(config, 'server')
        assert hasattr(config, 'paths')
        assert hasattr(config, 'processing')
        assert hasattr(config, 'logging')

    def test_server_config_defaults(self):
        """Test server configuration defaults."""
        config = get_config()
        
        # Check server defaults
        assert hasattr(config.server, 'host')
        assert hasattr(config.server, 'port')
        assert hasattr(config.server, 'reload')
        assert hasattr(config.server, 'workers')

    def test_paths_config_defaults(self):
        """Test paths configuration defaults."""
        config = get_config()
        
        # Check paths exist
        assert hasattr(config.paths, 'input_directory')
        assert hasattr(config.paths, 'output_directory')
        assert hasattr(config.paths, 'temp_directory')
        assert hasattr(config.paths, 'logs_directory')

    def test_processing_config_defaults(self):
        """Test processing configuration defaults."""
        config = get_config()
        
        # Check processing parameters
        assert hasattr(config.processing, 'min_chain_length')
        assert hasattr(config.processing, 'max_chain_length')
        assert hasattr(config.processing, 'min_spaces')
        assert hasattr(config.processing, 'max_spaces')
        assert hasattr(config.processing, 'default_batch_size')

    def test_logging_config_defaults(self):
        """Test logging configuration defaults."""
        config = get_config()
        
        # Check logging settings
        assert hasattr(config.logging, 'level')
        assert hasattr(config.logging, 'format')
        assert hasattr(config.logging, 'server_log_file')
        assert hasattr(config.logging, 'client_log_file')

    def test_config_from_environment_variables(self):
        """Test configuration from environment variables."""
        # Test with custom environment
        test_env = {
            'CHAIN_SERVER_HOST': '192.168.1.100',
            'CHAIN_SERVER_PORT': '9000',
            'CHAIN_BATCH_SIZE': '5000',
            'CHAIN_LOG_LEVEL': 'DEBUG'
        }
        
        with patch.dict(os.environ, test_env):
            # Create new config instance to pick up environment changes
            config = EnvironmentConfig()
            
            assert config.server.host == '192.168.1.100'
            assert config.server.port == 9000
            assert config.processing.default_batch_size == 5000
            assert config.logging.level == 'DEBUG'

    def test_config_type_conversion(self):
        """Test that environment variables are converted to correct types."""
        test_env = {
            'CHAIN_SERVER_PORT': '8080',
            'CHAIN_BATCH_SIZE': '1000',
            'CHAIN_MAX_CONCURRENT': '50'
        }
        
        with patch.dict(os.environ, test_env):
            config = EnvironmentConfig()
            
            # Should be integers, not strings
            assert isinstance(config.server.port, int)
            assert isinstance(config.processing.default_batch_size, int)
            assert isinstance(config.processing.max_concurrent_requests, int)
            
            assert config.server.port == 8080
            assert config.processing.default_batch_size == 1000
            assert config.processing.max_concurrent_requests == 50

    def test_config_create_directories(self):
        """Test that create_directories method works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the paths to use temporary directory
            config = get_config()
            
            # Override paths to use temp directory
            test_input = os.path.join(temp_dir, "input")
            test_output = os.path.join(temp_dir, "output")
            test_temp = os.path.join(temp_dir, "temp")
            test_logs = os.path.join(temp_dir, "logs")
            
            config.paths.input_directory = test_input
            config.paths.output_directory = test_output
            config.paths.temp_directory = test_temp
            config.paths.logs_directory = test_logs
            
            # Directories shouldn't exist yet
            assert not os.path.exists(test_input)
            assert not os.path.exists(test_output)
            assert not os.path.exists(test_temp)
            assert not os.path.exists(test_logs)
            
            # Create directories
            config.create_directories()
            
            # Directories should now exist
            assert os.path.exists(test_input)
            assert os.path.exists(test_output)
            assert os.path.exists(test_temp)
            assert os.path.exists(test_logs)
            
            # Should be directories, not files
            assert os.path.isdir(test_input)
            assert os.path.isdir(test_output)
            assert os.path.isdir(test_temp)
            assert os.path.isdir(test_logs)

    def test_config_boolean_values(self):
        """Test boolean configuration values."""
        test_env = {
            'CHAIN_SERVER_RELOAD': 'true',
            'CHAIN_SERVER_RELOAD_FALSE': 'false'
        }
        
        with patch.dict(os.environ, test_env):
            config = EnvironmentConfig()
            
            # Test boolean conversion
            assert config.server.reload is True
            
            # Test with explicit false value
            with patch.dict(os.environ, {'CHAIN_SERVER_RELOAD': 'false'}):
                config_false = EnvironmentConfig()
                assert config_false.server.reload is False

    def test_config_fallback_values(self):
        """Test that configuration falls back to defaults for invalid values."""
        test_env = {
            'CHAIN_SERVER_PORT': 'invalid_port',  # Invalid integer
            'CHAIN_BATCH_SIZE': 'not_a_number'    # Invalid integer
        }
        
        with patch.dict(os.environ, test_env):
            # This should either use defaults or handle the conversion gracefully
            config = EnvironmentConfig()
            
            # The config should still be usable even with invalid env vars
            assert hasattr(config.server, 'port')
            assert hasattr(config.processing, 'default_batch_size')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])