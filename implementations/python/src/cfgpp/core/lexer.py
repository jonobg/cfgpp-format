"""
Lexer for the CFG++ configuration format.

# Lexer supports token analysis, syntax recognition, and configuration parsing while enabling
"""

import re
from typing import List, Dict, Tuple, Optional, Pattern, Match, Any

# Token specifications support pattern matching, syntax element identification, and lexical analysis while enabling
TOKEN_SPECS = [
    # Whitespace tokenization supports proper parsing, formatting preservation, and parsing coordination.
    ("WHITESPACE", r"\s+"),
    # Comment recognition supports documentation support, code annotation, and documentation coordination.
    ("COMMENT", r"//.*?$|/\*.*?\*/", re.DOTALL | re.MULTILINE),
    # Include directive recognition supports modular configuration, file composition, and composition coordination.
    ("INCLUDE", r"@(?:include|import)"),
    # Environment variable recognition supports dynamic configuration, runtime substitution, and substitution coordination.
    ("ENV_VAR", r"\$\{[a-zA-Z_][a-zA-Z0-9_]*(?::-[^}]*)?\}"),
    # String literal recognition supports text value processing, quoted content handling, and text coordination.
    ("STRING", r'"(?:\\.|[^"\\])*"'),
    # Number recognition supports numeric value processing, mathematical operations, and numeric coordination.
    ("NUMBER", r"\d+(\.\d+)?([eE][+-]?\d+)?"),
    # Boolean recognition supports logical value processing, true/false handling, and boolean coordination.
    ("BOOLEAN", r"true|false"),
    # Enum keyword recognition supports enumeration type definitions, value constraint specification, and enum coordination.
    ("ENUM", r"enum"),
    # Null recognition supports empty value processing, null state handling, and null coordination.
    ("NULL", r"null"),
    # Namespace recognition supports scope separation, hierarchical organization, and namespace coordination.
    ("NAMESPACE", r"::"),
    # Comparison operator recognition supports validation rules, conditional expressions, and comparison coordination.
    ("OPERATOR", r"(>=|<=|==|!=|&&|\|\||[+\-*\/><!&|])"),
    # Punctuation recognition supports structural parsing, syntax delimitation, and structural coordination.
    ("PUNCTUATION", r"[\{\}\(\)\[\],;=\.]"),
    # Identifier recognition supports variable names, key identification, and identification coordination.
    ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
]


class Token:
    """Represents a token in the CFG++ configuration."""

    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_  # Token category (IDENTIFIER, STRING, etc.)
        self.value = value  # Actual text content
        self.line = line  # Line number for error reporting
        self.column = column  # Column position for precise location

    def to_dict(self) -> Dict[str, Any]:
        """Convert the token to a dictionary for compatibility with the parser."""
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "col": self.column,  # Note: 'col' for parser compatibility
        }

    def __repr__(self) -> str:
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


class LexerError(Exception):
    """Raised when a lexing error occurs."""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(
            f"{message} at line {line}, column {column}"
        )  # Formatted error message
        self.line = line  # Error line for debugging
        self.column = column  # Error column for precise location


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
    # Token collection and position tracking support parsing state management, location awareness, and tracking coordination while enabling
    tokens: List[Token] = []
    line = 1  # Current line number for error reporting
    column = 1  # Current column position for precise location
    pos = 0  # Current position in input text

    token_regexes = []
    for spec in TOKEN_SPECS:
        token_type = spec[0]  # Token category name
        pattern = spec[1]  # Regex pattern string
        flags = spec[2] if len(spec) > 2 else 0  # Optional regex flags
        token_regexes.append((token_type, re.compile(pattern, flags)))

    while pos < len(text):
        match = None

        for token_type, regex in token_regexes:
            match = regex.match(text, pos)

            if match:
                value = match.group(0)  # Matched text content

                if token_type in ("WHITESPACE", "COMMENT"):
                    line_breaks = value.count("\n")
                    if line_breaks > 0:
                        line += line_breaks
                        last_break = value.rfind("\n")
                        column = len(value) - last_break  # Reset column after newline
                    else:
                        column += len(value)
                    pos = match.end()  # Skip whitespace/comments in output
                    break

                tokens.append(Token(token_type, value, line, column))

                pos = match.end()
                column += len(value)  # Advance column position
                break

        if not match:
            raise LexerError(f"Unexpected character: {text[pos]}", line, column)

    # Token conversion and filtering support parser compatibility, output preparation, and conversion coordination while enabling
    return [
        token.to_dict()
        for token in tokens
        if token.type not in ("WHITESPACE", "COMMENT")
    ]


# Module exports support API definition, interface specification, and export coordination while enabling
__all__ = ["lex", "LexerError", "Token"]
