"""
Utility functions for chain generation and file operations.
Contains helper functions for data manipulation and I/O operations.
"""

import logging
import random
import string
from typing import List
from src.config.environment import get_config

config = get_config()
logger = logging.getLogger(__name__)

class ChainGenerator:
    """Handles generation of random character chains according to specifications."""
    
    @staticmethod
    def generate_single_chain() -> str:
        """
        Generate a single random chain according to specifications:
        - Length between configured min-max characters
        - Contains only a-zA-Z0-9 and spaces
        - Has configured min-max non-consecutive spaces
        - No spaces at beginning or end
        
        Returns:
            Generated chain string
        """

        allowed_chars = string.ascii_letters + string.digits
        length = random.randint(config.processing.min_chain_length, config.processing.max_chain_length)
        space_count = random.randint(config.processing.min_spaces, config.processing.max_spaces)
        char_count = length - space_count
        chain_chars = [random.choice(allowed_chars) for _ in range(char_count)]
        positions = []
        max_attempts = 100
        attempts = 0
        
        while len(positions) < space_count and attempts < max_attempts:
            pos = random.randint(1, len(chain_chars) - 1)

            if pos not in positions and (pos - 1) not in positions and (pos + 1) not in positions:
                positions.append(pos)
            attempts += 1
        
        for pos in sorted(positions, reverse=True):
            chain_chars.insert(pos, ' ')
        
        return ''.join(chain_chars)
    
    @classmethod
    def generate_multiple_chains(cls, count: int) -> List[str]:
        """
        Generate multiple chains.
        
        Args:
            count: Number of chains to generate
            
        Returns:
            List of generated chain strings
        """
        logger.info(f"Generating {count} chains")
        return [cls.generate_single_chain() for _ in range(count)]

class FileManager:
    """Handles file operations for chain data."""
    
    @staticmethod
    def write_chains_to_file(chains: List[str], filename: str) -> None:
        """
        Write chains to file, one per line.
        
        Args:
            chains: List of chain strings
            filename: Output filename (will be created in configured output directory)
        """
        import os

        output_dir = os.path.dirname(filename) or config.paths.output_directory
        os.makedirs(output_dir, exist_ok=True)
        
        if not filename:
            filename = os.path.join(config.paths.output_directory, "chains.txt")
        
        logger.info(f"Writing {len(chains)} chains to {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            for chain in chains:
                f.write(chain + '\n')
    
    @staticmethod
    def read_chains_from_file(filename: str) -> List[str]:
        """
        Read chains from file.
        
        Args:
            filename: Input filename (will look in configured input directory if relative path)
            
        Returns:
            List of chain strings
        """
        import os
        
        if not os.path.isabs(filename):
            filename = os.path.join(config.paths.input_directory, filename)
        
        logger.info(f"Reading chains from {filename}")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                chains = [line.strip() for line in f if line.strip()]
            logger.info(f"Read {len(chains)} chains from file")
            return chains
        except FileNotFoundError:
            logger.error(f"File {filename} not found")
            raise