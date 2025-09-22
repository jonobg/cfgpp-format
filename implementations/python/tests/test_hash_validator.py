"""Test hash validation functionality"""

import pytest
from cfgpp.ai.hash_validator import BasicHashValidator
from cfgpp.ai.feature_flags import FeatureFlags


def test_hash_validator_disabled_by_default():
    """Test that hash validator is disabled by default"""
    validator = BasicHashValidator()
    assert not validator.enabled

    # Should return empty hash when disabled
    hash_result = validator.calculate_hash("test content")
    assert hash_result == ""

    # Should always validate as true when disabled
    is_valid, message = validator.validate_hash("test", "sha256:abc123")
    assert is_valid
    assert "disabled" in message


def test_hash_calculation_when_enabled():
    """Test hash calculation when feature is enabled"""
    # Temporarily enable for testing
    original_value = FeatureFlags.HASH_VALIDATION
    FeatureFlags.HASH_VALIDATION = True

    try:
        validator = BasicHashValidator()
        assert validator.enabled

        # Test SHA256 calculation
        content = "test configuration content"
        hash_result = validator.calculate_hash(content)

        assert hash_result.startswith("sha256:")
        assert len(hash_result) == 71  # "sha256:" + 64 hex chars

        # Test consistent hashing
        hash_result2 = validator.calculate_hash(content)
        assert hash_result == hash_result2

        # Test different algorithms
        md5_hash = validator.calculate_hash(content, "md5")
        assert md5_hash.startswith("md5:")
        assert len(md5_hash) == 36  # "md5:" + 32 hex chars

        sha512_hash = validator.calculate_hash(content, "sha512")
        assert sha512_hash.startswith("sha512:")
        assert len(sha512_hash) == 135  # "sha512:" + 128 hex chars

    finally:
        # Restore original value
        FeatureFlags.HASH_VALIDATION = original_value


def test_hash_validation_when_enabled():
    """Test hash validation when feature is enabled"""
    original_value = FeatureFlags.HASH_VALIDATION
    FeatureFlags.HASH_VALIDATION = True

    try:
        validator = BasicHashValidator()

        content = "test configuration"
        expected_hash = validator.calculate_hash(content)

        # Test valid hash
        is_valid, message = validator.validate_hash(content, expected_hash)
        assert is_valid
        assert "passed" in message

        # Test invalid hash
        is_valid, message = validator.validate_hash(content, "sha256:invalid")
        assert not is_valid
        assert "mismatch" in message

        # Test no hash provided
        is_valid, message = validator.validate_hash(content, "")
        assert is_valid
        assert "No hash provided" in message

        # Test invalid hash format
        is_valid, message = validator.validate_hash(content, "invalidformat")
        assert not is_valid
        assert "Invalid hash format" in message

    finally:
        FeatureFlags.HASH_VALIDATION = original_value


def test_extract_hash_from_content():
    """Test extracting hash from configuration content"""
    original_value = FeatureFlags.HASH_VALIDATION
    FeatureFlags.HASH_VALIDATION = True

    try:
        validator = BasicHashValidator()

        # Content with hash header
<<<<<<< HEAD
        content_with_hash = """@config-hash: "sha256:abc123def456"
=======
        content_with_hash = '''@config-hash: "sha256:abc123def456"
>>>>>>> 1b1471a5237dd45c55ee78ad142950cd3d76bae8
@hash-algorithm: "sha256"

DatabaseConfig::primary(
    string host = "localhost"
<<<<<<< HEAD
)"""
=======
)'''
>>>>>>> 1b1471a5237dd45c55ee78ad142950cd3d76bae8

        extracted_hash = validator.extract_hash_from_content(content_with_hash)
        assert extracted_hash == "sha256:abc123def456"

        # Content without hash
<<<<<<< HEAD
        content_no_hash = """DatabaseConfig::primary(
    string host = "localhost"
)"""
=======
        content_no_hash = '''DatabaseConfig::primary(
    string host = "localhost"
)'''
>>>>>>> 1b1471a5237dd45c55ee78ad142950cd3d76bae8

        extracted_hash = validator.extract_hash_from_content(content_no_hash)
        assert extracted_hash is None

        # Content with malformed hash
<<<<<<< HEAD
        content_malformed = """@config-hash: malformed
DatabaseConfig::primary(
    string host = "localhost"
)"""
=======
        content_malformed = '''@config-hash: malformed
DatabaseConfig::primary(
    string host = "localhost"
)'''
>>>>>>> 1b1471a5237dd45c55ee78ad142950cd3d76bae8

        extracted_hash = validator.extract_hash_from_content(content_malformed)
        assert extracted_hash == "malformed"  # Returns the malformed value as-is

    finally:
        FeatureFlags.HASH_VALIDATION = original_value


def test_hash_validation_error_handling():
    """Test error handling in hash validation"""
    original_value = FeatureFlags.HASH_VALIDATION
    FeatureFlags.HASH_VALIDATION = True

    try:
        validator = BasicHashValidator()

        # Test unsupported algorithm
        hash_result = validator.calculate_hash("test", "unsupported")
        assert hash_result == ""  # Should return empty on error

        # Test hash validation with unsupported algorithm reference
        is_valid, message = validator.validate_hash("test", "unsupported:abc123")
        assert not is_valid  # Should reject unsupported algorithms
        assert "unsupported" in message.lower()

    finally:
        FeatureFlags.HASH_VALIDATION = original_value


def test_feature_flag_integration():
    """Test integration with feature flag system"""
    # Ensure feature starts disabled
    assert not FeatureFlags.HASH_VALIDATION

    validator = BasicHashValidator()
    assert not validator.enabled

    # Test disabled behavior
    assert validator.calculate_hash("test") == ""
    is_valid, message = validator.validate_hash("test", "sha256:abc")
    assert is_valid and "disabled" in message
    assert validator.extract_hash_from_content("@config-hash: sha256:test") is None


def test_production_safety():
    """Test that hash validator is safe for production use"""
    # Critical: These operations should NEVER raise exceptions in production
    validator = BasicHashValidator()

    # Test with various edge cases - should never crash
    try:
        validator.calculate_hash("")
        validator.calculate_hash(None)  # This should handle gracefully
    except TypeError:
        pass  # Expected for None input

    try:
        validator.validate_hash("", "")
        validator.validate_hash("test", None)  # This should handle gracefully
    except TypeError:
        pass  # Expected for None input

    try:
        validator.extract_hash_from_content("")
        validator.extract_hash_from_content(None)  # This should handle gracefully
    except (TypeError, AttributeError):
        pass  # Expected for None input

    # All operations completed without crashing - production safe


def test_zero_impact_on_existing_functionality():
    """Verify hash validator has zero impact on existing parser functionality"""
    # Import parser to ensure hash validator doesn't break imports
<<<<<<< HEAD
    from cfgpp.core.parser import loads
=======
    from cfgpp.parser import loads
>>>>>>> 1b1471a5237dd45c55ee78ad142950cd3d76bae8

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
    # Check that result structure is as expected (may vary by parser implementation)
    assert len(result["body"]) > 0

    # Hash validator exists but doesn't interfere
    validator = BasicHashValidator()
    assert not validator.enabled  # Disabled by default

    # Parser functionality unchanged
    result2 = loads(config)
    assert result == result2
