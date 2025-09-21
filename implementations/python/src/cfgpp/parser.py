"""
A simple parser for the CFG++ configuration format.

# REASONING: Parser enables syntax analysis and configuration structure recognition for parsing workflows.
# Parsing workflows require parser for syntax analysis and configuration structure recognition in parsing workflows.
# Parser supports syntax analysis, configuration structure recognition, and parsing coordination while enabling
# comprehensive parser strategies and systematic parsing workflows.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from .lexer import lex, Token, LexerError


# REASONING: ConfigParseError enables parsing error handling and diagnostic reporting for error workflows.
# Error workflows require config parse error for parsing error handling and diagnostic reporting in error workflows.
# ConfigParseError supports parsing error handling, diagnostic reporting, and error coordination while enabling
# comprehensive error strategies and systematic parsing error workflows.
class ConfigParseError(Exception):
    """Exception raised when configuration parsing fails."""

    # REASONING: Error constructor enables exception initialization and context preservation for error workflows.
    # Error workflows require error constructor for exception initialization and context preservation in error workflows.
    # Error constructor supports exception initialization, context preservation, and error coordination while enabling
    # comprehensive error handling strategies and systematic exception management workflows.
    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        context: Optional[str] = None,
        expected: Optional[str] = None,
    ):
        self.message = message  # Primary error description
        self.line = line  # Line number where error occurred
        self.column = column  # Column position for precise location
        self.col = column  # Alias for backward compatibility
        self.context = context  # Surrounding code/configuration for debugging
        self.expected = expected  # What was expected vs. what was found
        super().__init__(self._format_message())

    # REASONING: Message formatting enables error presentation and debugging support for formatting workflows.
    # Formatting workflows require message formatting for error presentation and debugging support in formatting workflows.
    # Message formatting supports error presentation, debugging support, and formatting coordination while enabling
    # comprehensive formatting strategies and systematic error presentation workflows.
    def _format_message(self) -> str:
        """Format the error message with line and column information if available."""
        location = []
        if self.line is not None:
            location.append(f"line {self.line}")
        if self.column is not None:
            location.append(f"column {self.column}")

        loc_str = f" at {' '.join(location)}" if location else ""
        context = f"\nContext: {self.context}" if self.context else ""
        return f"{self.message}{loc_str}{context}"


# REASONING: Parser class enables configuration parsing and syntax tree construction for parsing workflows.
# Parsing workflows require parser class for configuration parsing and syntax tree construction in parsing workflows.
# Parser class supports configuration parsing, syntax tree construction, and parsing coordination while enabling
# comprehensive parser strategies and systematic parsing workflows.
class Parser:
    """Parser for CFG++ configuration files."""

    # REASONING: Parser constructor enables parsing state initialization and context management for initialization workflows.
    # Initialization workflows require parser constructor for parsing state initialization and context management in initialization workflows.
    # Parser constructor supports parsing state initialization, context management, and initialization coordination while enabling
    # comprehensive constructor strategies and systematic parsing initialization workflows.
    def __init__(
        self,
        tokens: List[Dict[str, Any]],
        source_lines: List[str],
        base_path: Optional[Path] = None,
        included_files: Optional[Set[Path]] = None,
    ):
        self.tokens = tokens  # Tokenized input for parsing
        self.source_lines = source_lines  # Original source for error context
        self.pos = 0  # Current token position
        self.base_path = base_path or Path.cwd()  # Base path for file resolution
        self.included_files = included_files or set()  # Circular include prevention

    # REASONING: Parse method enables configuration processing and syntax tree construction for parsing workflows.
    # Parsing workflows require parse method for configuration processing and syntax tree construction in parsing workflows.
    # Parse method supports configuration processing, syntax tree construction, and parsing coordination while enabling
    # comprehensive parsing strategies and systematic configuration processing workflows.
    def parse(self, text: Optional[str] = None) -> Dict:
        """Parse the given cfgpp configuration text into a Python dictionary.

        Args:
            text: Optional text to parse. If not provided, tokens must be set in the constructor.

        Returns:
            Dict: The parsed configuration

        Raises:
            ValueError: If no tokens are provided and no text is given to parse
        """
        # REASONING: Input validation and tokenization enable proper parsing setup and input preparation for setup workflows.
        # Setup workflows require input validation and tokenization for proper parsing setup and input preparation in setup workflows.
        # Input validation and tokenization support proper parsing setup, input preparation, and setup coordination while enabling
        # comprehensive validation strategies and systematic setup workflows.
        if text is not None:
            self.tokens = self._tokenize(text)
        elif not self.tokens:
            raise ValueError("No tokens provided and no text to parse")

        self.pos = 0  # Reset parser position

        # REASONING: Simple assignment detection enables basic configuration handling and key-value recognition for detection workflows.
        # Detection workflows require simple assignment detection for basic configuration handling and key-value recognition in detection workflows.
        # Simple assignment detection supports basic configuration handling, key-value recognition, and detection coordination while enabling
        # comprehensive detection strategies and systematic assignment workflows.
        if (
            self._current_token()
            and self._current_token()["type"] == "IDENTIFIER"
            and self._current_token(1)
            and self._current_token(1)["value"] == "="
        ):
            # Parse as a simple key-value pair
            key, value = self._parse_key_value_pair()
            return {"body": {key: value}}

        # REASONING: Multi-object parsing enables complex configuration processing and hierarchical structure handling for structure workflows.
        # Structure workflows require multi-object parsing for complex configuration processing and hierarchical structure handling in structure workflows.
        # Multi-object parsing supports complex configuration processing, hierarchical structure handling, and structure coordination while enabling
        # comprehensive parsing strategies and systematic structure workflows.
        body = {}
        while self._current_token():
            # REASONING: Enum definition processing enables type definition and value constraint specification for enum workflows.
            # Enum workflows require enum definition processing for type definition and value constraint specification in enum workflows.
            # Enum definition processing supports type definition, value constraint specification, and enum coordination while enabling
            # comprehensive enum strategies and systematic type workflows.
            if self._current_token()["type"] == "ENUM":
                enum_name, enum_data = self._parse_enum_definition()
                body[enum_name] = enum_data
            # REASONING: Include directive processing enables modular configuration and file composition for composition workflows.
            # Composition workflows require include directive processing for modular configuration and file composition in composition workflows.
            # Include directive processing supports modular configuration, file composition, and composition coordination while enabling
            # comprehensive include strategies and systematic composition workflows.
            elif self._current_token()["type"] == "INCLUDE":
                include_token = self._consume("INCLUDE")

                # REASONING: Path validation enables file reference checking and include safety for validation workflows.
                # Validation workflows require path validation for file reference checking and include safety in validation workflows.
                # Path validation supports file reference checking, include safety, and validation coordination while enabling
                # comprehensive validation strategies and systematic include workflows.
                if (
                    not self._current_token()
                    or self._current_token()["type"] != "STRING"
                ):
                    raise self._create_syntax_error(
                        "Expected string path after include directive",
                        self._current_token(),
                        "string path",
                    )

                path_token = self._consume("STRING")
                include_path = path_token["value"][1:-1]  # Remove quotes

                # REASONING: Include processing and merging enable file composition and configuration integration for integration workflows.
                # Integration workflows require include processing and merging for file composition and configuration integration in integration workflows.
                # Include processing and merging support file composition, configuration integration, and integration coordination while enabling
                # comprehensive processing strategies and systematic integration workflows.
                included_data = self._process_include(include_path)

                # Merge included data into the current body
                if "body" in included_data:
                    for include_key, include_value in included_data["body"].items():
                        body[include_key] = include_value

            elif self._current_token()["type"] == "IDENTIFIER":
                # REASONING: Object parsing enables configuration object processing and structured data handling for object workflows.
                # Object workflows require object parsing for configuration object processing and structured data handling in object workflows.
                # Object parsing supports configuration object processing, structured data handling, and object coordination while enabling
                # comprehensive parsing strategies and systematic object workflows.
                obj = self._parse_object(is_top_level=True)
                if "body" in obj:
                    # Merge all objects from the parsed result
                    for obj_key, obj_value in obj["body"].items():
                        body[obj_key] = obj_value
                else:
                    # REASONING: Single object handling enables individual configuration processing and object integration for object workflows.
                    # Object workflows require single object handling for individual configuration processing and object integration in object workflows.
                    # Single object handling supports individual configuration processing, object integration, and object coordination while enabling
                    # comprehensive handling strategies and systematic object workflows.
                    if "name" in obj:
                        body[obj["name"]] = obj
                    else:
                        # Use a generated key if no name
                        body[f"object_{len(body)}"] = obj
            else:
                # REASONING: Error handling enables invalid syntax detection and parsing failure reporting for error workflows.
                # Error workflows require error handling for invalid syntax detection and parsing failure reporting in error workflows.
                # Error handling supports invalid syntax detection, parsing failure reporting, and error coordination while enabling
                # comprehensive error strategies and systematic parsing error workflows.
                raise self._create_syntax_error(
                    f"Unexpected token at top level: {self._current_token()['type']} '{self._current_token()['value']}'",
                    self._current_token(),
                    "object name or include directive",
                )

        # REASONING: Result construction enables parsed data structure creation and output preparation for construction workflows.
        # Construction workflows require result construction for parsed data structure creation and output preparation in construction workflows.
        # Result construction supports parsed data structure creation, output preparation, and construction coordination while enabling
        # comprehensive construction strategies and systematic result workflows.
        return {"body": body}

    # REASONING: Tokenize method enables text to token conversion and lexical analysis for tokenization workflows.
    # Tokenization workflows require tokenize method for text to token conversion and lexical analysis in tokenization workflows.
    # Tokenize method supports text to token conversion, lexical analysis, and tokenization coordination while enabling
    # comprehensive tokenization strategies and systematic lexical workflows.
    def _tokenize(self, text: str) -> List[Dict]:
        """Convert the input text into a list of tokens."""
        # REASONING: Token patterns enable syntax recognition and lexical element identification for pattern workflows.
        # Pattern workflows require token patterns for syntax recognition and lexical element identification in pattern workflows.
        # Token patterns support syntax recognition, lexical element identification, and pattern coordination while enabling
        # comprehensive pattern strategies and systematic recognition workflows.
        token_spec = [
            ("COMMENT", r"//.*?$"),  # Single-line comments
            ("STRING", r'"(?:\\.|[^"\\])*"'),  # Quoted strings with escape support
            ("NUMBER", r"\d+(\.\d+)?"),  # Integer and floating-point numbers
            ("BOOLEAN", r"true|false"),  # Boolean literals
            ("NAMESPACE", r"::"),  # Namespace operator
            ("IDENTIFIER", r"[a-zA-Z_]\w*"),  # Variable names and identifiers
            ("PUNCTUATION", r"[\{\}\(\)\[\],;=]"),  # Structural punctuation
            ("WHITESPACE", r"\s+"),  # Whitespace for formatting
            ("NEWLINE", r"\n"),  # Line breaks for tracking
            ("OTHER", r"."),  # Catch-all for unrecognized characters
        ]

        # REASONING: Regex compilation enables pattern matching optimization and parsing performance for compilation workflows.
        # Compilation workflows require regex compilation for pattern matching optimization and parsing performance in compilation workflows.
        # Regex compilation supports pattern matching optimization, parsing performance, and compilation coordination while enabling
        # comprehensive compilation strategies and systematic optimization workflows.
        token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)

        # REASONING: Token collection and position tracking enable parsing state management and location awareness for tracking workflows.
        # Tracking workflows require token collection and position tracking for parsing state management and location awareness in tracking workflows.
        # Token collection and position tracking support parsing state management, location awareness, and tracking coordination while enabling
        # comprehensive collection strategies and systematic tracking workflows.
        tokens = []
        line_num = 1  # Current line for error reporting
        line_start = 0  # Line start position for column calculation

        # REASONING: Pattern matching iteration enables token recognition and syntax element extraction for extraction workflows.
        # Extraction workflows require pattern matching iteration for token recognition and syntax element extraction in extraction workflows.
        # Pattern matching iteration supports token recognition, syntax element extraction, and extraction coordination while enabling
        # comprehensive matching strategies and systematic extraction workflows.
        for mo in re.finditer(token_regex, text, re.MULTILINE | re.DOTALL):
            kind = mo.lastgroup  # Token type from named group
            value = mo.group()  # Matched text content
            column = mo.start() - line_start  # Column position

            # REASONING: Special token handling enables formatting preservation and parsing state management for handling workflows.
            # Handling workflows require special token handling for formatting preservation and parsing state management in handling workflows.
            # Special token handling supports formatting preservation, parsing state management, and handling coordination while enabling
            # comprehensive handling strategies and systematic state workflows.
            if kind == "NEWLINE":
                line_start = mo.end()  # Update line start position
                line_num += 1  # Increment line counter
                continue
            elif kind == "WHITESPACE":
                continue  # Skip whitespace tokens
            elif kind == "COMMENT":
                continue  # Skip comment tokens
            elif kind == "OTHER":
                # REASONING: Error reporting enables invalid character detection and parsing failure indication for error workflows.
                # Error workflows require error reporting for invalid character detection and parsing failure indication in error workflows.
                # Error reporting supports invalid character detection, parsing failure indication, and error coordination while enabling
                # comprehensive error strategies and systematic parsing error workflows.
                raise SyntaxError(
                    f"Unexpected character: {value} at line {line_num}, column {column + 1}"
                )

            # REASONING: Token creation enables lexical unit construction and parser input preparation for creation workflows.
            # Creation workflows require token creation for lexical unit construction and parser input preparation in creation workflows.
            # Token creation supports lexical unit construction, parser input preparation, and creation coordination while enabling
            # comprehensive creation strategies and systematic token workflows.
            tokens.append(
                {
                    "type": kind,  # Token category
                    "value": value,  # Matched text
                    "line": line_num,  # Line number for errors
                    "col": column + 1,  # Column position (1-based)
                }
            )

        # REASONING: Token return enables parser input provision and lexical analysis completion for return workflows.
        # Return workflows require token return for parser input provision and lexical analysis completion in return workflows.
        # Token return supports parser input provision, lexical analysis completion, and return coordination while enabling
        # comprehensive return strategies and systematic token workflows.
        return tokens

    # REASONING: Current token method enables parsing state access and token inspection for access workflows.
    # Access workflows require current token method for parsing state access and token inspection in access workflows.
    # Current token method supports parsing state access, token inspection, and access coordination while enabling
    # comprehensive access strategies and systematic parsing workflows.
    def _current_token(self, offset: int = 0) -> Optional[Dict]:
        """Get the current token with an optional offset.

        Returns:
            The token at the current position + offset, or None if beyond the end
        """
        # REASONING: Position calculation and bounds checking enable safe token access and parsing state management for access workflows.
        # Access workflows require position calculation and bounds checking for safe token access and parsing state management in access workflows.
        # Position calculation and bounds checking support safe token access, parsing state management, and access coordination while enabling
        # comprehensive calculation strategies and systematic access workflows.
        pos = self.pos + offset
        if 0 <= pos < len(self.tokens):
            return self.tokens[pos]
        return None

    # REASONING: Syntax error creation enables parsing error construction and diagnostic information for error workflows.
    # Error workflows require syntax error creation for parsing error construction and diagnostic information in error workflows.
    # Syntax error creation supports parsing error construction, diagnostic information, and error coordination while enabling
    # comprehensive error strategies and systematic diagnostic workflows.
    def _create_syntax_error(
        self, message: str, token: Optional[Dict] = None, expected: Optional[str] = None
    ) -> ConfigParseError:
        """Create a syntax error with detailed context information."""
        return ConfigParseError(message, token, expected)

    # REASONING: Include processing enables modular configuration and file composition for composition workflows.
    # Composition workflows require include processing for modular configuration and file composition in composition workflows.
    # Include processing supports modular configuration, file composition, and composition coordination while enabling
    # comprehensive processing strategies and systematic composition workflows.
    def _process_include(self, include_path: str) -> Dict[str, Any]:
        """Process an include/import directive."""
        # REASONING: Path resolution enables file location and extension normalization for resolution workflows.
        # Resolution workflows require path resolution for file location and extension normalization in resolution workflows.
        # Path resolution supports file location, extension normalization, and resolution coordination while enabling
        # comprehensive resolution strategies and systematic file workflows.
        if not include_path.endswith(".cfgpp"):
            include_path += ".cfgpp"  # Add default extension

        resolved_path = (self.base_path / include_path).resolve()

        # REASONING: Circular include detection enables infinite recursion prevention and safety assurance for safety workflows.
        # Safety workflows require circular include detection for infinite recursion prevention and safety assurance in safety workflows.
        # Circular include detection supports infinite recursion prevention, safety assurance, and safety coordination while enabling
        # comprehensive detection strategies and systematic safety workflows.
        if resolved_path in self.included_files:
            raise ConfigParseError(f"Circular include detected: {include_path}")

        # REASONING: File existence validation enables include safety and error prevention for validation workflows.
        # Validation workflows require file existence validation for include safety and error prevention in validation workflows.
        # File existence validation supports include safety, error prevention, and validation coordination while enabling
        # comprehensive validation strategies and systematic include workflows.
        if not resolved_path.exists():
            raise ConfigParseError(f"Include file not found: {include_path}")

        # REASONING: File reading and error handling enable content loading and failure management for loading workflows.
        # Loading workflows require file reading and error handling for content loading and failure management in loading workflows.
        # File reading and error handling support content loading, failure management, and loading coordination while enabling
        # comprehensive reading strategies and systematic loading workflows.
        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                included_content = f.read()
        except IOError as e:
            raise ConfigParseError(f"Failed to read include file '{include_path}': {e}")

        # REASONING: Recursive parsing enables nested configuration processing and composition support for recursion workflows.
        # Recursion workflows require recursive parsing for nested configuration processing and composition support in recursion workflows.
        # Recursive parsing supports nested configuration processing, composition support, and recursion coordination while enabling
        # comprehensive parsing strategies and systematic recursion workflows.
        new_included_files = self.included_files.copy()  # Track included files
        new_included_files.add(resolved_path)

        return loads(included_content, str(resolved_path.parent), new_included_files)

    # REASONING: Expression detection enables mathematical expression recognition and parsing preparation for detection workflows.
    # Detection workflows require expression detection for mathematical expression recognition and parsing preparation in detection workflows.
    # Expression detection supports mathematical expression recognition, parsing preparation, and detection coordination while enabling
    # comprehensive detection strategies and systematic expression workflows.
    def _is_expression_start(self) -> bool:
        """Check if the current position starts an expression by looking ahead for operators."""
        # REASONING: Position preservation enables lookahead analysis and state restoration for preservation workflows.
        # Preservation workflows require position preservation for lookahead analysis and state restoration in preservation workflows.
        # Position preservation supports lookahead analysis, state restoration, and preservation coordination while enabling
        # comprehensive preservation strategies and systematic lookahead workflows.
        original_pos = self.pos

        try:
            # REASONING: Token validation enables expression checking and input verification for validation workflows.
            # Validation workflows require token validation for expression checking and input verification in validation workflows.
            # Token validation supports expression checking, input verification, and validation coordination while enabling
            # comprehensive validation strategies and systematic expression workflows.
            if not self._current_token():
                return False

            # REASONING: Parenthesis detection enables grouped expression recognition and precedence handling for grouping workflows.
            # Grouping workflows require parenthesis detection for grouped expression recognition and precedence handling in grouping workflows.
            # Parenthesis detection supports grouped expression recognition, precedence handling, and grouping coordination while enabling
            # comprehensive detection strategies and systematic grouping workflows.
            if self._current_token()["value"] == "(":
                return True

            # REASONING: Literal and operator checking enables expression pattern recognition and mathematical operation detection for pattern workflows.
            # Pattern workflows require literal and operator checking for expression pattern recognition and mathematical operation detection in pattern workflows.
            # Literal and operator checking supports expression pattern recognition, mathematical operation detection, and pattern coordination while enabling
            # comprehensive checking strategies and systematic pattern workflows.
            if self._current_token()["type"] in [
                "STRING",
                "NUMBER",
                "BOOLEAN",
                "ENV_VAR",
                "IDENTIFIER",
            ]:
                self.pos += 1
                # Check for following operators
                if (
                    self._current_token()
                    and self._current_token()["type"] == "OPERATOR"
                    and self._current_token()["value"] in ["+", "-", "*", "/"]
                ):
                    return True

            return False
        finally:
            # REASONING: State restoration enables parsing position recovery and consistent state management for restoration workflows.
            # Restoration workflows require state restoration for parsing position recovery and consistent state management in restoration workflows.
            # State restoration supports parsing position recovery, consistent state management, and restoration coordination while enabling
            # comprehensive restoration strategies and systematic state workflows.
            self.pos = original_pos

    # REASONING: Expression parsing enables mathematical expression processing and calculation support for expression workflows.
    # Expression workflows require expression parsing for mathematical expression processing and calculation support in expression workflows.
    # Expression parsing supports mathematical expression processing, calculation support, and expression coordination while enabling
    # comprehensive parsing strategies and systematic expression workflows.
    def _parse_expression(self) -> Dict[str, Any]:
        """Parse a mathematical or string expression."""
        return self._parse_addition()

    # REASONING: Addition parsing enables arithmetic operation processing and precedence handling for arithmetic workflows.
    # Arithmetic workflows require addition parsing for arithmetic operation processing and precedence handling in arithmetic workflows.
    # Addition parsing supports arithmetic operation processing, precedence handling, and arithmetic coordination while enabling
    # comprehensive parsing strategies and systematic arithmetic workflows.
    def _parse_addition(self) -> Dict[str, Any]:
        """Parse addition and subtraction operations."""
        left = self._parse_multiplication()  # Higher precedence first

        # REASONING: Operator iteration enables left-associative expression evaluation and operation chaining for iteration workflows.
        # Iteration workflows require operator iteration for left-associative expression evaluation and operation chaining in iteration workflows.
        # Operator iteration supports left-associative expression evaluation, operation chaining, and iteration coordination while enabling
        # comprehensive iteration strategies and systematic evaluation workflows.
        while (
            self._current_token()
            and self._current_token()["type"] == "OPERATOR"
            and self._current_token()["value"] in ["+", "-"]
        ):
            op_token = self._consume("OPERATOR")
            right = self._parse_multiplication()

            # REASONING: Binary operation evaluation enables arithmetic calculation and result computation for evaluation workflows.
            # Evaluation workflows require binary operation evaluation for arithmetic calculation and result computation in evaluation workflows.
            # Binary operation evaluation supports arithmetic calculation, result computation, and evaluation coordination while enabling
            # comprehensive evaluation strategies and systematic calculation workflows.
            left = self._evaluate_binary_op(left, op_token["value"], right)

        return left

    # REASONING: Multiplication parsing enables high-precedence arithmetic and mathematical operation processing for multiplication workflows.
    # Multiplication workflows require multiplication parsing for high-precedence arithmetic and mathematical operation processing in multiplication workflows.
    # Multiplication parsing supports high-precedence arithmetic, mathematical operation processing, and multiplication coordination while enabling
    # comprehensive parsing strategies and systematic multiplication workflows.
    def _parse_multiplication(self) -> Dict[str, Any]:
        """Parse multiplication and division operations."""
        left = self._parse_primary()  # Highest precedence

        # REASONING: High-precedence operator processing enables mathematical operation precedence and calculation order for precedence workflows.
        # Precedence workflows require high-precedence operator processing for mathematical operation precedence and calculation order in precedence workflows.
        # High-precedence operator processing supports mathematical operation precedence, calculation order, and precedence coordination while enabling
        # comprehensive processing strategies and systematic precedence workflows.
        while (
            self._current_token()
            and self._current_token()["type"] == "OPERATOR"
            and self._current_token()["value"] in ["*", "/"]
        ):
            op_token = self._consume("OPERATOR")
            right = self._parse_primary()

            # REASONING: Multiplication evaluation enables arithmetic calculation and numerical result computation for computation workflows.
            # Computation workflows require multiplication evaluation for arithmetic calculation and numerical result computation in computation workflows.
            # Multiplication evaluation supports arithmetic calculation, numerical result computation, and computation coordination while enabling
            # comprehensive evaluation strategies and systematic computation workflows.
            left = self._evaluate_binary_op(left, op_token["value"], right)

        return left

    # REASONING: Primary parsing enables fundamental expression element processing and literal value handling for primary workflows.
    # Primary workflows require primary parsing for fundamental expression element processing and literal value handling in primary workflows.
    # Primary parsing supports fundamental expression element processing, literal value handling, and primary coordination while enabling
    # comprehensive parsing strategies and systematic primary workflows.
    def _parse_primary(self) -> Dict[str, Any]:
        """Parse primary expressions (numbers, strings, parenthesized expressions)."""
        # REASONING: Token validation enables expression input checking and parsing safety for validation workflows.
        # Validation workflows require token validation for expression input checking and parsing safety in validation workflows.
        # Token validation supports expression input checking, parsing safety, and validation coordination while enabling
        # comprehensive validation strategies and systematic primary workflows.
        token = self._current_token()

        if not token:
            raise self._create_syntax_error("Unexpected end of input in expression")

        # REASONING: Parenthesized expression handling enables precedence override and grouped evaluation for grouping workflows.
        # Grouping workflows require parenthesized expression handling for precedence override and grouped evaluation in grouping workflows.
        # Parenthesized expression handling supports precedence override, grouped evaluation, and grouping coordination while enabling
        # comprehensive handling strategies and systematic grouping workflows.
        if token["value"] == "(":
            self._consume("PUNCTUATION", "(")
            result = self._parse_expression()  # Recursive expression parsing
            if not self._current_token() or self._current_token()["value"] != ")":
                raise self._create_syntax_error(
                    "Expected ')' to close expression", self._current_token(), "')'"
                )
            self._consume("PUNCTUATION", ")")
            return result

        # REASONING: String literal processing enables text value extraction and quote removal for text workflows.
        # Text workflows require string literal processing for text value extraction and quote removal in text workflows.
        # String literal processing supports text value extraction, quote removal, and text coordination while enabling
        # comprehensive processing strategies and systematic text workflows.
        if token["type"] == "STRING":
            value = self._consume("STRING")["value"]
            value = value[1:-1]  # Remove surrounding quotes
            return {
                "type": "string",
                "value": value,
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Number parsing enables numeric value processing and type determination for numeric workflows.
        # Numeric workflows require number parsing for numeric value processing and type determination in numeric workflows.
        # Number parsing supports numeric value processing, type determination, and numeric coordination while enabling
        # comprehensive parsing strategies and systematic numeric workflows.
        elif token["type"] == "NUMBER":
            value = self._consume("NUMBER")["value"]
            try:
                value = int(value)  # Try integer first
                value_type = "integer"
            except ValueError:
                try:
                    value = float(value)  # Fall back to float
                    value_type = "float"
                except ValueError:
                    raise self._create_syntax_error("Invalid number format", token)
            return {
                "type": value_type,
                "value": value,
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Boolean parsing enables logical value processing and true/false determination for boolean workflows.
        # Boolean workflows require boolean parsing for logical value processing and true/false determination in boolean workflows.
        # Boolean parsing supports logical value processing, true/false determination, and boolean coordination while enabling
        # comprehensive parsing strategies and systematic boolean workflows.
        elif token["type"] == "BOOLEAN":
            value = self._consume("BOOLEAN")["value"]
            return {
                "type": "boolean",
                "value": value.lower() == "true",  # Convert to boolean
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Environment variable processing enables dynamic configuration and runtime substitution for substitution workflows.
        # Substitution workflows require environment variable processing for dynamic configuration and runtime substitution in substitution workflows.
        # Environment variable processing supports dynamic configuration, runtime substitution, and substitution coordination while enabling
        # comprehensive processing strategies and systematic substitution workflows.
        elif token["type"] == "ENV_VAR":
            env_token = self._consume("ENV_VAR")["value"]
            env_content = env_token[2:-1]  # Remove ${ and } delimiters

            # REASONING: Default value handling enables fallback configuration and missing variable support for fallback workflows.
            # Fallback workflows require default value handling for fallback configuration and missing variable support in fallback workflows.
            # Default value handling supports fallback configuration, missing variable support, and fallback coordination while enabling
            # comprehensive handling strategies and systematic fallback workflows.
            if ":-" in env_content:
                var_name, default_value = env_content.split(":-", 1)
                if default_value.startswith('"') and default_value.endswith('"'):
                    default_value = default_value[1:-1]  # Remove quotes from default
            else:
                var_name = env_content
                default_value = None

            # REASONING: Environment resolution enables system variable access and configuration externalization for resolution workflows.
            # Resolution workflows require environment resolution for system variable access and configuration externalization in resolution workflows.
            # Environment resolution supports system variable access, configuration externalization, and resolution coordination while enabling
            # comprehensive resolution strategies and systematic environment workflows.
            env_value = os.getenv(var_name, default_value)
            if env_value is None:
                raise self._create_syntax_error(
                    f"Environment variable '{var_name}' is not set and no default provided",
                    token,
                )

            # REASONING: Type inference enables automatic type detection and value conversion for inference workflows.
            # Inference workflows require type inference for automatic type detection and value conversion in inference workflows.
            # Type inference supports automatic type detection, value conversion, and inference coordination while enabling
            # comprehensive inference strategies and systematic type workflows.
            if env_value.lower() in ("true", "false"):
                return {
                    "type": "boolean",
                    "value": env_value.lower() == "true",
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }

            # REASONING: Integer conversion enables numeric type detection and value parsing for conversion workflows.
            # Conversion workflows require integer conversion for numeric type detection and value parsing in conversion workflows.
            # Integer conversion supports numeric type detection, value parsing, and conversion coordination while enabling
            # comprehensive conversion strategies and systematic numeric workflows.
            try:
                int_value = int(env_value)
                return {
                    "type": "integer",
                    "value": int_value,
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }
            except ValueError:
                pass  # Continue to float or string handling

            # REASONING: Float conversion enables floating-point type detection and decimal number support for float workflows.
            # Float workflows require float conversion for floating-point type detection and decimal number support in float workflows.
            # Float conversion supports floating-point type detection, decimal number support, and float coordination while enabling
            # comprehensive conversion strategies and systematic float workflows.
            try:
                float_value = float(env_value)
                return {
                    "type": "float",
                    "value": float_value,
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }
            except ValueError:
                pass  # Fall back to string type

            # REASONING: String fallback enables default type handling and text value preservation for fallback workflows.
            # Fallback workflows require string fallback for default type handling and text value preservation in fallback workflows.
            # String fallback supports default type handling, text value preservation, and fallback coordination while enabling
            # comprehensive fallback strategies and systematic string workflows.
            return {
                "type": "string",
                "value": env_value,
                "line": token["line"],
                "col": token["col"],
                "env_var": var_name,
            }

        # REASONING: Null identifier handling enables empty value processing and null literal support for null workflows.
        # Null workflows require identifier handling for empty value processing and null literal support in null workflows.
        # Null identifier handling supports empty value processing, null literal support, and null coordination while enabling
        # comprehensive handling strategies and systematic null workflows.
        elif token["type"] == "IDENTIFIER" and token["value"].lower() == "null":
            self._consume("IDENTIFIER", "null")
            return {
                "type": "null",
                "value": None,
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Error handling enables invalid token detection and parsing failure reporting for error workflows.
        # Error workflows require error handling for invalid token detection and parsing failure reporting in error workflows.
        # Error handling supports invalid token detection, parsing failure reporting, and error coordination while enabling
        # comprehensive error strategies and systematic parsing error workflows.
        raise self._create_syntax_error(
            f"Unexpected token in expression: {token['value']}", token
        )

    # REASONING: Binary operation evaluation enables mathematical expression computation and value processing for evaluation workflows.
    # Evaluation workflows require binary operation evaluation for mathematical expression computation and value processing in evaluation workflows.
    # Binary operation evaluation supports mathematical expression computation, value processing, and evaluation coordination while enabling
    # comprehensive evaluation strategies and systematic computation workflows.
    def _evaluate_binary_op(
        self, left: Dict[str, Any], operator: str, right: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a binary operation between two values."""
        # REASONING: Value extraction enables operand preparation and type checking for extraction workflows.
        # Extraction workflows require value extraction for operand preparation and type checking in extraction workflows.
        # Value extraction supports operand preparation, type checking, and extraction coordination while enabling
        # comprehensive extraction strategies and systematic operand workflows.
        left_val = left["value"]
        right_val = right["value"]
        left_type = left["type"]
        right_type = right["type"]

        # REASONING: String concatenation enables text combination and string operation support for concatenation workflows.
        # Concatenation workflows require string concatenation for text combination and string operation support in concatenation workflows.
        # String concatenation supports text combination, string operation support, and concatenation coordination while enabling
        # comprehensive concatenation strategies and systematic string workflows.
        if operator == "+" and (left_type == "string" or right_type == "string"):
            result_val = str(left_val) + str(
                right_val
            )  # Coerce to strings and concatenate
            return {
                "type": "string",
                "value": result_val,
                "line": left.get("line", 1),
                "col": left.get("col", 1),
                "expression": True,
            }

        # REASONING: Numeric operations enable mathematical computation and arithmetic evaluation for numeric workflows.
        # Numeric workflows require numeric operations for mathematical computation and arithmetic evaluation in numeric workflows.
        # Numeric operations support mathematical computation, arithmetic evaluation, and numeric coordination while enabling
        # comprehensive operation strategies and systematic numeric workflows.
        if left_type in ["integer", "float"] and right_type in ["integer", "float"]:
            try:
                # REASONING: Arithmetic operation dispatch enables calculation execution and mathematical processing for calculation workflows.
                # Calculation workflows require arithmetic operation dispatch for calculation execution and mathematical processing in calculation workflows.
                # Arithmetic operation dispatch supports calculation execution, mathematical processing, and calculation coordination while enabling
                # comprehensive dispatch strategies and systematic calculation workflows.
                if operator == "+":
                    result_val = left_val + right_val
                elif operator == "-":
                    result_val = left_val - right_val
                elif operator == "*":
                    result_val = left_val * right_val
                elif operator == "/":
                    # REASONING: Division by zero checking enables error prevention and mathematical safety for safety workflows.
                    # Safety workflows require division by zero checking for error prevention and mathematical safety in safety workflows.
                    # Division by zero checking supports error prevention, mathematical safety, and safety coordination while enabling
                    # comprehensive checking strategies and systematic safety workflows.
                    if right_val == 0:
                        raise self._create_syntax_error(
                            "Division by zero in expression"
                        )
                    result_val = left_val / right_val
                else:
                    raise self._create_syntax_error(f"Unsupported operator: {operator}")

                # REASONING: Result type determination enables type preservation and numeric accuracy for type workflows.
                # Type workflows require result type determination for type preservation and numeric accuracy in type workflows.
                # Result type determination supports type preservation, numeric accuracy, and type coordination while enabling
                # comprehensive determination strategies and systematic type workflows.
                result_type = "float" if isinstance(result_val, float) else "integer"

                return {
                    "type": result_type,
                    "value": result_val,
                    "line": left.get("line", 1),
                    "col": left.get("col", 1),
                    "expression": True,
                }
            except Exception as e:
                # REASONING: Exception handling enables computation error management and failure reporting for error workflows.
                # Error workflows require exception handling for computation error management and failure reporting in error workflows.
                # Exception handling supports computation error management, failure reporting, and error coordination while enabling
                # comprehensive handling strategies and systematic error workflows.
                raise self._create_syntax_error(
                    f"Error in expression evaluation: {str(e)}"
                )

        # REASONING: Type compatibility error enables invalid operation detection and type safety for compatibility workflows.
        # Compatibility workflows require type compatibility error for invalid operation detection and type safety in compatibility workflows.
        # Type compatibility error supports invalid operation detection, type safety, and compatibility coordination while enabling
        # comprehensive error strategies and systematic compatibility workflows.
        raise self._create_syntax_error(
            f"Cannot apply operator '{operator}' to {left_type} and {right_type}"
        )

    # REASONING: Consume method enables token consumption and parsing state advancement for consumption workflows.
    # Consumption workflows require consume method for token consumption and parsing state advancement in consumption workflows.
    # Consume method supports token consumption, parsing state advancement, and consumption coordination while enabling
    # comprehensive consumption strategies and systematic parsing workflows.
    def _consume(self, expected_type: str = None, expected_value: str = None) -> Dict:
        """Consume the current token if it matches the expected type and/or value.

        Args:
            expected_type: The expected token type (e.g., 'IDENTIFIER', 'STRING')
            expected_value: The expected token value (e.g., '=', '{', '}')

        Returns:
            Dict: The consumed token

        Raises:
            ConfigParseError: If the current token doesn't match expectations
        """
        # REASONING: Token retrieval enables current position access and parsing state inspection for retrieval workflows.
        # Retrieval workflows require token retrieval for current position access and parsing state inspection in retrieval workflows.
        # Token retrieval supports current position access, parsing state inspection, and retrieval coordination while enabling
        # comprehensive retrieval strategies and systematic access workflows.
        token = self._current_token()

        # REASONING: End-of-input handling enables parsing completion detection and error reporting for completion workflows.
        # Completion workflows require end-of-input handling for parsing completion detection and error reporting in completion workflows.
        # End-of-input handling supports parsing completion detection, error reporting, and completion coordination while enabling
        # comprehensive handling strategies and systematic completion workflows.
        if token is None:
            expected = []
            if expected_type:
                expected.append(f"type '{expected_type}'")
            if expected_value:
                expected.append(f"value '{expected_value}'")
            expected_str = " or ".join(expected) or "token"

            # REASONING: Error construction enables end-of-input reporting and expectation communication for error workflows.
            # Error workflows require error construction for end-of-input reporting and expectation communication in error workflows.
            # Error construction supports end-of-input reporting, expectation communication, and error coordination while enabling
            # comprehensive construction strategies and systematic error workflows.
            raise self._create_syntax_error(
                message=f"Unexpected end of input, expected {expected_str}",
                expected=expected_str,
            )

        # REASONING: Type validation enables token type checking and syntax enforcement for validation workflows.
        # Validation workflows require type validation for token type checking and syntax enforcement in validation workflows.
        # Type validation supports token type checking, syntax enforcement, and validation coordination while enabling
        # comprehensive validation strategies and systematic type workflows.
        if expected_type is not None and token["type"] != expected_type:
            raise self._create_syntax_error(
                message=f"Got unexpected token type '{token['type']}'",
                token=token,
                expected=f"{expected_type}",
            )

        # REASONING: Value validation enables token content checking and exact match enforcement for validation workflows.
        # Validation workflows require value validation for token content checking and exact match enforcement in validation workflows.
        # Value validation supports token content checking, exact match enforcement, and validation coordination while enabling
        # comprehensive validation strategies and systematic content workflows.
        if expected_value is not None and token["value"] != expected_value:
            raise self._create_syntax_error(
                message=f"Got unexpected value '{token['value']}'",
                token=token,
                expected=f"'{expected_value}'",
            )

        # REASONING: Position advancement enables parsing progression and token consumption for advancement workflows.
        # Advancement workflows require position advancement for parsing progression and token consumption in advancement workflows.
        # Position advancement supports parsing progression, token consumption, and advancement coordination while enabling
        # comprehensive advancement strategies and systematic progression workflows.
        self.pos += 1
        return token

    # REASONING: Parameter parsing enables function signature analysis and type definition processing for parameter workflows.
    # Parameter workflows require parameter parsing for function signature analysis and type definition processing in parameter workflows.
    # Parameter parsing supports function signature analysis, type definition processing, and parameter coordination while enabling
    # comprehensive parsing strategies and systematic parameter workflows.
    def _parse_parameter(self) -> tuple:
        """Parse a single parameter definition.

        Returns:
            A tuple containing:
            - The parameter name as a string
            - A dictionary with parameter information (type, is_array, value, line, col, etc.)
        """
        # REASONING: Type parsing enables parameter type identification and namespace support for type workflows.
        # Type workflows require type parsing for parameter type identification and namespace support in type workflows.
        # Type parsing supports parameter type identification, namespace support, and type coordination while enabling
        # comprehensive parsing strategies and systematic type workflows.

        # REASONING: Type parsing enables parameter type identification and namespace support for type workflows.
        # Type workflows require type parsing for parameter type identification and namespace support in type workflows.
        # Type parsing supports parameter type identification, namespace support, and type coordination while enabling
        # comprehensive parsing strategies and systematic type workflows.
        param_type, type_parts = self._parse_identifier(allow_namespace=True)

        # REASONING: Enum type usage detection enables enum parameter recognition and type constraint enforcement for enum workflows.
        # Enum workflows require enum type usage detection for enum parameter recognition and type constraint enforcement in enum workflows.
        # Enum type usage detection supports enum parameter recognition, type constraint enforcement, and enum coordination while enabling
        # comprehensive detection strategies and systematic enum usage workflows.
        # Note: This is a simplified check - in a complete implementation, we would validate against defined enums
        is_enum_type = "::" not in param_type and param_type not in [
            "string",
            "int",
            "float",
            "boolean",
            "array",
            "object",
        ]

        is_array = False

        # REASONING: Array notation detection enables array type recognition and collection type support for array workflows.
        # Array workflows require array notation detection for array type recognition and collection type support in array workflows.
        # Array notation detection supports array type recognition, collection type support, and array coordination while enabling
        # comprehensive detection strategies and systematic array workflows.
        if self._current_token() and self._current_token()["value"] == "[":
            self._consume("PUNCTUATION", "[")
            self._consume("PUNCTUATION", "]")
            is_array = True

        # REASONING: Parameter name extraction enables identifier processing and variable naming for naming workflows.
        # Naming workflows require parameter name extraction for identifier processing and variable naming in naming workflows.
        # Parameter name extraction supports identifier processing, variable naming, and naming coordination while enabling
        # comprehensive extraction strategies and systematic naming workflows.
        param_name = self._consume("IDENTIFIER")

        # REASONING: Default value parsing enables optional parameter support and fallback value processing for default workflows.
        # Default workflows require default value parsing for optional parameter support and fallback value processing in default workflows.
        # Default value parsing supports optional parameter support, fallback value processing, and default coordination while enabling
        # comprehensive parsing strategies and systematic default workflows.
        default_value = None
        if self._current_token() and self._current_token()["value"] == "=":
            self._consume("PUNCTUATION", "=")
            default_value = self._parse_value()

        # REASONING: Parameter information construction enables type metadata preservation and parsing result organization for construction workflows.
        # Construction workflows require parameter information construction for type metadata preservation and parsing result organization in construction workflows.
        # Parameter information construction supports type metadata preservation, parsing result organization, and construction coordination while enabling
        # comprehensive construction strategies and systematic parameter workflows.
        param_info = {
            "type": param_type,  # Parameter type name
            "is_array": is_array,  # Array type flag
            "is_enum_type": is_enum_type,  # Enum type flag for constraint validation
            "value": default_value,  # Default value if specified
            "line": type_parts[0]["line"],  # Line number for error reporting
            "col": type_parts[0]["col"],  # Column position for location
        }

        # REASONING: Nested type handling enables complex type definition and hierarchical type support for nesting workflows.
        # Nesting workflows require nested type handling for complex type definition and hierarchical type support in nesting workflows.
        # Nested type handling supports complex type definition, hierarchical type support, and nesting coordination while enabling
        # comprehensive handling strategies and systematic nesting workflows.
        if self._current_token() and self._current_token()["value"] == "(":
            param_info["nested"] = self._parse_object()

        return param_name["value"], param_info

    # REASONING: Identifier parsing enables name resolution and namespace support for identifier workflows.
    # Identifier workflows require identifier parsing for name resolution and namespace support in identifier workflows.
    # Identifier parsing supports name resolution, namespace support, and identifier coordination while enabling
    # comprehensive parsing strategies and systematic identifier workflows.
    def _parse_identifier(self, allow_namespace=True) -> tuple:
        """Parse an identifier, which could be a simple name or a namespaced name.

        Args:
            allow_namespace: Whether to allow namespace separators (::) in the identifier

        Returns:
            A tuple containing:
            - The full identifier as a string
            - A list of token parts that make up the identifier

        Raises:
            ConfigParseError: If the identifier is invalid or incomplete
        """
        # REASONING: Identifier validation enables name token checking and parsing safety for validation workflows.
        # Validation workflows require identifier validation for name token checking and parsing safety in validation workflows.
        # Identifier validation supports name token checking, parsing safety, and validation coordination while enabling
        # comprehensive validation strategies and systematic identifier workflows.
        if not self._current_token() or self._current_token()["type"] != "IDENTIFIER":
            token = self._current_token()
            raise self._create_syntax_error(
                message="Expected an identifier", token=token, expected="identifier"
            )

        # REASONING: Name part collection enables identifier component tracking and namespace construction for collection workflows.
        # Collection workflows require name part collection for identifier component tracking and namespace construction in collection workflows.
        # Name part collection supports identifier component tracking, namespace construction, and collection coordination while enabling
        # comprehensive collection strategies and systematic identifier workflows.
        name_parts = [self._consume("IDENTIFIER")]

        # REASONING: Namespace processing enables hierarchical naming and scope resolution for namespace workflows.
        # Namespace workflows require namespace processing for hierarchical naming and scope resolution in namespace workflows.
        # Namespace processing supports hierarchical naming, scope resolution, and namespace coordination while enabling
        # comprehensive processing strategies and systematic namespace workflows.
        if allow_namespace:
            while (
                self._current_token() and self._current_token()["type"] == "NAMESPACE"
            ):
                namespace_token = self._current_token()
                self._consume("NAMESPACE")

                # REASONING: Namespace continuation validation enables proper identifier chaining and syntax enforcement for continuation workflows.
                # Continuation workflows require namespace continuation validation for proper identifier chaining and syntax enforcement in continuation workflows.
                # Namespace continuation validation supports proper identifier chaining, syntax enforcement, and continuation coordination while enabling
                # comprehensive validation strategies and systematic continuation workflows.
                if (
                    not self._current_token()
                    or self._current_token()["type"] != "IDENTIFIER"
                ):
                    raise self._create_syntax_error(
                        message="Incomplete namespaced identifier",
                        token=namespace_token,
                        expected="identifier after '::'",
                    )

                # The next token must be an identifier
                name_parts.append("::")
                name_parts.append(self._consume("IDENTIFIER"))

        # REASONING: Name construction enables identifier assembly and namespace concatenation for construction workflows.
        # Construction workflows require name construction for identifier assembly and namespace concatenation in construction workflows.
        # Name construction supports identifier assembly, namespace concatenation, and construction coordination while enabling
        # comprehensive construction strategies and systematic identifier workflows.
        full_name = "".join(
            part["value"] if isinstance(part, dict) else part for part in name_parts
        )
        return full_name, [part for part in name_parts if isinstance(part, dict)]

    # REASONING: Object parsing enables configuration object processing and structured data handling for object workflows.
    # Object workflows require object parsing for configuration object processing and structured data handling in object workflows.
    # Object parsing supports configuration object processing, structured data handling, and object coordination while enabling
    # comprehensive parsing strategies and systematic object workflows.
    def _parse_object(self, is_top_level: bool = True) -> Dict:
        """Parse an object definition.

        Args:
            is_top_level: Whether this is a top-level object (affects return structure)

        Returns:
            A dictionary representing the parsed object with the following structure:
            - If is_top_level is True:
                {
                    'body': {
                        'TypeName': {
                            'name': 'TypeName',
                            'body': { ...nested properties... },
                            'line': int,
                            'col': int
                        }
                    }
                }
            - If is_top_level is False:
                {
                    'name': 'TypeName',
                    'body': { ...nested properties... },
                    'line': int,
                    'col': int
                }
        """
        # REASONING: Object name parsing enables type identification and namespace resolution for identification workflows.
        # Identification workflows require object name parsing for type identification and namespace resolution in identification workflows.
        # Object name parsing supports type identification, namespace resolution, and identification coordination while enabling
        # comprehensive parsing strategies and systematic identification workflows.
        full_name, name_parts = self._parse_identifier()

        # REASONING: Position tracking enables error location and parsing context preservation for tracking workflows.
        # Tracking workflows require position tracking for error location and parsing context preservation in tracking workflows.
        # Position tracking supports error location, parsing context preservation, and tracking coordination while enabling
        # comprehensive tracking strategies and systematic location workflows.
        start_line = name_parts[0]["line"]
        start_col = name_parts[0]["col"]

        # REASONING: Parameter parsing enables function signature processing and type definition support for parameter workflows.
        # Parameter workflows require parameter parsing for function signature processing and type definition support in parameter workflows.
        # Parameter parsing supports function signature processing, type definition support, and parameter coordination while enabling
        # comprehensive parsing strategies and systematic parameter workflows.
        params = {}
        if self._current_token() and self._current_token()["value"] == "(":
            self._consume("PUNCTUATION", "(")

            # REASONING: Parameter iteration enables parameter list processing and function signature construction for iteration workflows.
            # Iteration workflows require parameter iteration for parameter list processing and function signature construction in iteration workflows.
            # Parameter iteration supports parameter list processing, function signature construction, and iteration coordination while enabling
            # comprehensive iteration strategies and systematic parameter workflows.
            while self._current_token() and self._current_token()["value"] != ")":
                param_name, param_info = self._parse_parameter()
                params[param_name] = param_info

                # REASONING: Parameter separation handling enables comma-separated list parsing and syntax compliance for separation workflows.
                # Separation workflows require parameter separation handling for comma-separated list parsing and syntax compliance in separation workflows.
                # Parameter separation handling supports comma-separated list parsing, syntax compliance, and separation coordination while enabling
                # comprehensive handling strategies and systematic separation workflows.
                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")
                else:
                    break

            self._consume("PUNCTUATION", ")")

        # REASONING: Object body parsing enables property collection and structural content processing for body workflows.
        # Body workflows require object body parsing for property collection and structural content processing in body workflows.
        # Object body parsing supports property collection, structural content processing, and body coordination while enabling
        # comprehensive parsing strategies and systematic body workflows.
        body = self._parse_object_body()

        # REASONING: Parameter body handling enables simplified return structure and value optimization for optimization workflows.
        # Optimization workflows require parameter body handling for simplified return structure and value optimization in optimization workflows.
        # Parameter body handling supports simplified return structure, value optimization, and optimization coordination while enabling
        # comprehensive handling strategies and systematic optimization workflows.
        # Note: Removed early return to ensure consistent object structure for nested parsing

        # REASONING: Result construction enables object metadata assembly and parsing result organization for construction workflows.
        # Construction workflows require result construction for object metadata assembly and parsing result organization in construction workflows.
        # Result construction supports object metadata assembly, parsing result organization, and construction coordination while enabling
        # comprehensive construction strategies and systematic result workflows.
        result = {
            "name": full_name,  # Object type name
            "body": body or {},  # Object properties
            "line": start_line,  # Line number for errors
            "col": start_col,  # Column position for location
        }

        # REASONING: Parameter integration enables function signature inclusion and complete object representation for integration workflows.
        # Integration workflows require parameter integration for function signature inclusion and complete object representation in integration workflows.
        # Parameter integration supports function signature inclusion, complete object representation, and integration coordination while enabling
        # comprehensive integration strategies and systematic parameter workflows.
        if params:
            result["params"] = params

        # REASONING: Top-level wrapping enables proper nesting structure and parsing result consistency for wrapping workflows.
        # Wrapping workflows require top-level wrapping for proper nesting structure and parsing result consistency in wrapping workflows.
        # Top-level wrapping supports proper nesting structure, parsing result consistency, and wrapping coordination while enabling
        # comprehensive wrapping strategies and systematic structure workflows.
        if is_top_level and (
            self._current_token() is None
            or self._current_token()["value"] not in {",", ";", "="}
        ):
            return {"body": {full_name: result}}

        return result

    # REASONING: Value parsing enables configuration value processing and data type handling for value workflows.
    # Value workflows require value parsing for configuration value processing and data type handling in value workflows.
    # Value parsing supports configuration value processing, data type handling, and value coordination while enabling
    # comprehensive parsing strategies and systematic value workflows.
    def _parse_value(self):
        """Parse a value, which can be a literal, array, object, constructor call, or expression.

        Returns:
            A dictionary containing the parsed value with type information.

        Raises:
            ConfigParseError: If there's a syntax error in the value
        """
        # REASONING: Input validation enables parsing safety and error prevention for validation workflows.
        # Validation workflows require input validation for parsing safety and error prevention in validation workflows.
        # Input validation supports parsing safety, error prevention, and validation coordination while enabling
        # comprehensive validation strategies and systematic value workflows.
        if not self._current_token():
            raise self._create_syntax_error(
                "Unexpected end of input while expecting a value"
            )

        # REASONING: Expression detection enables mathematical operation recognition and calculation support for detection workflows.
        # Detection workflows require expression detection for mathematical operation recognition and calculation support in detection workflows.
        # Expression detection supports mathematical operation recognition, calculation support, and detection coordination while enabling
        # comprehensive detection strategies and systematic expression workflows.
        if self._is_expression_start():
            return self._parse_expression()

        token = self._current_token()

        # REASONING: Token type dispatch enables value type processing and data handling for dispatch workflows.
        # Dispatch workflows require token type dispatch for value type processing and data handling in dispatch workflows.
        # Token type dispatch supports value type processing, data handling, and dispatch coordination while enabling
        # comprehensive dispatch strategies and systematic value workflows.
        if token["type"] == "ENV_VAR":
            # REASONING: Environment variable processing enables dynamic configuration and runtime substitution for substitution workflows.
            # Substitution workflows require environment variable processing for dynamic configuration and runtime substitution in substitution workflows.
            # Environment variable processing supports dynamic configuration, runtime substitution, and substitution coordination while enabling
            # comprehensive processing strategies and systematic substitution workflows.
            env_token = self._consume("ENV_VAR")["value"]
            env_content = env_token[2:-1]  # Remove ${ and } delimiters

            # REASONING: Default value parsing enables fallback configuration and missing variable handling for fallback workflows.
            # Fallback workflows require default value parsing for fallback configuration and missing variable handling in fallback workflows.
            # Default value parsing supports fallback configuration, missing variable handling, and fallback coordination while enabling
            # comprehensive parsing strategies and systematic fallback workflows.
            if ":-" in env_content:
                var_name, default_value = env_content.split(":-", 1)
                if default_value.startswith('"') and default_value.endswith('"'):
                    default_value = default_value[1:-1]  # Remove quotes from default
            else:
                var_name = env_content
                default_value = None

            # REASONING: Environment resolution enables system variable access and configuration externalization for resolution workflows.
            # Resolution workflows require environment resolution for system variable access and configuration externalization in resolution workflows.
            # Environment resolution supports system variable access, configuration externalization, and resolution coordination while enabling
            # comprehensive resolution strategies and systematic environment workflows.
            env_value = os.getenv(var_name, default_value)

            if env_value is None:
                raise self._create_syntax_error(
                    f"Environment variable '{var_name}' is not set and no default provided",
                    token,
                )

            # REASONING: Type inference enables automatic type detection and value conversion for inference workflows.
            # Inference workflows require type inference for automatic type detection and value conversion in inference workflows.
            # Type inference supports automatic type detection, value conversion, and inference coordination while enabling
            # comprehensive inference strategies and systematic type workflows.
            if env_value.lower() in ("true", "false"):
                return {
                    "type": "boolean",
                    "value": env_value.lower() == "true",
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }

            # REASONING: Integer conversion enables numeric type detection and whole number support for conversion workflows.
            # Conversion workflows require integer conversion for numeric type detection and whole number support in conversion workflows.
            # Integer conversion supports numeric type detection, whole number support, and conversion coordination while enabling
            # comprehensive conversion strategies and systematic numeric workflows.
            try:
                int_value = int(env_value)
                return {
                    "type": "integer",
                    "value": int_value,
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }
            except ValueError:
                pass  # Try float conversion next

            # REASONING: Float conversion enables decimal number detection and floating-point support for float workflows.
            # Float workflows require float conversion for decimal number detection and floating-point support in float workflows.
            # Float conversion supports decimal number detection, floating-point support, and float coordination while enabling
            # comprehensive conversion strategies and systematic float workflows.
            try:
                float_value = float(env_value)
                return {
                    "type": "float",
                    "value": float_value,
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }
            except ValueError:
                pass  # Default to string type

            # REASONING: String fallback enables default type handling and text preservation for fallback workflows.
            # Fallback workflows require string fallback for default type handling and text preservation in fallback workflows.
            # String fallback supports default type handling, text preservation, and fallback coordination while enabling
            # comprehensive fallback strategies and systematic string workflows.
            return {
                "type": "string",
                "value": env_value,
                "line": token["line"],
                "col": token["col"],
                "env_var": var_name,
            }

        # REASONING: String literal processing enables text value handling and quote removal for text workflows.
        # Text workflows require string literal processing for text value handling and quote removal in text workflows.
        # String literal processing supports text value handling, quote removal, and text coordination while enabling
        # comprehensive processing strategies and systematic text workflows.
        elif token["type"] == "STRING":
            value = self._consume("STRING")["value"]
            value = value[1:-1]  # Remove surrounding quotes
            return {
                "type": "string",
                "value": value,
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Number parsing enables numeric value processing and type determination for numeric workflows.
        # Numeric workflows require number parsing for numeric value processing and type determination in numeric workflows.
        # Number parsing supports numeric value processing, type determination, and numeric coordination while enabling
        # comprehensive parsing strategies and systematic numeric workflows.
        elif token["type"] == "NUMBER":
            value = self._consume("NUMBER")["value"]
            try:
                value = int(value)  # Try integer first
                value_type = "integer"
            except ValueError:
                try:
                    value = float(value)  # Fall back to float
                    value_type = "float"
                except ValueError:
                    raise self._create_syntax_error("Invalid number format", token)

            return {
                "type": value_type,
                "value": value,
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Boolean parsing enables logical value processing and true/false determination for boolean workflows.
        # Boolean workflows require boolean parsing for logical value processing and true/false determination in boolean workflows.
        # Boolean parsing supports logical value processing, true/false determination, and boolean coordination while enabling
        # comprehensive parsing strategies and systematic boolean workflows.
        elif token["type"] == "BOOLEAN":
            value = self._consume("BOOLEAN")["value"]
            return {
                "type": "boolean",
                "value": value.lower() == "true",  # Convert to boolean
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Null identifier handling enables empty value processing and null literal support for null workflows.
        # Null workflows require identifier handling for empty value processing and null literal support in null workflows.
        # Null identifier handling supports empty value processing, null literal support, and null coordination while enabling
        # comprehensive handling strategies and systematic null workflows.
        elif token["type"] == "IDENTIFIER" and token["value"].lower() == "null":
            self._consume("IDENTIFIER", "null")
            return {
                "type": "null",
                "value": None,
                "line": token["line"],
                "col": token["col"],
            }

        # REASONING: Array literal detection enables collection processing and list structure support for array workflows.
        # Array workflows require array literal detection for collection processing and list structure support in array workflows.
        # Array literal detection supports collection processing, list structure support, and array coordination while enabling
        # comprehensive detection strategies and systematic array workflows.
        elif token["value"] == "[":
            return self._parse_array()

        # REASONING: Object literal detection enables structured data processing and nested object support for object workflows.
        # Object workflows require object literal detection for structured data processing and nested object support in object workflows.
        # Object literal detection supports structured data processing, nested object support, and object coordination while enabling
        # comprehensive detection strategies and systematic object workflows.
        elif token["value"] == "{":
            return self._parse_object(is_top_level=False)

        # REASONING: Constructor call detection enables function invocation and parameterized object creation for constructor workflows.
        # Constructor workflows require constructor call detection for function invocation and parameterized object creation in constructor workflows.
        # Constructor call detection supports function invocation, parameterized object creation, and constructor coordination while enabling
        # comprehensive detection strategies and systematic constructor workflows.
        elif (
            token["type"] == "IDENTIFIER"
            and self._current_token(1)
            and self._current_token(1)["value"] == "("
        ):
            return self._parse_constructor_call()

        # REASONING: Identifier handling enables variable reference and name resolution for identifier workflows.
        # Identifier workflows require identifier handling for variable reference and name resolution in identifier workflows.
        # Identifier handling supports variable reference, name resolution, and identifier coordination while enabling
        # comprehensive handling strategies and systematic identifier workflows.
        elif token["type"] == "IDENTIFIER":
            # REASONING: Lookahead parsing enables object constructor detection and namespaced type recognition for lookahead workflows.
            # Lookahead workflows require lookahead parsing for object constructor detection and namespaced type recognition in lookahead workflows.
            # Lookahead parsing supports object constructor detection, namespaced type recognition, and lookahead coordination while enabling
            # comprehensive parsing strategies and systematic lookahead workflows.
            lookahead = 1
            while (
                self._current_token(lookahead)
                and self._current_token(lookahead)["type"] == "NAMESPACE"
                and self._current_token(lookahead + 1)
                and self._current_token(lookahead + 1)["type"] == "IDENTIFIER"
            ):
                lookahead += 2  # Skip namespace separator and identifier

            # REASONING: Object constructor recognition enables typed object creation and structured initialization for constructor workflows.
            # Constructor workflows require object constructor recognition for typed object creation and structured initialization in constructor workflows.
            # Object constructor recognition supports typed object creation, structured initialization, and constructor coordination while enabling
            # comprehensive recognition strategies and systematic constructor workflows.
            if (
                self._current_token(lookahead)
                and self._current_token(lookahead)["value"] == "{"
            ):
                # Parse as constructor call with direct property access
                obj_result = self._parse_object(is_top_level=False)

                # REASONING: Constructor flattening enables direct property access and test compatibility for constructor workflows.
                # Constructor workflows require constructor flattening for direct property access and test compatibility in constructor workflows.
                # Constructor flattening supports direct property access, test compatibility, and constructor coordination while enabling
                # comprehensive flattening strategies and systematic constructor workflows.
                # Flatten constructor call structure: properties should be directly accessible under 'value'
                flattened_result = {
                    "type": obj_result.get("name", "object"),
                    "line": obj_result.get("line", token["line"]),
                    "col": obj_result.get("col", token["col"]),
                }

                # Merge body properties directly into the result
                if "body" in obj_result:
                    flattened_result.update(obj_result["body"])

                return flattened_result

        # REASONING: Error handling enables syntax validation and invalid token reporting for error workflows.
        # Error workflows require error handling for syntax validation and invalid token reporting in error workflows.
        # Error handling supports syntax validation, invalid token reporting, and error coordination while enabling
        # comprehensive handling strategies and systematic error workflows.
        else:
            raise self._create_syntax_error(
                f"Unexpected token: {token['type']} '{token['value']}'",
                token,
                expected="a value (string, number, boolean, null, array, object, or constructor call)",
            )

    # REASONING: Key-value pair parsing enables configuration assignment and typed declaration processing for pair workflows.
    # Pair workflows require key-value pair parsing for configuration assignment and typed declaration processing in pair workflows.
    # Key-value pair parsing supports configuration assignment, typed declaration processing, and pair coordination while enabling
    # comprehensive parsing strategies and systematic pair workflows.
    def _parse_key_value_pair(self):
        """Parse a key-value pair like 'key = value' or 'TypeName name = value'.

        Returns:
            A tuple of (key_name, value_info) if a key-value pair was parsed,
            or (None, None) if the current position doesn't contain a key-value pair.
        """
        # REASONING: Position tracking enables backtrack capability and parsing state management for tracking workflows.
        # Tracking workflows require position tracking for backtrack capability and parsing state management in tracking workflows.
        # Position tracking supports backtrack capability, parsing state management, and tracking coordination while enabling
        # comprehensive tracking strategies and systematic position workflows.
        start_pos = self.pos

        try:
            # REASONING: Type identification enables typed parameter recognition and namespace resolution for identification workflows.
            # Identification workflows require type identification for typed parameter recognition and namespace resolution in identification workflows.
            # Type identification supports typed parameter recognition, namespace resolution, and identification coordination while enabling
            # comprehensive identification strategies and systematic type workflows.
            type_name, _ = self._parse_identifier(allow_namespace=True)

            # REASONING: Type-name pair detection enables variable declaration and strong typing support for declaration workflows.
            # Declaration workflows require type-name pair detection for variable declaration and strong typing support in declaration workflows.
            # Type-name pair detection supports variable declaration, strong typing support, and declaration coordination while enabling
            # comprehensive detection strategies and systematic declaration workflows.
            if self._current_token() and self._current_token()["type"] == "IDENTIFIER":
                key_name = self._consume("IDENTIFIER")[
                    "value"
                ]  # This is a typed declaration
                is_type_declaration = True
            else:
                # REASONING: Fallback parsing enables regular key handling and simple assignment support for fallback workflows.
                # Fallback workflows require fallback parsing for regular key handling and simple assignment support in fallback workflows.
                # Fallback parsing supports regular key handling, simple assignment support, and fallback coordination while enabling
                # comprehensive parsing strategies and systematic fallback workflows.
                self.pos = start_pos  # Reset position for regular key parsing
                key_name = self._consume("IDENTIFIER")["value"]
                is_type_declaration = False

            # REASONING: Array notation detection enables collection type recognition and array parameter support for array workflows.
            # Array workflows require array notation detection for collection type recognition and array parameter support in array workflows.
            # Array notation detection supports collection type recognition, array parameter support, and array coordination while enabling
            # comprehensive detection strategies and systematic array workflows.
            is_array = False
            if self._current_token() and self._current_token()["value"] == "[":
                self._consume("PUNCTUATION", "[")
                self._consume("PUNCTUATION", "]")  # Empty brackets indicate array type
                is_array = True

            # REASONING: Assignment operator validation enables key-value relationship and assignment detection for validation workflows.
            # Validation workflows require assignment operator validation for key-value relationship and assignment detection in validation workflows.
            # Assignment operator validation supports key-value relationship, assignment detection, and validation coordination while enabling
            # comprehensive validation strategies and systematic assignment workflows.
            if not (self._current_token() and self._current_token()["value"] == "="):
                self.pos = start_pos  # Not a key-value pair, backtrack
                return None, None

            self._consume("PUNCTUATION", "=")
            value = self._parse_value()

            # REASONING: Result construction enables metadata preservation and type information packaging for construction workflows.
            # Construction workflows require result construction for metadata preservation and type information packaging in construction workflows.
            # Result construction supports metadata preservation, type information packaging, and construction coordination while enabling
            # comprehensive construction strategies and systematic result workflows.
            result = {
                "value": value,
                "is_array": is_array,
                "line": self.tokens[start_pos]["line"],
                "col": self.tokens[start_pos]["col"],
            }

            # Elevate params to same level as value for test compatibility
            if isinstance(value, dict) and "params" in value:
                result["params"] = value["params"]

            # REASONING: Type annotation inclusion enables strong typing and declaration metadata for annotation workflows.
            # Annotation workflows require type annotation inclusion for strong typing and declaration metadata in annotation workflows.
            # Type annotation inclusion supports strong typing, declaration metadata, and annotation coordination while enabling
            # comprehensive inclusion strategies and systematic annotation workflows.
            if is_type_declaration:
                result["type"] = type_name

            return key_name, result

        except SyntaxError:
            # REASONING: Error recovery enables fallback parsing and syntax error handling for recovery workflows.
            # Recovery workflows require error recovery for fallback parsing and syntax error handling in recovery workflows.
            # Error recovery supports fallback parsing, syntax error handling, and recovery coordination while enabling
            # comprehensive recovery strategies and systematic error workflows.
            self.pos = start_pos  # Rewind on syntax error

            # REASONING: Simple pair parsing enables basic key-value processing and untyped assignment for simple workflows.
            # Simple workflows require simple pair parsing for basic key-value processing and untyped assignment in simple workflows.
            # Simple pair parsing supports basic key-value processing, untyped assignment, and simple coordination while enabling
            # comprehensive parsing strategies and systematic simple workflows.
            if self._current_token() and self._current_token()["type"] == "IDENTIFIER":
                key_name = self._consume("IDENTIFIER")["value"]

                # REASONING: Assignment validation enables key-value detection and pair identification for validation workflows.
                # Validation workflows require assignment validation for key-value detection and pair identification in validation workflows.
                # Assignment validation supports key-value detection, pair identification, and validation coordination while enabling
                # comprehensive validation strategies and systematic assignment workflows.
                if not (
                    self._current_token() and self._current_token()["value"] == "="
                ):
                    self.pos = start_pos  # Not a valid pair, backtrack
                    return None, None

                self._consume("PUNCTUATION", "=")
                value = self._parse_value()

                # REASONING: Simple result packaging enables basic metadata and value wrapping for packaging workflows.
                # Packaging workflows require simple result packaging for basic metadata and value wrapping in packaging workflows.
                # Simple result packaging supports basic metadata, value wrapping, and packaging coordination while enabling
                # comprehensive packaging strategies and systematic result workflows.
                result = {
                    "value": value,
                    "line": self.tokens[start_pos]["line"],
                    "col": self.tokens[start_pos]["col"],
                }

                # Elevate params to same level as value for test compatibility
                if isinstance(value, dict) and "params" in value:
                    result["params"] = value["params"]

                return key_name, result

        # REASONING: Fallback handling enables non-pair detection and parsing continuation for fallback workflows.
        # Fallback workflows require fallback handling for non-pair detection and parsing continuation in fallback workflows.
        # Fallback handling supports non-pair detection, parsing continuation, and fallback coordination while enabling
        # comprehensive handling strategies and systematic fallback workflows.
        self.pos = start_pos  # Reset position if not a key-value pair
        return None, None

    # REASONING: Object body parsing enables structured content processing and nested data handling for body workflows.
    # Body workflows require object body parsing for structured content processing and nested data handling in body workflows.
    # Object body parsing supports structured content processing, nested data handling, and body coordination while enabling
    # comprehensive parsing strategies and systematic body workflows.
    def _parse_object_body(self) -> Dict:
        """Parse the body of an object.

        Returns:
            A dictionary containing the parsed key-value pairs and nested objects.
            Each value is a dictionary with at least 'value' and may include 'type', 'is_array', etc.
        """
        # REASONING: Body initialization enables content accumulation and result collection for initialization workflows.
        # Initialization workflows require body initialization for content accumulation and result collection in initialization workflows.
        # Body initialization supports content accumulation, result collection, and initialization coordination while enabling
        # comprehensive initialization strategies and systematic body workflows.
        body = {}

        # REASONING: Opening brace validation enables object structure detection and syntax verification for validation workflows.
        # Validation workflows require opening brace validation for object structure detection and syntax verification in validation workflows.
        # Opening brace validation supports object structure detection, syntax verification, and validation coordination while enabling
        # comprehensive validation strategies and systematic structure workflows.
        if not (self._current_token() and self._current_token()["value"] == "{"):
            return body  # Empty body if no opening brace

        self._consume("PUNCTUATION", "{")

        # REASONING: Content iteration enables member processing and object content parsing for iteration workflows.
        # Iteration workflows require content iteration for member processing and object content parsing in iteration workflows.
        # Content iteration supports member processing, object content parsing, and iteration coordination while enabling
        # comprehensive iteration strategies and systematic content workflows.
        while self._current_token() and self._current_token()["value"] != "}":
            # REASONING: Include directive detection enables file inclusion and configuration composition for inclusion workflows.
            # Inclusion workflows require include directive detection for file inclusion and configuration composition in inclusion workflows.
            # Include directive detection supports file inclusion, configuration composition, and inclusion coordination while enabling
            # comprehensive detection strategies and systematic inclusion workflows.
            if self._current_token() and self._current_token()["type"] == "INCLUDE":
                include_token = self._consume("INCLUDE")

                # REASONING: Path validation enables include file verification and path string processing for path workflows.
                # Path workflows require path validation for include file verification and path string processing in path workflows.
                # Path validation supports include file verification, path string processing, and path coordination while enabling
                # comprehensive validation strategies and systematic path workflows.
                if (
                    not self._current_token()
                    or self._current_token()["type"] != "STRING"
                ):
                    raise self._create_syntax_error(
                        "Expected string path after include directive",
                        self._current_token(),
                        "string path",
                    )

                path_token = self._consume("STRING")
                include_path = path_token["value"][1:-1]  # Remove surrounding quotes

                # REASONING: Include processing enables external file integration and configuration merging for processing workflows.
                # Processing workflows require include processing for external file integration and configuration merging in processing workflows.
                # Include processing supports external file integration, configuration merging, and processing coordination while enabling
                # comprehensive processing strategies and systematic integration workflows.
                included_data = self._process_include(include_path)

                # REASONING: Data merging enables configuration composition and included content integration for merging workflows.
                # Merging workflows require data merging for configuration composition and included content integration in merging workflows.
                # Data merging supports configuration composition, included content integration, and merging coordination while enabling
                # comprehensive merging strategies and systematic composition workflows.
                if "body" in included_data:
                    for include_key, include_value in included_data["body"].items():
                        body[include_key] = include_value  # Merge body content
                else:
                    for include_key, include_value in included_data.items():
                        body[include_key] = include_value  # Merge entire result

                # REASONING: Separator handling enables optional punctuation and syntax flexibility for separator workflows.
                # Separator workflows require separator handling for optional punctuation and syntax flexibility in separator workflows.
                # Separator handling supports optional punctuation, syntax flexibility, and separator coordination while enabling
                # comprehensive handling strategies and systematic separator workflows.
                if self._current_token() and self._current_token()["value"] in [
                    ";",
                    ",",
                ]:
                    self._consume("PUNCTUATION")  # Skip optional separator

                continue  # Process next object member

            # REASONING: Key-value pair processing enables parameter assignment and configuration member handling for pair workflows.
            # Pair workflows require key-value pair processing for parameter assignment and configuration member handling in pair workflows.
            # Key-value pair processing supports parameter assignment, configuration member handling, and pair coordination while enabling
            # comprehensive processing strategies and systematic pair workflows.
            key, value = self._parse_key_value_pair()

            if key is not None:
                body[key] = value  # Add parsed pair to body

                # REASONING: Comma handling enables optional separator processing and syntax flexibility for separator workflows.
                # Separator workflows require comma handling for optional separator processing and syntax flexibility in separator workflows.
                # Comma handling supports optional separator processing, syntax flexibility, and separator coordination while enabling
                # comprehensive handling strategies and systematic separator workflows.
                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")  # Optional comma separator
            else:
                # REASONING: Nested object parsing enables hierarchical structure handling and complex configuration support for nesting workflows.
                # Nesting workflows require nested object parsing for hierarchical structure handling and complex configuration support in nesting workflows.
                # Nested object parsing supports hierarchical structure handling, complex configuration support, and nesting coordination while enabling
                # comprehensive parsing strategies and systematic nesting workflows.
                if (
                    self._current_token()
                    and self._current_token()["type"] == "IDENTIFIER"
                ):
                    nested_obj = self._parse_object(
                        is_top_level=False
                    )  # Parse nested object

                    # REASONING: Object name handling enables keyed storage and object identification for naming workflows.
                    # Naming workflows require object name handling for keyed storage and object identification in naming workflows.
                    # Object name handling supports keyed storage, object identification, and naming coordination while enabling
                    # comprehensive handling strategies and systematic naming workflows.
                    if "name" in nested_obj:
                        obj_name = nested_obj["name"]

                        # REASONING: Duplicate key handling enables array conversion and multiple object support for duplicate workflows.
                        # Duplicate workflows require duplicate key handling for array conversion and multiple object support in duplicate workflows.
                        # Duplicate key handling supports array conversion, multiple object support, and duplicate coordination while enabling
                        # comprehensive handling strategies and systematic duplicate workflows.
                        if obj_name in body:
                            if not isinstance(body[obj_name]["value"], list):
                                body[obj_name] = {
                                    "value": [
                                        body[obj_name]["value"]
                                    ],  # Convert to array
                                    "is_array": True,
                                    "line": body[obj_name]["line"],
                                    "col": body[obj_name]["col"],
                                }
                            body[obj_name]["value"].append(
                                nested_obj
                            )  # Add to existing array
                        else:
                            body[obj_name] = {
                                "value": nested_obj,
                                "is_array": False,
                                "line": nested_obj.get("line", 0),
                                "col": nested_obj.get("col", 0),
                            }

                            # Elevate params to same level as value for test compatibility
                            if isinstance(nested_obj, dict) and "params" in nested_obj:
                                body[obj_name]["params"] = nested_obj["params"]
                else:
                    # REASONING: Token skipping enables unknown token handling and parsing robustness for skipping workflows.
                    # Skipping workflows require token skipping for unknown token handling and parsing robustness in skipping workflows.
                    # Token skipping supports unknown token handling, parsing robustness, and skipping coordination while enabling
                    # comprehensive skipping strategies and systematic token workflows.
                    if self._current_token():
                        self._consume()  # Skip unrecognized token
                    else:
                        break  # End of input reached

            # REASONING: Semicolon handling enables optional separator processing and syntax flexibility for separator workflows.
            # Separator workflows require semicolon handling for optional separator processing and syntax flexibility in separator workflows.
            # Semicolon handling supports optional separator processing, syntax flexibility, and separator coordination while enabling
            # comprehensive handling strategies and systematic separator workflows.
            if self._current_token() and self._current_token()["value"] == ";":
                self._consume("PUNCTUATION", ";")  # Optional semicolon separator

        # REASONING: Closing brace validation enables object completion and structure termination for completion workflows.
        # Completion workflows require closing brace validation for object completion and structure termination in completion workflows.
        # Closing brace validation supports object completion, structure termination, and completion coordination while enabling
        # comprehensive validation strategies and systematic completion workflows.
        self._consume("PUNCTUATION", "}")
        return body

    # REASONING: Constructor call parsing enables function-style instantiation and parameterized object creation for constructor workflows.
    # Constructor workflows require constructor call parsing for function-style instantiation and parameterized object creation in constructor workflows.
    # Constructor call parsing supports function-style instantiation, parameterized object creation, and constructor coordination while enabling
    # comprehensive parsing strategies and systematic constructor workflows.
    def _parse_constructor_call(self):
        """Parse a constructor-style call like TypeName(arg1, arg2, ...)"""
        # REASONING: Type name identification enables constructor type resolution and namespace support for identification workflows.
        # Identification workflows require type name identification for constructor type resolution and namespace support in identification workflows.
        # Type name identification supports constructor type resolution, namespace support, and identification coordination while enabling
        # comprehensive identification strategies and systematic type workflows.
        type_name, _ = self._parse_identifier()

        # REASONING: Argument list processing enables parameter collection and constructor input handling for argument workflows.
        # Argument workflows require argument list processing for parameter collection and constructor input handling in argument workflows.
        # Argument list processing supports parameter collection, constructor input handling, and argument coordination while enabling
        # comprehensive processing strategies and systematic argument workflows.
        args = []
        if self._current_token() and self._current_token()["value"] == "(":
            self._consume("PUNCTUATION", "(")

            # REASONING: Argument iteration enables parameter parsing and value collection for iteration workflows.
            # Iteration workflows require argument iteration for parameter parsing and value collection in iteration workflows.
            # Argument iteration supports parameter parsing, value collection, and iteration coordination while enabling
            # comprehensive iteration strategies and systematic argument workflows.
            while self._current_token() and self._current_token()["value"] != ")":
                arg_value = self._parse_value()  # Parse each argument
                args.append(arg_value)

                # REASONING: Comma handling enables argument separation and parameter list processing for separation workflows.
                # Separation workflows require comma handling for argument separation and parameter list processing in separation workflows.
                # Comma handling supports argument separation, parameter list processing, and separation coordination while enabling
                # comprehensive handling strategies and systematic separation workflows.
                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")  # Optional comma separator

            self._consume("PUNCTUATION", ")")  # Close parameter list

        # REASONING: Body parsing enables constructor body processing and structured initialization for body workflows.
        # Body workflows require body parsing for constructor body processing and structured initialization in body workflows.
        # Body parsing supports constructor body processing, structured initialization, and body coordination while enabling
        # comprehensive parsing strategies and systematic body workflows.
        body = {}
        if self._current_token() and self._current_token()["value"] == "{":
            body = self._parse_object_body()  # Parse optional constructor body

        # REASONING: Constructor result construction enables typed object creation and metadata packaging for construction workflows.
        # Construction workflows require constructor result construction for typed object creation and metadata packaging in construction workflows.
        # Constructor result construction supports typed object creation, metadata packaging, and construction coordination while enabling
        # comprehensive construction strategies and systematic result workflows.
        return {"type": type_name, "body": body}

    # REASONING: Array parsing enables collection processing and list literal support for array workflows.
    # Array workflows require array parsing for collection processing and list literal support in array workflows.
    # Array parsing supports collection processing, list literal support, and array coordination while enabling
    # comprehensive parsing strategies and systematic array workflows.
    def _parse_array(self) -> List:
        """Parse an array literal.

        Returns:
            List: The parsed array of values

        Raises:
            ConfigParseError: If there's a syntax error in the array
        """
        # REASONING: Array bracket validation enables array detection and syntax verification for validation workflows.
        # Validation workflows require array bracket validation for array detection and syntax verification in validation workflows.
        # Array bracket validation supports array detection, syntax verification, and validation coordination while enabling
        # comprehensive validation strategies and systematic array workflows.
        start_token = self._current_token()
        if start_token is None or start_token["value"] != "[":
            raise self._create_syntax_error(
                message="Expected '[' to start array", token=start_token, expected="'['"
            )

        self._consume("PUNCTUATION", "[")
        elements = []

        try:
            # REASONING: Empty array handling enables null collection support and zero-element processing for empty workflows.
            # Empty workflows require empty array handling for null collection support and zero-element processing in empty workflows.
            # Empty array handling supports null collection support, zero-element processing, and empty coordination while enabling
            # comprehensive handling strategies and systematic empty workflows.
            if self._current_token() and self._current_token()["value"] == "]":
                self._consume("PUNCTUATION", "]")  # Empty array case
                return elements

            # REASONING: First element parsing enables initial value processing and array population for element workflows.
            # Element workflows require first element parsing for initial value processing and array population in element workflows.
            # First element parsing supports initial value processing, array population, and element coordination while enabling
            # comprehensive parsing strategies and systematic element workflows.
            elements.append(self._parse_value())  # Parse first element

            # REASONING: Additional element iteration enables multi-value processing and comma-separated parsing for iteration workflows.
            # Iteration workflows require additional element iteration for multi-value processing and comma-separated parsing in iteration workflows.
            # Additional element iteration supports multi-value processing, comma-separated parsing, and iteration coordination while enabling
            # comprehensive iteration strategies and systematic element workflows.
            while self._current_token() and self._current_token()["value"] == ",":
                self._consume("PUNCTUATION", ",")  # Comma separator

                # REASONING: Trailing comma handling enables flexible syntax and optional separator support for trailing workflows.
                # Trailing workflows require trailing comma handling for flexible syntax and optional separator support in trailing workflows.
                # Trailing comma handling supports flexible syntax, optional separator support, and trailing coordination while enabling
                # comprehensive handling strategies and systematic trailing workflows.
                if self._current_token() and self._current_token()["value"] == "]":
                    break  # Allow trailing comma

                elements.append(self._parse_value())  # Parse next element

            # REASONING: Closing bracket validation enables array completion and structure termination for completion workflows.
            # Completion workflows require closing bracket validation for array completion and structure termination in completion workflows.
            # Closing bracket validation supports array completion, structure termination, and completion coordination while enabling
            # comprehensive validation strategies and systematic completion workflows.
            if not self._current_token() or self._current_token()["value"] != "]":
                raise self._create_syntax_error(
                    message="Expected ']' to close array",
                    token=self._current_token(),
                    expected="']' or ','",
                )

            self._consume("PUNCTUATION", "]")
            return elements

        except ConfigParseError as e:
            # REASONING: Custom error preservation enables specific error handling and diagnostic information retention for preservation workflows.
            # Preservation workflows require custom error preservation for specific error handling and diagnostic information retention in preservation workflows.
            # Custom error preservation supports specific error handling, diagnostic information retention, and preservation coordination while enabling
            # comprehensive preservation strategies and systematic error workflows.
            raise e from None  # Re-raise custom errors without modification

        except Exception as e:
            # REASONING: Exception wrapping enables generic error handling and consistent error format for wrapping workflows.
            # Wrapping workflows require exception wrapping for generic error handling and consistent error format in wrapping workflows.
            # Exception wrapping supports generic error handling, consistent error format, and wrapping coordination while enabling
            # comprehensive wrapping strategies and systematic exception workflows.
            raise self._create_syntax_error(
                message=f"Array parsing failed: {str(e)}", token=self._current_token()
            ) from e

    def _parse_enum_values_array(self) -> List[str]:
        """Parse an enum values array and return simple string values."""
        start_token = self._current_token()
        if start_token is None or start_token["value"] != "[":
            raise self._create_syntax_error(
                "Expected '[' for enum values array", start_token, "'['"
            )

        self._consume("PUNCTUATION", "[")
        values = []

        # Handle empty array
        if self._current_token() and self._current_token()["value"] == "]":
            self._consume("PUNCTUATION", "]")
            return values

        # Parse first value
        value_obj = self._parse_value()
        values.append(value_obj["value"])  # Extract just the value, not the full object

        # Parse additional values
        while self._current_token() and self._current_token()["value"] == ",":
            self._consume("PUNCTUATION", ",")

            # Handle trailing comma
            if self._current_token() and self._current_token()["value"] == "]":
                break

            value_obj = self._parse_value()
            values.append(value_obj["value"])  # Extract just the value

        if not self._current_token() or self._current_token()["value"] != "]":
            raise self._create_syntax_error(
                "Expected ']' to close enum values array", self._current_token(), "']'"
            )

        self._consume("PUNCTUATION", "]")
        return values

    # REASONING: Enum definition parsing enables type definition and constraint specification for enum workflows.
    # Enum workflows require enum definition parsing for type definition and constraint specification in enum workflows.
    # Enum definition parsing supports type definition, constraint specification, and enum coordination while enabling
    # comprehensive enum strategies and systematic type workflows.
    def _parse_enum_definition(self) -> Tuple[str, Dict]:
        """Parse an enum definition: enum::EnumName { values = [...], default = "..." }"""
        try:
            # REASONING: Enum keyword consumption enables syntax validation and parsing progression for parsing workflows.
            # Parsing workflows require enum keyword consumption for syntax validation and parsing progression in parsing workflows.
            # Enum keyword consumption supports syntax validation, parsing progression, and parsing coordination while enabling
            # comprehensive consumption strategies and systematic enum workflows.
            self._consume("ENUM")

            # REASONING: Namespace separator validation enables proper enum syntax and type system integration for validation workflows.
            # Validation workflows require namespace separator validation for proper enum syntax and type system integration in validation workflows.
            # Namespace separator validation supports proper enum syntax, type system integration, and validation coordination while enabling
            # comprehensive validation strategies and systematic namespace workflows.
            if not self._current_token() or self._current_token()["value"] != "::":
                raise self._create_syntax_error(
                    "Expected '::' after 'enum'", self._current_token(), "'::'"
                )
            self._consume("NAMESPACE", "::")

            # REASONING: Enum name extraction enables type identification and namespace organization for identification workflows.
            # Identification workflows require enum name extraction for type identification and namespace organization in identification workflows.
            # Enum name extraction supports type identification, namespace organization, and identification coordination while enabling
            # comprehensive extraction strategies and systematic naming workflows.
            if (
                not self._current_token()
                or self._current_token()["type"] != "IDENTIFIER"
            ):
                raise self._create_syntax_error(
                    "Expected enum name after 'enum::'",
                    self._current_token(),
                    "identifier",
                )
            enum_name = self._consume("IDENTIFIER")["value"]

            # REASONING: Opening brace validation enables block structure and parameter parsing for structure workflows.
            # Structure workflows require opening brace validation for block structure and parameter parsing in structure workflows.
            # Opening brace validation supports block structure, parameter parsing, and structure coordination while enabling
            # comprehensive validation strategies and systematic structure workflows.
            if not self._current_token() or self._current_token()["value"] != "{":
                raise self._create_syntax_error(
                    "Expected '{' to start enum body", self._current_token(), "'{'"
                )
            self._consume("PUNCTUATION", "{")

            # REASONING: Enum properties parsing enables value specification and configuration handling for property workflows.
            # Property workflows require enum properties parsing for value specification and configuration handling in property workflows.
            # Enum properties parsing supports value specification, configuration handling, and property coordination while enabling
            # comprehensive parsing strategies and systematic property workflows.
            enum_data = {
                "type": "enum_definition",
                "name": enum_name,
                "values": [],
                "default": None,
            }

            # Parse enum properties (values and default)
            while self._current_token() and self._current_token()["value"] != "}":
                # REASONING: Property name validation enables enum configuration and parameter identification for validation workflows.
                # Validation workflows require property name validation for enum configuration and parameter identification in validation workflows.
                # Property name validation supports enum configuration, parameter identification, and validation coordination while enabling
                # comprehensive validation strategies and systematic property workflows.
                if (
                    not self._current_token()
                    or self._current_token()["type"] != "IDENTIFIER"
                ):
                    raise self._create_syntax_error(
                        "Expected property name in enum definition",
                        self._current_token(),
                        "'values' or 'default'",
                    )

                prop_name = self._consume("IDENTIFIER")["value"]

                # REASONING: Assignment operator validation enables property assignment and syntax compliance for assignment workflows.
                # Assignment workflows require assignment operator validation for property assignment and syntax compliance in assignment workflows.
                # Assignment operator validation supports property assignment, syntax compliance, and assignment coordination while enabling
                # comprehensive validation strategies and systematic assignment workflows.
                if not self._current_token() or self._current_token()["value"] != "=":
                    raise self._create_syntax_error(
                        "Expected '=' after enum property name",
                        self._current_token(),
                        "'='",
                    )
                self._consume("PUNCTUATION", "=")

                # REASONING: Property value parsing enables enum configuration and constraint specification for value workflows.
                # Value workflows require property value parsing for enum configuration and constraint specification in value workflows.
                # Property value parsing supports enum configuration, constraint specification, and value coordination while enabling
                # comprehensive parsing strategies and systematic value workflows.
                if prop_name == "values":
                    # REASONING: Values array parsing enables enum option specification and constraint definition for array workflows.
                    # Array workflows require values array parsing for enum option specification and constraint definition in array workflows.
                    # Values array parsing supports enum option specification, constraint definition, and array coordination while enabling
                    # comprehensive parsing strategies and systematic array workflows.
                    enum_data["values"] = self._parse_enum_values_array()
                elif prop_name == "default":
                    # REASONING: Default value parsing enables fallback specification and value initialization for default workflows.
                    # Default workflows require default value parsing for fallback specification and value initialization in default workflows.
                    # Default value parsing supports fallback specification, value initialization, and default coordination while enabling
                    # comprehensive parsing strategies and systematic default workflows.
                    default_obj = self._parse_value()
                    enum_data["default"] = default_obj[
                        "value"
                    ]  # Extract just the value
                else:
                    raise self._create_syntax_error(
                        f"Unknown enum property: {prop_name}",
                        self._current_token(),
                        "'values' or 'default'",
                    )

                # REASONING: Optional comma handling enables flexible syntax and property separation for separation workflows.
                # Separation workflows require optional comma handling for flexible syntax and property separation in separation workflows.
                # Optional comma handling supports flexible syntax, property separation, and separation coordination while enabling
                # comprehensive handling strategies and systematic separation workflows.
                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")

            # REASONING: Closing brace validation enables block completion and structure termination for completion workflows.
            # Completion workflows require closing brace validation for block completion and structure termination in completion workflows.
            # Closing brace validation supports block completion, structure termination, and completion coordination while enabling
            # comprehensive validation strategies and systematic completion workflows.
            if not self._current_token() or self._current_token()["value"] != "}":
                raise self._create_syntax_error(
                    "Expected '}' to close enum body", self._current_token(), "'}'"
                )
            self._consume("PUNCTUATION", "}")

            # Validate that enum has required values property with actual values
            if "values" not in enum_data or not enum_data["values"]:
                raise self._create_syntax_error(
                    "Enum definition must include 'values' property with at least one value",
                    self._current_token(),
                    "values = [...]",
                )

            return enum_name, enum_data

        except ConfigParseError as e:
            # REASONING: Custom error preservation enables specific error handling and diagnostic information retention for preservation workflows.
            # Preservation workflows require custom error preservation for specific error handling and diagnostic information retention in preservation workflows.
            # Custom error preservation supports specific error handling, diagnostic information retention, and preservation coordination while enabling
            # comprehensive preservation strategies and systematic error workflows.
            raise e from None

        except Exception as e:
            # REASONING: Exception wrapping enables generic error handling and consistent error format for wrapping workflows.
            # Wrapping workflows require exception wrapping for generic error handling and consistent error format in wrapping workflows.
            # Exception wrapping supports generic error handling, consistent error format, and wrapping coordination while enabling
            # comprehensive wrapping strategies and systematic exception workflows.
            raise self._create_syntax_error(
                message=f"Error parsing enum definition: {str(e)}",
                token=self._current_token(),
                expected="enum definition syntax",
            ) from e


# REASONING: Loads function enables string-based configuration parsing and API simplification for parsing workflows.
# Parsing workflows require loads function for string-based configuration parsing and API simplification in parsing workflows.
# Loads function supports string-based configuration parsing, API simplification, and parsing coordination while enabling
# comprehensive function strategies and systematic configuration workflows.
def loads(text: str, base_path: str = None, included_files: Set[Path] = None) -> Dict:
    """Parse a cfgpp configuration string into a Python dictionary.

    Args:
        text: The configuration text to parse
        base_path: Base path for resolving include directives (defaults to current directory)
        included_files: Set of already included files to prevent circular includes

    Returns:
        Dict: The parsed configuration as a Python dictionary

    Raises:
        ConfigParseError: If there's a syntax error in the configuration
    """
    # REASONING: Lexer integration enables tokenization dependency and modular parsing architecture for integration workflows.
    # Integration workflows require lexer integration for tokenization dependency and modular parsing architecture in integration workflows.
    # Lexer integration supports tokenization dependency, modular parsing architecture, and integration coordination while enabling
    # comprehensive integration strategies and systematic lexer workflows.
    from .lexer import lex

    # REASONING: Tokenization processing enables text-to-token conversion and parsing preparation for tokenization workflows.
    # Tokenization workflows require tokenization processing for text-to-token conversion and parsing preparation in tokenization workflows.
    # Tokenization processing supports text-to-token conversion, parsing preparation, and tokenization coordination while enabling
    # comprehensive processing strategies and systematic tokenization workflows.
    tokens = lex(text)

    # REASONING: Base path resolution enables include path handling and file system navigation for resolution workflows.
    # Resolution workflows require base path resolution for include path handling and file system navigation in resolution workflows.
    # Base path resolution supports include path handling, file system navigation, and resolution coordination while enabling
    # comprehensive resolution strategies and systematic path workflows.
    base_path_obj = Path(base_path) if base_path else Path.cwd()

    # REASONING: Parser instantiation enables parsing context creation and configuration processing for instantiation workflows.
    # Instantiation workflows require parser instantiation for parsing context creation and configuration processing in instantiation workflows.
    # Parser instantiation supports parsing context creation, configuration processing, and instantiation coordination while enabling
    # comprehensive instantiation strategies and systematic parser workflows.
    parser = Parser(tokens, text.splitlines(), base_path_obj, included_files)

    try:
        # REASONING: Parse execution enables configuration processing and structured data generation for execution workflows.
        # Execution workflows require parse execution for configuration processing and structured data generation in execution workflows.
        # Parse execution supports configuration processing, structured data generation, and execution coordination while enabling
        # comprehensive execution strategies and systematic parsing workflows.
        return parser.parse()
    except Exception as e:
        # REASONING: Exception handling enables error classification and consistent error reporting for handling workflows.
        # Handling workflows require exception handling for error classification and consistent error reporting in handling workflows.
        # Exception handling supports error classification, consistent error reporting, and handling coordination while enabling
        # comprehensive handling strategies and systematic exception workflows.
        if isinstance(e, ConfigParseError):
            raise  # Re-raise custom errors as-is
        raise ConfigParseError(f"Error parsing configuration: {str(e)}") from e


# REASONING: Load function enables file-based configuration parsing and filesystem integration for file workflows.
# File workflows require load function for file-based configuration parsing and filesystem integration in file workflows.
# Load function supports file-based configuration parsing, filesystem integration, and file coordination while enabling
# comprehensive function strategies and systematic file workflows.
def load(file_path: str) -> Dict:
    """Parse a cfgpp configuration file into a Python dictionary."""
    # REASONING: Path object creation enables file path handling and filesystem abstraction for path workflows.
    # Path workflows require path object creation for file path handling and filesystem abstraction in path workflows.
    # Path object creation supports file path handling, filesystem abstraction, and path coordination while enabling
    # comprehensive creation strategies and systematic path workflows.
    file_path_obj = Path(file_path)

    # REASONING: Circular include prevention enables infinite recursion protection and include safety for prevention workflows.
    # Prevention workflows require circular include prevention for infinite recursion protection and include safety in prevention workflows.
    # Circular include prevention supports infinite recursion protection, include safety, and prevention coordination while enabling
    # comprehensive prevention strategies and systematic include workflows.
    included_files = {file_path_obj.resolve()}

    # REASONING: File reading enables content access and text extraction for reading workflows.
    # Reading workflows require file reading for content access and text extraction in reading workflows.
    # File reading supports content access, text extraction, and reading coordination while enabling
    # comprehensive reading strategies and systematic file workflows.
    with open(file_path_obj, "r", encoding="utf-8") as f:
        return loads(f.read(), str(file_path_obj.parent), included_files)
