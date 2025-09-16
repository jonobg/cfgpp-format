"""
Lexer for the CFG++ configuration format.

# REASONING: Lexer enables token analysis and syntax recognition for configuration parsing workflows.
# Configuration parsing workflows require lexer for token analysis and syntax recognition in parsing workflows.
# Lexer supports token analysis, syntax recognition, and configuration parsing while enabling
# comprehensive lexical strategies and systematic parsing workflows.
"""
import re
from typing import List, Dict, Tuple, Optional, Pattern, Match, Any

# REASONING: Token specifications enable pattern matching and syntax element identification for lexical workflows.
# Lexical workflows require token specifications for pattern matching and syntax element identification in lexical workflows.
# Token specifications support pattern matching, syntax element identification, and lexical analysis while enabling
# comprehensive specification strategies and systematic lexical workflows.
TOKEN_SPECS = [
    # REASONING: Whitespace tokenization enables proper parsing and formatting preservation for parsing workflows.
    # Parsing workflows require whitespace tokenization for proper parsing and formatting preservation in parsing workflows.
    # Whitespace tokenization supports proper parsing, formatting preservation, and parsing coordination.
    ('WHITESPACE', r'\s+'),
    
    # REASONING: Comment recognition enables documentation support and code annotation for documentation workflows.
    # Documentation workflows require comment recognition for documentation support and code annotation in documentation workflows.
    # Comment recognition supports documentation support, code annotation, and documentation coordination.
    ('COMMENT', r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE),
    
    # REASONING: Include directive recognition enables modular configuration and file composition for composition workflows.
    # Composition workflows require include directive recognition for modular configuration and file composition in composition workflows.
    # Include directive recognition supports modular configuration, file composition, and composition coordination.
    ('INCLUDE', r'@(?:include|import)'),
    
    # REASONING: Environment variable recognition enables dynamic configuration and runtime substitution for substitution workflows.
    # Substitution workflows require environment variable recognition for dynamic configuration and runtime substitution in substitution workflows.
    # Environment variable recognition supports dynamic configuration, runtime substitution, and substitution coordination.
    ('ENV_VAR', r'\$\{[a-zA-Z_][a-zA-Z0-9_]*(?::-[^}]*)?\}'),
    
    # REASONING: String literal recognition enables text value processing and quoted content handling for text workflows.
    # Text workflows require string literal recognition for text value processing and quoted content handling in text workflows.
    # String literal recognition supports text value processing, quoted content handling, and text coordination.
    ('STRING', r'"(?:\\.|[^"\\])*"'),
    
    # REASONING: Number recognition enables numeric value processing and mathematical operations for numeric workflows.
    # Numeric workflows require number recognition for numeric value processing and mathematical operations in numeric workflows.
    # Number recognition supports numeric value processing, mathematical operations, and numeric coordination.
    ('NUMBER', r'\d+(\.\d+)?([eE][+-]?\d+)?'),
    
    # REASONING: Boolean recognition enables logical value processing and true/false handling for boolean workflows.
    # Boolean workflows require boolean recognition for logical value processing and true/false handling in boolean workflows.
    # Boolean recognition supports logical value processing, true/false handling, and boolean coordination.
    ('BOOLEAN', r'true|false'),
    
    # REASONING: Enum keyword recognition enables enumeration type definitions and value constraint specification for enum workflows.
    # Enum workflows require enum keyword recognition for enumeration type definitions and value constraint specification in enum workflows.
    # Enum keyword recognition supports enumeration type definitions, value constraint specification, and enum coordination.
    ('ENUM', r'enum'),
    
    # REASONING: Null recognition enables empty value processing and null state handling for null workflows.
    # Null workflows require null recognition for empty value processing and null state handling in null workflows.
    # Null recognition supports empty value processing, null state handling, and null coordination.
    ('NULL', r'null'),
    
    # REASONING: Namespace recognition enables scope separation and hierarchical organization for namespace workflows.
    # Namespace workflows require namespace recognition for scope separation and hierarchical organization in namespace workflows.
    # Namespace recognition supports scope separation, hierarchical organization, and namespace coordination.
    ('NAMESPACE', r'::'),
    
    # REASONING: Comparison operator recognition enables validation rules and conditional expressions for comparison workflows.
    # Comparison workflows require comparison operator recognition for validation rules and conditional expressions in comparison workflows.
    # Comparison operator recognition supports validation rules, conditional expressions, and comparison coordination.
    ('OPERATOR', r'(>=|<=|==|!=|&&|\|\||[+\-*\/><!&|])'),
    
    # REASONING: Punctuation recognition enables structural parsing and syntax delimitation for structural workflows.
    # Structural workflows require punctuation recognition for structural parsing and syntax delimitation in structural workflows.
    # Punctuation recognition supports structural parsing, syntax delimitation, and structural coordination.
    ('PUNCTUATION', r'[\{\}\(\)\[\],;=\.]'),
    
    # REASONING: Identifier recognition enables variable names and key identification for identification workflows.
    # Identification workflows require identifier recognition for variable names and key identification in identification workflows.
    # Identifier recognition supports variable names, key identification, and identification coordination.
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
]

