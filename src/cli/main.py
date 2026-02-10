"""
Enhanced Chain Weighting Client CLI
Professional command-line interface with advanced features and configurability.
"""

import argparse
import asyncio
import logging
import os
import time
from typing import Optional
import aiohttp
import json

from ..utils.helpers import ChainGenerator, FileManager
from ..config.environment import get_config

config = get_config()
config.create_directories()

logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format=config.logging.format,
    handlers=[
        logging.FileHandler(os.path.join(config.paths.logs_directory, config.logging.client_log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChainWeightingClient:
    """Enhanced client for chain weighting analysis with advanced features."""

    def __init__(self, server_url: str = None):
        if server_url is None:
            server_url = f"http://{config.server.host}:{config.server.port}"
        self.server_url = server_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def process_chains(self, chains: list, timeout: int = 300) -> dict:
        """
        Send chains to server for processing.

        Args:
            chains: List of chain strings
            timeout: Request timeout in seconds

        Returns:
            Server response dictionary
        """
        if not self.session:
            raise RuntimeError("Client session not initialized")

        url = f"{self.server_url}/api/v1/process-chains"
        payload = {"chains": chains}

        logger.info(f"Sending {len(chains)} chains to {url}")
        start_time = time.time()

        try:
            async with self.session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    processing_time = time.time() - start_time
                    logger.info(f"Server response received in {processing_time:.3f} seconds")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Server error {response.status}: {error_text}")
                    raise Exception(f"Server returned status {response.status}: {error_text}")
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {timeout} seconds")
            raise Exception(f"Request timeout after {timeout} seconds")
        except Exception as e:
            logger.error(f"Communication error: {str(e)}")
            raise

def save_results_detailed(results: dict, filename: str) -> None:
    """
    Save processing results with enhanced formatting and metadata.

    Args:
        results: Results dictionary from server
        filename: Output filename
    """
    logger.info(f"Saving detailed results to {filename}")

    enhanced_results = {
        "metadata": {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_chains": len(results.get("results", [])),
            "processing_time": results.get("processing_time", 0),
            "api_version": results.get("api_version", "2.0.0")
        },
        "results": results
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(enhanced_results, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved successfully to {filename}")

async def main_async():
    """Enhanced main client function with advanced options."""
    parser = argparse.ArgumentParser(
        description="Enhanced Chain Weighting Analysis Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            python -m src.cli.main --count 1000000
            python -m src.cli.main --input data/input/custom_chains.txt --output data/output/results.json
            python -m src.cli.main --generate-only --count 50000
            python -m src.cli.main --server http://production-server.com:8000 --count 10000
        """
    )

    parser.add_argument("--count", type=int, default=1000000,
                       help="Number of chains to generate (default: 1,000,000)")
    parser.add_argument("--input", type=str, default=os.path.join(config.paths.input_directory, "chains.txt"),
                       help=f"Input file name (default: {os.path.join(config.paths.input_directory, 'chains.txt')})")
    parser.add_argument("--output", type=str, default=os.path.join(config.paths.output_directory, "results.json"),
                       help=f"Output file name (default: {os.path.join(config.paths.output_directory, 'results.json')})")
    parser.add_argument("--server", type=str, default=f"http://{config.server.host}:{config.server.port}",
                       help=f"Server URL (default: http://{config.server.host}:{config.server.port})")
    parser.add_argument("--generate-only", action="store_true",
                       help="Only generate chains file, don't process")
    parser.add_argument("--timeout", type=int, default=config.processing.timeout_seconds,
                       help=f"Server request timeout in seconds (default: {config.processing.timeout_seconds})")
    parser.add_argument("--batch-size", type=int, default=config.processing.default_batch_size,
                       help=f"Process chains in batches (default: {config.processing.default_batch_size})")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    total_start_time = time.time()
    logger.info("=== Enhanced Chain Weighting Client Started ===")
    logger.info(f"Configuration: {args.count} chains, server: {args.server}")

    try:
        os.makedirs(os.path.dirname(args.input), exist_ok=True)
        os.makedirs(os.path.dirname(args.output), exist_ok=True)

        logger.info("Step 1: Generating chains...")
        chains = ChainGenerator.generate_multiple_chains(args.count)
        FileManager.write_chains_to_file(chains, args.input)

        if args.generate_only:
            logger.info("Chain generation completed. Exiting.")
            return

        logger.info("Step 2: Processing chains with server...")
        all_results = []

        async with ChainWeightingClient(args.server) as client:
            for i in range(0, len(chains), args.batch_size):
                batch = chains[i:i + args.batch_size]
                batch_num = (i // args.batch_size) + 1
                total_batches = (len(chains) + args.batch_size - 1) // args.batch_size

                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chains)")

                batch_results = await client.process_chains(batch, args.timeout)
                all_results.extend(batch_results.get("results", []))

                if batch_num % 10 == 0 or batch_num == total_batches:
                    progress = (batch_num / total_batches) * 100
                    logger.info(f"Progress: {progress:.1f}% ({batch_num}/{total_batches} batches)")

        final_results = {
            "results": all_results,
            "processing_time": time.time() - total_start_time,
            "total_chains": len(all_results),
            "api_version": "2.0.0"
        }

        logger.info("Step 3: Saving results...")
        save_results_detailed(final_results, args.output)

        total_time = time.time() - total_start_time
        logger.info("=== Processing Complete ===")
        logger.info(f"Total chains processed: {len(all_results)}")
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        logger.info(f"Average time per chain: {(total_time/len(all_results))*1000:.2f} ms")
        logger.info(f"Results saved to: {args.output}")

    except Exception as e:
        logger.error(f"Client operation failed: {str(e)}")
        raise

def main():
    """Entry point for the CLI application."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
