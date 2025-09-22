"""
CFGPP AI-Aware Features

AI-aware parsing, compression, hash validation, and extensions.
All features are disabled by default via feature flags.
"""

from .feature_flags import FeatureFlags
from .parser import (
    loads_with_extensions,
    load_with_extensions,
    explain_config,
    query_config,
)
from .compression import CFGPPCompressor
from .hash_validator import BasicHashValidator

__all__ = [
    # Feature Control
    "FeatureFlags",
    # AI-Aware Parser
    "loads_with_extensions",
    "load_with_extensions",
    "explain_config",
    "query_config",
    # AI Components
    "CFGPPCompressor",
    "BasicHashValidator",
]