# REASONING: Token class enables lexical unit representation and parser integration for token workflows.
# Token workflows require token class for lexical unit representation and parser integration in token workflows.
# Token class supports lexical unit representation, parser integration, and token coordination while enabling
# comprehensive token strategies and systematic lexical workflows.
class Token:
    """Represents a token in the CFG++ configuration."""
    
    # REASONING: Constructor enables token initialization and attribute assignment for initialization workflows.
    # Initialization workflows require constructor for token initialization and attribute assignment in initialization workflows.
    # Constructor supports token initialization, attribute assignment, and initialization coordination while enabling
    # comprehensive constructor strategies and systematic initialization workflows.
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_        # Token category (IDENTIFIER, STRING, etc.)
        self.value = value       # Actual text content
        self.line = line         # Line number for error reporting
        self.column = column     # Column position for precise location
    
    # REASONING: Dictionary conversion enables parser compatibility and data structure integration for compatibility workflows.
    # Compatibility workflows require dictionary conversion for parser compatibility and data structure integration in compatibility workflows.
    # Dictionary conversion supports parser compatibility, data structure integration, and compatibility coordination while enabling
    # comprehensive conversion strategies and systematic compatibility workflows.
    def to_dict(self) -> Dict[str, Any]:
        """Convert the token to a dictionary for compatibility with the parser."""
        return {
            'type': self.type,
            'value': self.value,
            'line': self.line,
            'col': self.column      # Note: 'col' for parser compatibility
        }
    
    # REASONING: String representation enables debugging support and development visibility for debugging workflows.
    # Debugging workflows require string representation for debugging support and development visibility in debugging workflows.
    # String representation supports debugging support, development visibility, and debugging coordination while enabling
    # comprehensive representation strategies and systematic debugging workflows.
    def __repr__(self) -> str:
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})'

# REASONING: LexerError enables error handling and diagnostic reporting for error workflows.
# Error workflows require lexer error for error handling and diagnostic reporting in error workflows.
# LexerError supports error handling, diagnostic reporting, and error coordination while enabling
# comprehensive error strategies and systematic error workflows.
class LexerError(Exception):
    """Raised when a lexing error occurs."""
    
    # REASONING: Error constructor enables error initialization and location tracking for error workflows.
    # Error workflows require error constructor for error initialization and location tracking in error workflows.
    # Error constructor supports error initialization, location tracking, and error coordination while enabling
    # comprehensive constructor strategies and systematic error workflows.
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f'{message} at line {line}, column {column}')  # Formatted error message
        self.line = line      # Error line for debugging
        self.column = column  # Error column for precise location

