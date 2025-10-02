"""
cfgpp - Python parser for CFG++ configuration files.

Parses CFG++ configuration files. Seems to work reasonably well.
"""
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

__version__ = "1.2.0"

__all__ = [
    # Core functionality
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
