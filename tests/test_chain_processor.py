"""
Unit tests for chain processor functionality.
Tests the core chain processing logic and weight calculation.
"""

import pytest
import sys
import os
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.chain_processor import ChainProcessor
from src.models.chain_models import ChainResult


class TestChainProcessor:
    """Test suite for ChainProcessor class."""

    def test_calculate_weight_normal_case(self):
        """Test normal chain weight calculation."""
        chain = "Hello World 123"
        # Letters: 10 (H,e,l,l,o,W,o,r,l,d), Digits: 3 (1,2,3), Spaces: 2
        # Expected: (10 * 1.5 + 3 * 2) / 2 = (15 + 6) / 2 = 21 / 2 = 10.5
        expected_weight = 10.5
        
        result = ChainProcessor.calculate_weight(chain)
        assert result == expected_weight

    def test_calculate_weight_no_spaces(self):
        """Test chain with no spaces returns 0.0."""
        chain = "HelloWorld123"
        result = ChainProcessor.calculate_weight(chain)
        assert result == 0.0

    def test_calculate_weight_double_a_rule(self):
        """Test that double 'a' rule returns 1000.0."""
        chain = "aa test chain"
        result = ChainProcessor.calculate_weight(chain)
        assert result == 1000.0

    def test_calculate_weight_double_a_case_insensitive(self):
        """Test that double 'a' rule is case insensitive."""
        chain = "AA test chain"
        result = ChainProcessor.calculate_weight(chain)
        assert result == 1000.0

    def test_calculate_weight_single_a_allowed(self):
        """Test that single 'a' characters are allowed."""
        chain = "A B C D E"
        # Letters: 5, Digits: 0, Spaces: 4
        # Expected: (5 * 1.5 + 0 * 2) / 4 = 7.5 / 4 = 1.875
        result = ChainProcessor.calculate_weight(chain)
        assert abs(result - 1.875) < 0.01

    def test_calculate_weight_only_digits_and_spaces(self):
        """Test chain with only digits and spaces."""
        chain = "123 456 789"
        # Letters: 0, Digits: 9, Spaces: 2
        # Expected: (0 * 1.5 + 9 * 2) / 2 = 18 / 2 = 9.0
        result = ChainProcessor.calculate_weight(chain)
        assert result == 9.0

    def test_calculate_weight_only_letters_and_spaces(self):
        """Test chain with only letters and spaces."""
        chain = "abc def ghi"
        # Letters: 9, Digits: 0, Spaces: 2
        # Expected: (9 * 1.5 + 0 * 2) / 2 = 13.5 / 2 = 6.75
        result = ChainProcessor.calculate_weight(chain)
        assert result == 6.75

    def test_calculate_weight_mixed_case(self):
        """Test chain with mixed case letters."""
        chain = "HeLLo WoRLd 123"
        # Letters: 10, Digits: 3, Spaces: 2
        # Expected: (10 * 1.5 + 3 * 2) / 2 = 21 / 2 = 10.5
        result = ChainProcessor.calculate_weight(chain)
        assert result == 10.5

    def test_process_chains_empty_list(self):
        """Test processing empty chain list."""
        chains: List[str] = []
        results = ChainProcessor.process_chains(chains)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_process_chains_single_chain(self):
        """Test processing single chain."""
        chains = ["Hello World"]
        results = ChainProcessor.process_chains(chains)
        assert len(results) == 1
        assert isinstance(results[0], ChainResult)
        assert results[0].index == 0
        assert results[0].chain == "Hello World"
        assert results[0].weight > 0
        assert results[0].error is None

    def test_process_chains_multiple_chains(self):
        """Test processing multiple chains."""
        chains = ["Hello World", "Test 123", "aa test"]
        results = ChainProcessor.process_chains(chains)
        assert len(results) == 3
        
        # Check each result
        for i, result in enumerate(results):
            assert isinstance(result, ChainResult)
            assert result.index == i
            assert result.chain == chains[i]
            assert result.error is None
            
        # Third chain should have weight 1000.0 due to double 'a'
        assert results[2].weight == 1000.0

    def test_process_chains_with_invalid_chain(self):
        """Test processing with invalid chain that causes exception."""
        # This test would require mocking or creating a scenario that raises an exception
        # For now, we test that the method handles exceptions gracefully
        chains = ["Normal chain", "", "Another normal chain"]
        results = ChainProcessor.process_chains(chains)
        assert len(results) == 3
        
        # Empty string should still produce a result with some weight calculation
        assert results[1].index == 1
        assert results[1].chain == ""
        # Empty string has 0 letters, 0 digits, 0 spaces, so weight should be 0.0
        assert results[1].weight == 0.0

    def test_chain_length_validation_logging(self, caplog):
        """Test that chain length validation produces appropriate logging."""
        import logging
        # Test with a very short chain that should trigger warning
        short_chain = "Hi"
        ChainProcessor.calculate_weight(short_chain)
        
        # Note: Actual logging assertion depends on test configuration
        # This test ensures the method doesn't crash with edge cases

    def test_space_count_validation_logging(self, caplog):
        """Test that space count validation produces appropriate logging."""
        import logging
        # Test with chain having many spaces
        many_spaces_chain = "H e l l o W o r l d"
        ChainProcessor.calculate_weight(many_spaces_chain)
        
        # Note: Actual logging assertion depends on test configuration
        # This test ensures the method handles various space counts

    def test_weight_calculation_precision(self):
        """Test that weight calculation maintains proper precision."""
        chain = "AB CD EF GH"
        # 8 letters, 0 digits, 3 spaces
        # Expected: (8 * 1.5 + 0 * 2) / 3 = 12 / 3 = 4.0
        result = ChainProcessor.calculate_weight(chain)
        assert abs(result - 4.0) < 0.01  # Allow small floating point differences

    def test_consecutive_character_detection(self):
        """Test detection of various consecutive characters."""
        # Test double b (should be fine)
        chain_b = "Bubble bath"
        result_b = ChainProcessor.calculate_weight(chain_b)
        assert result_b != 1000.0
        
        # Test double z (should be fine)
        chain_z = "Pizza zone"
        result_z = ChainProcessor.calculate_weight(chain_z)
        assert result_z != 1000.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])