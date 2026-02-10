"""
Package initialization for the core module.
Contains shared utilities and base configurations.
"""

import logging
import os

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure package-level logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

__version__ = "2.0.0"
__author__ = "Chain Analysis Team"