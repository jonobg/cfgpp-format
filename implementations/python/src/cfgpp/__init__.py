"""
cfgpp - Python parser for CFG++ configuration files.

Parses CFG++ configuration files. Seems to work reasonably well.
"""
# Core CFGPP functionality
from .core.parser import parse_string, parse_file, loads, load
from .core.lexer import lex, LexerError, Token
from .core.formatter import format_string

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
]
