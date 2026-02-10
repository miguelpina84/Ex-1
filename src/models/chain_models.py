"""
Data models for chain processing system.
Defines the structure for requests, responses, and internal data.
Using dataclasses (built-in) instead of Pydantic.
"""

from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ChainRequest:
    """Request model for chain processing"""
    chains: List[str]

@dataclass
class ChainResult:
    """Individual chain processing result"""
    index: int
    chain: str
    weight: float
    error: Optional[str] = None

@dataclass
class ChainResponse:
    """Response model for chain processing results"""
    results: List[ChainResult]
    processing_time: Optional[float] = None
    total_chains: Optional[int] = None

@dataclass
class HealthCheck:
    """Health check response model"""
    status: str
    service: str
    version: str = "1.0.0"