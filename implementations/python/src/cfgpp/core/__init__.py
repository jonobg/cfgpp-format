"""
CFGPP Core Library

Core parsing, lexing, and formatting functionality.
"""

from .lexer import lex, Token, LexerError
from .parser import parse_string, parse_file, loads, load, ConfigParseError
from .formatter import format_string, format_file, CfgppFormatter

__all__ = [
    # Lexer
    "lex",
    "Token",
    "LexerError",
    # Parser (new clear API)
    "parse_string",
    "parse_file",
    "ConfigParseError",
    # Parser (legacy aliases)
    "loads",
    "load",
    # Formatter
    "format_string",
    "format_file",
    "CfgppFormatter",
]
