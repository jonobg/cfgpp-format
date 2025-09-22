"""
Hash validation for configuration integrity
Phase 1: Read-only validation that never affects parsing

# REASONING: Hash validation enables configuration integrity verification and tamper detection for validation workflows.
# Validation workflows require hash validation for configuration integrity verification and tamper detection in validation workflows.
# Hash validation supports configuration integrity verification, tamper detection, and validation coordination while enabling
# comprehensive integrity strategies and systematic configuration security workflows.
"""

import hashlib
import logging
from typing import Optional, Tuple

from .feature_flags import FeatureFlags


class BasicHashValidator:
    """
    Basic hash validation for configuration files

    Phase 1 Implementation:
    - Calculate hashes but don't modify files
    - Validate hashes but don't error on failure
    - All functionality disabled by default via feature flags
    """

    def __init__(self):
        self.enabled = FeatureFlags.is_enabled("HASH_VALIDATION")
        self.logger = logging.getLogger(__name__)

    def calculate_hash(self, content: str, algorithm: str = "sha256") -> str:
        """
        Calculate hash of configuration content

        Args:
            content: Configuration file content
            algorithm: Hash algorithm (sha256, sha512, md5)

        Returns:
            Hash string in format "algorithm:hexdigest" or empty if disabled
        """
        if not self.enabled:
            return ""  # Disabled by default

        try:
            if algorithm == "sha256":
                hasher = hashlib.sha256()
            elif algorithm == "sha512":
                hasher = hashlib.sha512()
            elif algorithm == "md5":
                hasher = hashlib.md5()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")

            hasher.update(content.encode("utf-8"))
            return f"{algorithm}:{hasher.hexdigest()}"

        except Exception as e:
            self.logger.warning(f"Hash calculation failed: {e}")
            return ""

    def validate_hash(self, content: str, expected_hash: str) -> Tuple[bool, str]:
        """
        Validate configuration hash

        Args:
            content: Configuration content to validate
            expected_hash: Expected hash in format "algorithm:hexdigest"

        Returns:
            Tuple of (is_valid, message)
        """
        if not self.enabled:
            return True, "Hash validation disabled"

        try:
            if not expected_hash:
                return True, "No hash provided"

            # Extract algorithm from hash
            if ":" not in expected_hash:
                return False, "Invalid hash format"

            algorithm, expected_hex = expected_hash.split(":", 1)
            calculated_hash = self.calculate_hash(content, algorithm)

            if calculated_hash == expected_hash:
                return True, "Hash validation passed"
            else:
                return (
                    False,
                    f"Hash mismatch: expected {expected_hash}, got {calculated_hash}",
                )

        except Exception as e:
            self.logger.error(f"Hash validation error: {e}")
            # For unsupported algorithms in validation, return False
            if "Unsupported hash algorithm" in str(e):
                return False, f"Unsupported algorithm: {e}"
            return True, f"Validation error (allowing): {e}"

    def extract_hash_from_content(self, content: str) -> Optional[str]:
        """
        Extract hash from configuration content

        Looks for @config-hash: "algorithm:hexdigest" pattern
        """
        if not self.enabled:
            return None

        lines = content.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("@config-hash:"):
                # Extract hash value from @config-hash: "sha256:abc123"
                # Find the quoted value after the colon
                colon_pos = stripped.find(":", len("@config-hash"))
                if colon_pos != -1:
                    value_part = stripped[colon_pos + 1 :].strip()
                    if value_part.startswith('"') and value_part.endswith('"'):
                        return value_part[1:-1]  # Remove quotes
                    else:
                        return value_part

        return None