# REASONING: Lex function enables text tokenization and lexical analysis for tokenization workflows.
# Tokenization workflows require lex function for text tokenization and lexical analysis in tokenization workflows.
# Lex function supports text tokenization, lexical analysis, and tokenization coordination while enabling
# comprehensive lex strategies and systematic tokenization workflows.
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
    # REASONING: Token collection and position tracking enable parsing state management and location awareness for tracking workflows.
    # Tracking workflows require token collection and position tracking for parsing state management and location awareness in tracking workflows.
    # Token collection and position tracking support parsing state management, location awareness, and tracking coordination while enabling
    # comprehensive collection strategies and systematic tracking workflows.
    tokens: List[Token] = []
    line = 1      # Current line number for error reporting
    column = 1    # Current column position for precise location
    pos = 0       # Current position in input text
    
    # REASONING: Regex compilation enables pattern matching optimization and performance improvement for compilation workflows.
    # Compilation workflows require regex compilation for pattern matching optimization and performance improvement in compilation workflows.
    # Regex compilation supports pattern matching optimization, performance improvement, and compilation coordination while enabling
    # comprehensive compilation strategies and systematic optimization workflows.
    token_regexes = []
    for spec in TOKEN_SPECS:
        token_type = spec[0]     # Token category name
        pattern = spec[1]        # Regex pattern string
        flags = spec[2] if len(spec) > 2 else 0  # Optional regex flags
        token_regexes.append((token_type, re.compile(pattern, flags)))
    
    # REASONING: Main tokenization loop enables sequential text processing and token extraction for processing workflows.
    # Processing workflows require main tokenization loop for sequential text processing and token extraction in processing workflows.
    # Main tokenization loop supports sequential text processing, token extraction, and processing coordination while enabling
    # comprehensive loop strategies and systematic processing workflows.
    while pos < len(text):
        match = None
        
        # REASONING: Pattern matching iteration enables token type recognition and syntax element identification for recognition workflows.
        # Recognition workflows require pattern matching iteration for token type recognition and syntax element identification in recognition workflows.
        # Pattern matching iteration supports token type recognition, syntax element identification, and recognition coordination while enabling
        # comprehensive matching strategies and systematic recognition workflows.
        for token_type, regex in token_regexes:
            match = regex.match(text, pos)
            
            if match:
                value = match.group(0)  # Matched text content
                
                # REASONING: Whitespace and comment handling enables formatting preservation and documentation support for formatting workflows.
                # Formatting workflows require whitespace and comment handling for formatting preservation and documentation support in formatting workflows.
                # Whitespace and comment handling supports formatting preservation, documentation support, and formatting coordination while enabling
                # comprehensive handling strategies and systematic formatting workflows.
                if token_type in ('WHITESPACE', 'COMMENT'):
                    # REASONING: Line and column tracking enables position accuracy and error location for location workflows.
                    # Location workflows require line and column tracking for position accuracy and error location in location workflows.
                    # Line and column tracking supports position accuracy, error location, and location coordination while enabling
                    # comprehensive tracking strategies and systematic location workflows.
                    line_breaks = value.count('\n')
                    if line_breaks > 0:
                        line += line_breaks
                        last_break = value.rfind('\n')
                        column = len(value) - last_break  # Reset column after newline
                    else:
                        column += len(value)
                    pos = match.end()  # Skip whitespace/comments in output
                    break
                
                # REASONING: Token creation enables lexical unit instantiation and parser preparation for creation workflows.
                # Creation workflows require token creation for lexical unit instantiation and parser preparation in creation workflows.
                # Token creation supports lexical unit instantiation, parser preparation, and creation coordination while enabling
                # comprehensive creation strategies and systematic instantiation workflows.
                tokens.append(Token(token_type, value, line, column))
                
                # REASONING: Position advancement enables text progression and parsing continuation for advancement workflows.
                # Advancement workflows require position advancement for text progression and parsing continuation in advancement workflows.
                # Position advancement supports text progression, parsing continuation, and advancement coordination while enabling
                # comprehensive advancement strategies and systematic progression workflows.
                pos = match.end()
                column += len(value)  # Advance column position
                break
        
        # REASONING: Error handling enables invalid character detection and diagnostic reporting for error workflows.
        # Error workflows require error handling for invalid character detection and diagnostic reporting in error workflows.
        # Error handling supports invalid character detection, diagnostic reporting, and error coordination while enabling
        # comprehensive error strategies and systematic diagnostic workflows.
        if not match:
            raise LexerError(f'Unexpected character: {text[pos]}', line, column)
    
    # REASONING: Token conversion and filtering enables parser compatibility and output preparation for conversion workflows.
    # Conversion workflows require token conversion and filtering for parser compatibility and output preparation in conversion workflows.
    # Token conversion and filtering support parser compatibility, output preparation, and conversion coordination while enabling
    # comprehensive conversion strategies and systematic preparation workflows.
    return [token.to_dict() for token in tokens if token.type not in ('WHITESPACE', 'COMMENT')]

# REASONING: Module exports enable API definition and interface specification for export workflows.
# Export workflows require module exports for API definition and interface specification in export workflows.
# Module exports support API definition, interface specification, and export coordination while enabling
# comprehensive export strategies and systematic interface workflows.
__all__ = ['lex', 'LexerError', 'Token']
