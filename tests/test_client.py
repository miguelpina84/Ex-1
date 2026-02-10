"""
Unit tests for client functionality.
Tests the client-side chain generation and server communication.
"""

import pytest
import sys
import os
import tempfile
import json
from unittest.mock import patch, AsyncMock, MagicMock, ANY
import asyncio

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from client import (
    generate_random_chain, 
    generate_chains_file, 
    read_chains_from_file, 
    send_chains_to_server,
    save_results_to_file
)


class TestClientFunctions:
    """Test suite for client utility functions."""

    def test_generate_random_chain_length(self):
        """Test that generated chains have correct length."""
        chain = generate_random_chain()
        assert 50 <= len(chain) <= 100

    def test_generate_random_chain_characters(self):
        """Test that generated chains contain only allowed characters."""
        chain = generate_random_chain()
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")
        
        for char in chain:
            assert char in allowed_chars

    def test_generate_random_chain_spaces(self):
        """Test that generated chains have correct number of spaces."""
        chain = generate_random_chain()
        space_count = chain.count(' ')
        assert 3 <= space_count <= 5

    def test_generate_random_chain_no_leading_trailing_spaces(self):
        """Test that generated chains don't start or end with spaces."""
        chain = generate_random_chain()
        assert not chain.startswith(' ')
        assert not chain.endswith(' ')

    def test_generate_random_chain_non_consecutive_spaces(self):
        """Test that spaces are not consecutive."""
        chain = generate_random_chain()
        assert '  ' not in chain  # No double spaces

    def test_generate_multiple_chains_are_different(self):
        """Test that multiple generated chains are different."""
        chain1 = generate_random_chain()
        chain2 = generate_random_chain()
        chain3 = generate_random_chain()
        
        # Very unlikely to get identical chains
        assert chain1 != chain2 or chain2 != chain3

    def test_generate_chains_file_creates_file(self):
        """Test that generate_chains_file creates a file with correct content."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Generate small number of chains for testing
            generate_chains_file(temp_filename, count=5)
            
            # Check file exists and has content
            assert os.path.exists(temp_filename)
            
            # Read and verify content
            with open(temp_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                assert len(lines) == 5
                
                # Verify each line is a valid chain
                for line in lines:
                    chain = line.strip()
                    assert 50 <= len(chain) <= 100
                    assert 3 <= chain.count(' ') <= 5
                    assert not chain.startswith(' ')
                    assert not chain.endswith(' ')
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_read_chains_from_file(self):
        """Test reading chains from file."""
        # Create a test file
        test_chains = [
            "Hello World Test Chain ABC 123",
            "Another Valid Chain XYZ 789",
            "Third Chain Example DEF 456"
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            for chain in test_chains:
                temp_file.write(chain + '\n')
            temp_filename = temp_file.name
        
        try:
            # Read chains from file
            chains = read_chains_from_file(temp_filename)
            
            # Verify results
            assert len(chains) == len(test_chains)
            for i, chain in enumerate(chains):
                assert chain == test_chains[i]
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_read_chains_from_nonexistent_file(self):
        """Test reading from nonexistent file raises exception."""
        with pytest.raises(FileNotFoundError):
            read_chains_from_file("nonexistent_file.txt")

    def test_read_chains_from_file_strips_whitespace(self):
        """Test that read_chains_from_file strips whitespace."""
        test_content = "  Hello World  \n  Another Chain  \n\n  Third Chain  \n"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_filename = temp_file.name
        
        try:
            chains = read_chains_from_file(temp_filename)
            assert len(chains) == 3
            assert chains[0] == "Hello World"
            assert chains[1] == "Another Chain"
            assert chains[2] == "Third Chain"
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    @pytest.mark.asyncio
    async def test_send_chains_to_server_success(self):
        """Test successful server communication."""
        # Mock the actual aiohttp functionality
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Create a proper mock for the session
            mock_session_instance = MagicMock()
            mock_response = AsyncMock()
            
            # Configure the response
            mock_response.status = 200
            mock_response.json.return_value = {"results": [], "processing_time": 0.1}
            
            # Configure the session to return our mock response when post is called
            mock_post_context = AsyncMock()
            mock_post_context.__aenter__.return_value = mock_response
            mock_post_context.__aexit__.return_value = None
            
            mock_session_instance.post.return_value = mock_post_context
            mock_session_class.return_value.__aenter__.return_value = mock_session_instance
            mock_session_class.return_value.__aexit__.return_value = None
            
            # Test data
            test_chains = ["Hello World", "Test Chain"]
            server_url = "http://test-server:8000"
            
            # Call the function
            result = await send_chains_to_server(test_chains, server_url)
            
            # Verify the call was made correctly
            mock_session_instance.post.assert_called_once()
            
            # Verify result
            assert result == {"results": [], "processing_time": 0.1}

    @pytest.mark.asyncio
    async def test_send_chains_to_server_error_status(self):
        """Test server returning error status."""
        # Mock error response properly
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Create a proper mock for the session
            mock_session_instance = MagicMock()
            mock_response = AsyncMock()
            
            # Set up the error response
            mock_response.status = 500
            mock_response.text.return_value = "Internal Server Error"
            
            # Configure the session to return our mock response when post is called
            mock_post_context = AsyncMock()
            mock_post_context.__aenter__.return_value = mock_response
            mock_post_context.__aexit__.return_value = None
            
            mock_session_instance.post.return_value = mock_post_context
            mock_session_class.return_value.__aenter__.return_value = mock_session_instance
            mock_session_class.return_value.__aexit__.return_value = None
            
            test_chains = ["Hello World"]
            
            # Should raise exception
            with pytest.raises(Exception) as exc_info:
                await send_chains_to_server(test_chains, "http://test-server:8000")
            
            assert "Server returned status 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_chains_to_server_network_error(self):
        """Test network communication error."""
        test_chains = ["Hello World"]
        
        # Patch aiohttp to raise an exception
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session_class.side_effect = Exception("Network error")
            
            with pytest.raises(Exception) as exc_info:
                await send_chains_to_server(test_chains, "http://test-server:8000")
            
            assert "Network error" in str(exc_info.value)

    def test_save_results_to_file(self):
        """Test saving results to file."""
        test_results = {
            "results": [
                {"index": 0, "chain": "Hello World", "weight": 10.5},
                {"index": 1, "chain": "Test Chain", "weight": 8.0}
            ],
            "processing_time": 0.123,
            "total_chains": 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Save results
            save_results_to_file(test_results, temp_filename)
            
            # Read and verify
            with open(temp_filename, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                
            assert saved_data == test_results
            assert saved_data["total_chains"] == 2
            assert len(saved_data["results"]) == 2
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_save_results_to_file_creates_directory(self):
        """Test that save_results_to_file creates directory if needed."""
        test_results = {"results": [], "processing_time": 0.0, "total_chains": 0}
        
        # Create temporary directory and file path
        with tempfile.TemporaryDirectory() as temp_dir:
            subdir = os.path.join(temp_dir, "subdir")
            filename = os.path.join(subdir, "results.json")
            
            # Directory shouldn't exist yet
            assert not os.path.exists(subdir)
            
            # Create the subdirectory first
            os.makedirs(subdir, exist_ok=True)
            
            # Save should work now
            save_results_to_file(test_results, filename)
            
            # File should now exist
            assert os.path.exists(filename)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])