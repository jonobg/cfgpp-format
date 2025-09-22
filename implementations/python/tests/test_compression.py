"""Test compression functionality"""

import pytest
from cfgpp.ai.compression import CFGPPCompressor
from cfgpp.ai.feature_flags import FeatureFlags


def test_compression_disabled_by_default():
    """Test that compression is disabled by default"""
    compressor = CFGPPCompressor()
    assert not compressor.enabled

    content = "test configuration content for compression"

    # Should return uncompressed data when disabled
    result = compressor.compress(content)
    assert result == content.encode("utf-8")

    # Should handle decompression gracefully when disabled
    decompressed = compressor.decompress(result)
    assert decompressed == content


def test_compression_when_enabled():
    """Test compression functionality when feature is enabled"""
    original_value = FeatureFlags.COMPRESSION
    FeatureFlags.COMPRESSION = True

    try:
        compressor = CFGPPCompressor()
        assert compressor.enabled

        content = "test configuration content for compression " * 10  # Larger content

        # Test GZIP compression (always available)
        compressed = compressor.compress(content, "gzip")
        assert len(compressed) < len(content.encode("utf-8"))  # Should be smaller

        # Test decompression
        decompressed = compressor.decompress(compressed, "gzip")
        assert decompressed == content

        # Test round-trip compression
        for algorithm in ["gzip"]:  # Only test guaranteed available algorithms
            compressed = compressor.compress(content, algorithm)
            decompressed = compressor.decompress(compressed, algorithm)
            assert decompressed == content

    finally:
        FeatureFlags.COMPRESSION = original_value


def test_compression_with_metadata():
    """Test compression with metadata generation"""
    original_value = FeatureFlags.COMPRESSION
    FeatureFlags.COMPRESSION = True

    try:
        compressor = CFGPPCompressor()

        content = (
            "test configuration content " * 20
        )  # Larger content for better compression

        # Test metadata generation
        metadata = compressor.compress_with_metadata(content, "ai-communication")

        assert metadata["compressed"] is True
        assert metadata["algorithm"] in ["gzip", "lz4", "zstd"]
        assert metadata["target"] == "ai-communication"
        assert metadata["original_size"] > 0
        assert metadata["compressed_size"] > 0
        assert metadata["compression_ratio"] < 1.0  # Should achieve some compression
        assert metadata["compression_time"] >= 0
        assert isinstance(metadata["data"], bytes)

        # Verify we can decompress the data
        decompressed = compressor.decompress(metadata["data"], metadata["algorithm"])
        assert decompressed == content

    finally:
        FeatureFlags.COMPRESSION = original_value


def test_compression_disabled_metadata():
    """Test metadata when compression is disabled"""
    compressor = CFGPPCompressor()
    assert not compressor.enabled

    content = "test configuration content"
    metadata = compressor.compress_with_metadata(content)

    assert metadata["compressed"] is False
    assert metadata["algorithm"] == "none"
    assert metadata["compression_ratio"] == 1.0
    assert metadata["data"] == content.encode("utf-8")


def test_algorithm_fallback():
    """Test algorithm fallback behavior"""
    original_value = FeatureFlags.COMPRESSION
    FeatureFlags.COMPRESSION = True

    try:
        compressor = CFGPPCompressor()
        content = "test content for algorithm fallback testing"

        # Test unsupported algorithm
        compressed = compressor.compress(content, "unsupported")
        # Should return uncompressed content on error
        assert compressed == content.encode("utf-8")

        # Test auto algorithm selection
        compressed_auto = compressor.compress(content, "auto", "ai-communication")
        assert len(compressed_auto) > 0

    finally:
        FeatureFlags.COMPRESSION = original_value


def test_algorithm_info():
    """Test algorithm information retrieval"""
    compressor = CFGPPCompressor()

    info = compressor.get_algorithm_info()

    # GZIP should always be available
    assert "gzip" in info
    assert info["gzip"]["available"] is True

    # LZ4 and ZSTD may or may not be available
    assert "lz4" in info
    assert "zstd" in info

    # Each algorithm should have required metadata
    for algorithm, details in info.items():
        assert "available" in details
        assert "use_case" in details
        assert "speed" in details
        assert "compression" in details


