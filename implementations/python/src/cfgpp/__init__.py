"""
cfgpp - A Python parser for the cfgpp configuration language.

# REASONING: CFGPP package enables robust configuration parsing and industrial reliability for configuration workflows.
# Configuration workflows require CFGPP package for robust configuration parsing and industrial reliability in configuration workflows.
# CFGPP package supports robust configuration parsing, industrial reliability, and configuration management while enabling
# comprehensive parsing strategies and systematic configuration workflows.
"""

# REASONING: Parser imports enable configuration processing and document parsing for parsing workflows.
# Parsing workflows require parser imports for configuration processing and document parsing in parsing workflows.
# Parser imports support configuration processing, document parsing, and parsing coordination while enabling
# comprehensive import strategies and systematic parsing workflows.
# Core CFGPP functionality (always available)
from .core.parser import parse_string, parse_file, loads, load
from .core.lexer import lex, LexerError, Token
from .core.formatter import format_string

# Optional AI-aware features (requires feature flags)
try:
    from .ai.parser import loads_with_extensions, explain_config, query_config
    from .ai.feature_flags import FeatureFlags
except ImportError:
    # AI features not available
    pass

# REASONING: Version and exports enable package identification and API management for package workflows.
# Package workflows require version and exports for package identification and API management in package workflows.
# Version and exports support package identification, API management, and package coordination while enabling
# comprehensive version strategies and systematic package workflows.
__version__ = "0.1.0"
__all__ = [
    # Core functionality (new clear API)
    "parse_string",
    "parse_file",
    "lex",
    "LexerError",
    "Token",
    "format_string",
    # Legacy aliases
    "loads",
    "load",
    # AI features (optional)
    "loads_with_extensions",
    "explain_config",
    "query_config",
    "FeatureFlags",
]
