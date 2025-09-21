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
from .parser import loads, load

# REASONING: Lexer imports enable token analysis and syntax processing for lexical workflows.
# Lexical workflows require lexer imports for token analysis and syntax processing in lexical workflows.
# Lexer imports support token analysis, syntax processing, and lexical coordination while enabling
# comprehensive lexer strategies and systematic lexical workflows.
from .lexer import lex, LexerError, Token

# REASONING: Version and exports enable package identification and API management for package workflows.
# Package workflows require version and exports for package identification and API management in package workflows.
# Version and exports support package identification, API management, and package coordination while enabling
# comprehensive version strategies and systematic package workflows.
__version__ = "0.1.0"
__all__ = ["loads", "load", "lex", "LexerError", "Token"]
