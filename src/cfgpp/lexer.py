"""
Lexer for the CFG++ configuration format.
"""
import re
from typing import List, Dict, Tuple, Optional, Pattern, Match, Any

# Token types with their patterns and optional flags
TOKEN_SPECS = [
    ('WHITESPACE', r'\s+'),
    ('COMMENT', r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE),
    ('INCLUDE', r'@(?:include|import)'),
    ('ENV_VAR', r'\$\{[a-zA-Z_][a-zA-Z0-9_]*(?::-[^}]*)?\}'),
    ('STRING', r'"(?:\\.|[^"\\])*"'),
    ('NUMBER', r'\d+(\.\d+)?([eE][+-]?\d+)?'),
    ('BOOLEAN', r'true|false'),
    ('NULL', r'null'),
    ('OPERATOR', r'[+\-*/]'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NAMESPACE', r'::'),
    ('PUNCTUATION', r'[\{\}\(\)\[\],;=]'),
]

class Token:
    """Represents a token in the CFG++ configuration."""
    
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the token to a dictionary for compatibility with the parser."""
        return {
            'type': self.type,
            'value': self.value,
            'line': self.line,
            'col': self.column
        }
    
    def __repr__(self) -> str:
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})'

class LexerError(Exception):
    """Raised when a lexing error occurs."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f'{message} at line {line}, column {column}')
        self.line = line
        self.column = column

def lex(text: str) -> List[Dict[str, Any]]:
    """
    Convert the input text into a list of tokens.
    
    Args:
        text: The input text to tokenize
        
    Returns:
        A list of token dictionaries with 'type', 'value', 'line', and 'col' keys
        
    Raises:
        LexerError: If an unexpected character is encountered
    """
    tokens: List[Token] = []
    line = 1
    column = 1
    pos = 0
    
    # Compile regex patterns with their respective flags
    token_regexes = []
    for spec in TOKEN_SPECS:
        token_type = spec[0]
        pattern = spec[1]
        flags = spec[2] if len(spec) > 2 else 0
        token_regexes.append((token_type, re.compile(pattern, flags)))
    
    while pos < len(text):
        match = None
        
        # Try to match each token type
        for token_type, regex in token_regexes:
            match = regex.match(text, pos)
            
            if match:
                value = match.group(0)
                
                # Skip whitespace and comments
                if token_type in ('WHITESPACE', 'COMMENT'):
                    # Update line and column counters
                    line_breaks = value.count('\n')
                    if line_breaks > 0:
                        line += line_breaks
                        last_break = value.rfind('\n')
                        column = len(value) - last_break
                    else:
                        column += len(value)
                    # Update position for whitespace/comments too
                    pos = match.end()
                    break
                
                # Create token
                tokens.append(Token(token_type, value, line, column))
                
                # Update position and column
                pos = match.end()
                column += len(value)
                break
        
        if not match:
            # No token matched, raise an error
            raise LexerError(f'Unexpected character: {text[pos]}', line, column)
    
    # Convert tokens to dictionaries for compatibility
    return [token.to_dict() for token in tokens if token.type not in ('WHITESPACE', 'COMMENT')]

__all__ = ['lex', 'LexerError', 'Token']
