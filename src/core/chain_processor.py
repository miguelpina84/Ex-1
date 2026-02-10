"""
Core chain processing logic with weighting calculation.
This module contains the business logic for chain analysis.
"""

import logging
from typing import List
from src.models.chain_models import ChainResult
from src.config.environment import get_config

config = get_config()
logger = logging.getLogger(__name__)

class ChainProcessor:
    """Handles chain processing and weight calculation logic."""
    
    @staticmethod
    def calculate_weight(chain: str) -> float:
        """
        Calculate the weight metric for a chain.
        
        Formula: (letter_count * 1.5 + digit_count * 2) / space_count
        
        Args:
            chain: String to analyze
            
        Returns:
            Weight value or 1000.0 if double 'a' rule is violated
        """

        if not (config.processing.min_chain_length <= len(chain) <= config.processing.max_chain_length):
            logger.warning(f"Chain length {len(chain)} outside configured range "
                        f"[{config.processing.min_chain_length}, {config.processing.max_chain_length}]")

        lower_chain = chain.lower()
        if 'aa' in lower_chain:
            logger.warning(f"Double 'a' rule detected >> '{chain}'")
            return 1000.0
        
        letter_count = sum(1 for c in chain if c.isalpha())
        digit_count = sum(1 for c in chain if c.isdigit())
        space_count = chain.count(' ')

        if not (config.processing.min_spaces <= space_count <= config.processing.max_spaces):
            logger.warning(f"Space count {space_count} outside configured range "
                        f"[{config.processing.min_spaces}, {config.processing.max_spaces}]")
        
        if space_count == 0:
            return 0.0 
        
        weight = (letter_count * 1.5 + digit_count * 2) / space_count
        return round(weight, 2)
    
    @classmethod
    def process_chains(cls, chains: List[str]) -> List[ChainResult]:
        """
        Process multiple chains and return their weight metrics.
        
        Args:
            chains: List of chain strings to process
            
        Returns:
            List of ChainResult objects with processing results
        """
        logger.info(f"Processing {len(chains)} chains with batch size {config.processing.default_batch_size}")
        results = []
        
        for i, chain in enumerate(chains):
            try:
                weight = cls.calculate_weight(chain)
                result = ChainResult(
                    index=i,
                    chain=chain,
                    weight=weight
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing chain {i}: {str(e)}")
                result = ChainResult(
                    index=i,
                    chain=chain,
                    weight=0.0,
                    error=str(e)
                )
                results.append(result)
        
        return results