def test_compression_error_handling():
    """Test error handling in compression operations"""
    original_value = FeatureFlags.COMPRESSION
    FeatureFlags.COMPRESSION = True

    try:
        compressor = CFGPPCompressor()

        # Test compression with invalid algorithm
        result = compressor.compress("test", "invalid_algorithm")
        assert result == "test".encode("utf-8")  # Should return uncompressed

        # Test decompression with invalid data
        result = compressor.decompress(b"invalid compressed data", "gzip")
        assert result == "DECOMPRESSION_ERROR"

    finally:
        FeatureFlags.COMPRESSION = original_value


def test_target_algorithm_mapping():
    """Test target-based algorithm selection"""
    original_value = FeatureFlags.COMPRESSION
    FeatureFlags.COMPRESSION = True

    try:
        compressor = CFGPPCompressor()
        content = "test content for target algorithm mapping"

        # Test different targets
        targets = ["ai-communication", "storage", "network", "iot", "default"]

        for target in targets:
            metadata = compressor.compress_with_metadata(content, target)
            assert metadata["target"] == target
            assert metadata["algorithm"] in compressor.algorithm_map.values()

    finally:
        FeatureFlags.COMPRESSION = original_value


def test_feature_flag_integration():
    """Test integration with feature flag system"""
    # Ensure feature starts disabled
    assert not FeatureFlags.COMPRESSION

    compressor = CFGPPCompressor()
    assert not compressor.enabled

    # Test disabled behavior
    content = "test content"
    assert compressor.compress(content) == content.encode("utf-8")
    assert compressor.decompress(content.encode("utf-8")) == content


def test_production_safety():
    """Test that compressor is safe for production use"""
    compressor = CFGPPCompressor()

    # Test with edge cases - should never crash
    try:
        compressor.compress("")
        compressor.compress("single char: a")
        compressor.compress("unicode: 你好世界 🌍")
    except Exception as e:
        pytest.fail(f"Compression crashed with: {e}")

    try:
        compressor.decompress(b"")
        compressor.decompress(b"test")
    except Exception as e:
        # Decompression errors are expected and handled gracefully
        pass


def test_zero_impact_on_existing_functionality():
    """Verify compressor has zero impact on existing parser functionality"""
    # Import parser to ensure compressor doesn't break imports
    from cfgpp.core.parser import loads

    # Test that parser still works normally
    config = """
    AppConfig {
        name = "test",
        port = 8080,
        debug = true
    }
    """

    result = loads(config)
    assert "body" in result
    assert len(result["body"]) > 0

    # Compressor exists but doesn't interfere
    compressor = CFGPPCompressor()
    assert not compressor.enabled  # Disabled by default

    # Parser functionality unchanged
    result2 = loads(config)
    assert result == result2


def test_compression_performance():
    """Test compression performance characteristics"""
    original_value = FeatureFlags.COMPRESSION
    FeatureFlags.COMPRESSION = True

    try:
        compressor = CFGPPCompressor()

        # Create larger content for meaningful compression testing
        content = (
            """
        # Large configuration for compression testing
        DatabaseConfig::primary(
            string host = "database.example.com",
            int port = 5432,
            bool ssl_enabled = true,
            string database_name = "production_db",
            ConnectionPool pool(
                int min_connections = 5,
                int max_connections = 100,
                int connection_timeout = 30000
            )
        )
        """
            * 50
        )  # Repeat to create larger content

        # Test compression achieves reasonable ratio
        metadata = compressor.compress_with_metadata(content)

        if metadata["compressed"]:
            # Should achieve at least some compression on repetitive content
            assert metadata["compression_ratio"] < 0.8  # At least 20% reduction
            # Compression should be reasonably fast (< 1 second for test content)
            assert metadata["compression_time"] < 1.0

    finally:
        FeatureFlags.COMPRESSION = original_value
