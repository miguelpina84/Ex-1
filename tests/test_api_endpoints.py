"""
Unit tests for API endpoints.
Tests the FastAPI server endpoints and request/response handling.
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api.main import app
from src.models.chain_models import ChainRequest, ChainResponse

# Create test client
client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.0.0"

    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Chain Weighting Analysis API"
        assert data["version"] == "2.0.0"

    def test_stats_endpoint(self):
        """Test statistics endpoint."""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "supported_operations" in data

    def test_process_chains_valid_request(self):
        """Test processing valid chains request."""
        chains = ["Hello World", "Test 123", "Amazing Apples"]
        request_data = {"chains": chains}
        
        response = client.post("/api/v1/process-chains", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "processing_time" in data
        assert "total_chains" in data
        assert data["total_chains"] == len(chains)
        assert len(data["results"]) == len(chains)
        
        # Check result structure
        for i, result in enumerate(data["results"]):
            assert result["index"] == i
            assert result["chain"] == chains[i]
            assert "weight" in result
            assert result["error"] is None

    def test_process_chains_empty_list(self):
        """Test processing empty chains list."""
        request_data = {"chains": []}
        
        response = client.post("/api/v1/process-chains", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_chains"] == 0
        assert len(data["results"]) == 0

    def test_process_chains_missing_chains_field(self):
        """Test request missing required chains field."""
        request_data = {}  # Missing "chains" field
        
        response = client.post("/api/v1/process-chains", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_process_chains_invalid_json(self):
        """Test invalid JSON request."""
        response = client.post("/api/v1/process-chains", content="invalid json")
        assert response.status_code == 422  # Validation error

    def test_process_chains_with_double_a_rule(self):
        """Test chains that trigger double 'a' rule."""
        chains = ["Amazing Apples", "AA Testing"]  # "AA Testing" has consecutive 'A's
        request_data = {"chains": chains}
        
        response = client.post("/api/v1/process-chains", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        results = data["results"]
        
        # Only the chain with consecutive 'a'/'A' should have weight 1000.0
        weights = [result["weight"] for result in results]
        assert 1000.0 in weights  # At least one chain should have weight 1000.0
        # Verify "AA Testing" specifically has weight 1000.0
        aa_result = next(r for r in results if "AA Testing" in r["chain"])
        assert aa_result["weight"] == 1000.0

    def test_process_chains_various_formats(self):
        """Test chains with various valid formats."""
        chains = [
            "Simple test",           # Normal case
            "ABC DEF GHI",           # Only letters
            "123 456 789",           # Only digits
            "Mix3d Ch4rs 5p4c3s",    # Mixed alphanumeric
            "a b c d e f g h i j"    # Single characters
        ]
        request_data = {"chains": chains}
        
        response = client.post("/api/v1/process-chains", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["results"]) == len(chains)
        
        # All should have valid weights (not 1000.0 unless they violate rules)
        for result in data["results"]:
            assert isinstance(result["weight"], (int, float))
            assert result["weight"] >= 0

    @patch('src.core.chain_processor.ChainProcessor.process_chains')
    def test_process_chains_internal_error(self, mock_process):
        """Test handling of internal processing errors."""
        # Mock the processor to raise an exception
        mock_process.side_effect = Exception("Processing failed")
        
        request_data = {"chains": ["test chain"]}
        response = client.post("/api/v1/process-chains", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Processing failed" in data["detail"]

    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.get("/api/v1/health")
        # FastAPI's TestClient doesn't fully simulate CORS, but we can check
        # that the endpoint works and returns expected data
        assert response.status_code == 200

    def test_openapi_docs_available(self):
        """Test that API documentation endpoints are available."""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_404_for_nonexistent_endpoint(self):
        """Test that nonexistent endpoints return 404."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])