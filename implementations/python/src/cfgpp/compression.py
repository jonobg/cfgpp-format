"""
Basic compression library for CFGPP configurations
Phase 1: Standalone compression that doesn't integrate with parsing yet
"""

import gzip
import logging
import time
from typing import Dict, Optional, Union

from .features import FeatureFlags


class CFGPPCompressor:
    """
    Basic compression for configuration files

    Phase 1 Implementation:
    - Compress/decompress content but don't integrate with parser yet
    - Support multiple algorithms for different use cases
    - All functionality disabled by default via feature flags
    """

    def __init__(self):
        self.enabled = FeatureFlags.is_enabled("COMPRESSION")
        self.logger = logging.getLogger(__name__)

        # Algorithm preferences based on use case
        self.algorithm_map = {
            "ai-communication": "gzip",  # Fast and widely supported
            "storage": "gzip",  # Good compression ratio
            "network": "gzip",  # Standard network compression
            "iot": "gzip",  # Broad compatibility
            "default": "gzip",  # Safe fallback
        }

    def compress(
        self, content: str, algorithm: str = "gzip", target: str = "default"
    ) -> bytes:
        """
        Compress configuration content

        Args:
            content: Configuration content to compress
            algorithm: Compression algorithm (gzip, lz4, zstd)
            target: Target use case (ai-communication, storage, network, iot)

        Returns:
            Compressed bytes or original content encoded if disabled
        """
        if not self.enabled:
            return content.encode("utf-8")  # Pass-through when disabled

        # Auto-select algorithm based on target if not specified explicitly
        if algorithm == "auto":
            algorithm = self.algorithm_map.get(target, "gzip")

        try:
            content_bytes = content.encode("utf-8")

            if algorithm == "gzip":
                return gzip.compress(content_bytes, compresslevel=6)
            elif algorithm == "lz4":
                # Try to import lz4, fallback to gzip if not available
                try:
                    import lz4.frame

                    return lz4.frame.compress(content_bytes)
                except ImportError:
                    self.logger.warning("LZ4 not available, falling back to gzip")
                    return gzip.compress(content_bytes, compresslevel=1)
            elif algorithm == "zstd":
                # Try to import zstd, fallback to gzip if not available
                try:
                    import zstandard as zstd

                    compressor = zstd.ZstdCompressor(level=3)
                    return compressor.compress(content_bytes)
                except ImportError:
                    self.logger.warning("ZSTD not available, falling back to gzip")
                    return gzip.compress(content_bytes, compresslevel=6)
            else:
                raise ValueError(f"Unsupported compression algorithm: {algorithm}")

        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            return content.encode("utf-8")  # Return uncompressed on error

    def decompress(self, compressed_data: bytes, algorithm: str = "gzip") -> str:
        """
        Decompress configuration content

        Args:
            compressed_data: Compressed bytes to decompress
            algorithm: Algorithm used for compression

        Returns:
            Decompressed content or original data decoded if disabled
        """
        if not self.enabled:
            try:
                return compressed_data.decode("utf-8")
            except UnicodeDecodeError:
                # If it's actually compressed but feature is disabled, try gzip anyway
                try:
                    return gzip.decompress(compressed_data).decode("utf-8")
                except:
                    return "DECOMPRESSION_FAILED"

        try:
            if algorithm == "gzip":
                return gzip.decompress(compressed_data).decode("utf-8")
            elif algorithm == "lz4":
                try:
                    import lz4.frame

                    return lz4.frame.decompress(compressed_data).decode("utf-8")
                except ImportError:
                    # Try gzip as fallback
                    return gzip.decompress(compressed_data).decode("utf-8")
            elif algorithm == "zstd":
                try:
                    import zstandard as zstd

                    decompressor = zstd.ZstdDecompressor()
                    return decompressor.decompress(compressed_data).decode("utf-8")
                except ImportError:
                    # Try gzip as fallback
                    return gzip.decompress(compressed_data).decode("utf-8")
            else:
                raise ValueError(f"Unsupported compression algorithm: {algorithm}")

        except Exception as e:
            self.logger.error(f"Decompression failed: {e}")
            return "DECOMPRESSION_ERROR"

    def compress_with_metadata(self, content: str, target: str = "default") -> Dict:
        """
        Compress content and return with metadata for AI systems

        Args:
            content: Configuration content to compress
            target: Target use case for algorithm selection

        Returns:
            Dictionary with compressed data and metadata
        """
        if not self.enabled:
            return {
                "compressed": False,
                "algorithm": "none",
                "original_size": len(content),
                "compressed_size": len(content),
                "compression_ratio": 1.0,
                "data": content.encode("utf-8"),
            }

        algorithm = self.algorithm_map.get(target, "gzip")

        start_time = time.time()
        compressed_data = self.compress(content, algorithm, target)
        compression_time = time.time() - start_time

        original_size = len(content.encode("utf-8"))
        compressed_size = len(compressed_data)
        compression_ratio = (
            compressed_size / original_size if original_size > 0 else 1.0
        )

        return {
            "compressed": True,
            "algorithm": algorithm,
            "target": target,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": compression_ratio,
            "compression_time": compression_time,
            "data": compressed_data,
        }

    def get_algorithm_info(self) -> Dict[str, Dict]:
        """
        Get information about available compression algorithms

        Returns:
            Dictionary with algorithm availability and characteristics
        """
        info = {
            "gzip": {
                "available": True,
                "use_case": "General purpose, widely supported",
                "speed": "Medium",
                "compression": "Good",
            }
        }

        # Check LZ4 availability
        try:
            import lz4.frame

            info["lz4"] = {
                "available": True,
                "use_case": "Real-time AI communication",
                "speed": "Very Fast",
                "compression": "Moderate",
            }
        except ImportError:
            info["lz4"] = {
                "available": False,
                "install": "pip install lz4",
                "use_case": "Real-time AI communication",
                "speed": "Very Fast",
                "compression": "Moderate",
            }

        # Check ZSTD availability
        try:
            import zstandard

            info["zstd"] = {
                "available": True,
                "use_case": "Storage and balanced performance",
                "speed": "Fast",
                "compression": "Excellent",
            }
        except ImportError:
            info["zstd"] = {
                "available": False,
                "install": "pip install zstandard",
                "use_case": "Storage and balanced performance",
                "speed": "Fast",
                "compression": "Excellent",
            }

        return info
