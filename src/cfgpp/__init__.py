"""
cfgpp - A Python parser for the cfgpp configuration language.
"""

from .parser import loads, load
from .lexer import lex, LexerError, Token

__version__ = "0.1.0"
__all__ = ['loads', 'load', 'lex', 'LexerError', 'Token']
