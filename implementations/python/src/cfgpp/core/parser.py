"""
A simple parser for the CFG++ configuration format.

"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from .lexer import lex, Token, LexerError


class ConfigParseError(Exception):
    """Exception raised when configuration parsing fails."""

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


class Parser:
    """Parser for CFG++ configuration files."""

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

    def parse(self, text: Optional[str] = None) -> Dict:
        """Parse the given cfgpp configuration text into a Python dictionary.

        Args:
            text: Optional text to parse. If not provided, tokens must be set in the constructor.

        Returns:
            Dict: The parsed configuration

        Raises:
            ValueError: If no tokens are provided and no text is given to parse
        """
        # Input validation and tokenization support proper parsing setup, input preparation, and setup coordination while enabling
        if text is not None:
            self.tokens = self._tokenize(text)
        elif not self.tokens:
            raise ValueError("No tokens provided and no text to parse")

        self.pos = 0  # Reset parser position

        if (
            self._current_token()
            and self._current_token()["type"] == "IDENTIFIER"
            and self._current_token(1)
            and self._current_token(1)["value"] == "="
        ):
            # Parse as a simple key-value pair
            key, value = self._parse_key_value_pair()
            return {"body": {key: value}}

        body = {}
        while self._current_token():
            if self._current_token()["type"] == "ENUM":
                enum_name, enum_data = self._parse_enum_definition()
                body[enum_name] = enum_data
            elif self._current_token()["type"] == "INCLUDE":
                include_token = self._consume("INCLUDE")

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

                # Include processing and merging support file composition, configuration integration, and integration coordination while enabling
                included_data = self._process_include(include_path)

                # Merge included data into the current body
                if "body" in included_data:
                    for include_key, include_value in included_data["body"].items():
                        body[include_key] = include_value

            elif self._current_token()["type"] == "IDENTIFIER":
                obj = self._parse_object(is_top_level=True)
                if "body" in obj:
                    # Merge all objects from the parsed result
                    for obj_key, obj_value in obj["body"].items():
                        body[obj_key] = obj_value
                else:
                    if "name" in obj:
                        body[obj["name"]] = obj
                    else:
                        # Use a generated key if no name
                        body[f"object_{len(body)}"] = obj
            else:
                raise self._create_syntax_error(
                    f"Unexpected token at top level: {self._current_token()['type']} '{self._current_token()['value']}'",
                    self._current_token(),
                    "object name or include directive",
                )

        return {"body": body}

    def _tokenize(self, text: str) -> List[Dict]:
        """Convert the input text into a list of tokens."""
        # Token patterns support syntax recognition, lexical element identification, and pattern coordination while enabling
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

        token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)

        # Token collection and position tracking support parsing state management, location awareness, and tracking coordination while enabling
        tokens = []
        line_num = 1  # Current line for error reporting
        line_start = 0  # Line start position for column calculation

        for mo in re.finditer(token_regex, text, re.MULTILINE | re.DOTALL):
            kind = mo.lastgroup  # Token type from named group
            value = mo.group()  # Matched text content
            column = mo.start() - line_start  # Column position

            if kind == "NEWLINE":
                line_start = mo.end()  # Update line start position
                line_num += 1  # Increment line counter
                continue
            elif kind == "WHITESPACE":
                continue  # Skip whitespace tokens
            elif kind == "COMMENT":
                continue  # Skip comment tokens
            elif kind == "OTHER":
                raise SyntaxError(
                    f"Unexpected character: {value} at line {line_num}, column {column + 1}"
                )

            tokens.append(
                {
                    "type": kind,  # Token category
                    "value": value,  # Matched text
                    "line": line_num,  # Line number for errors
                    "col": column + 1,  # Column position (1-based)
                }
            )

        return tokens

    def _current_token(self, offset: int = 0) -> Optional[Dict]:
        """Get the current token with an optional offset.

        Returns:
            The token at the current position + offset, or None if beyond the end
        """
        # Position calculation and bounds checking support safe token access, parsing state management, and access coordination while enabling
        pos = self.pos + offset
        if 0 <= pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _create_syntax_error(
        self, message: str, token: Optional[Dict] = None, expected: Optional[str] = None
    ) -> ConfigParseError:
        """Create a syntax error with detailed context information."""
        return ConfigParseError(message, token, expected)

    def _process_include(self, include_path: str) -> Dict[str, Any]:
        """Process an include/import directive."""
        if not include_path.endswith(".cfgpp"):
            include_path += ".cfgpp"  # Add default extension

        resolved_path = (self.base_path / include_path).resolve()

        if resolved_path in self.included_files:
            raise ConfigParseError(f"Circular include detected: {include_path}")

        if not resolved_path.exists():
            raise ConfigParseError(f"Include file not found: {include_path}")

        # File reading and error handling support content loading, failure management, and loading coordination while enabling
        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                included_content = f.read()
        except IOError as e:
            raise ConfigParseError(f"Failed to read include file '{include_path}': {e}")

        new_included_files = self.included_files.copy()  # Track included files
        new_included_files.add(resolved_path)

        return loads(included_content, str(resolved_path.parent), new_included_files)

    def _is_expression_start(self) -> bool:
        """Check if the current position starts an expression by looking ahead for operators."""
        original_pos = self.pos

        try:
            if not self._current_token():
                return False

            if self._current_token()["value"] == "(":
                return True

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
            self.pos = original_pos

    def _parse_expression(self) -> Dict[str, Any]:
        """Parse a mathematical or string expression."""
        return self._parse_addition()

    def _parse_addition(self) -> Dict[str, Any]:
        """Parse addition and subtraction operations."""
        left = self._parse_multiplication()  # Higher precedence first

        while (
            self._current_token()
            and self._current_token()["type"] == "OPERATOR"
            and self._current_token()["value"] in ["+", "-"]
        ):
            op_token = self._consume("OPERATOR")
            right = self._parse_multiplication()

            left = self._evaluate_binary_op(left, op_token["value"], right)

        return left

    def _parse_multiplication(self) -> Dict[str, Any]:
        """Parse multiplication and division operations."""
        left = self._parse_primary()  # Highest precedence

        while (
            self._current_token()
            and self._current_token()["type"] == "OPERATOR"
            and self._current_token()["value"] in ["*", "/"]
        ):
            op_token = self._consume("OPERATOR")
            right = self._parse_primary()

            left = self._evaluate_binary_op(left, op_token["value"], right)

        return left

    def _parse_primary(self) -> Dict[str, Any]:
        """Parse primary expressions (numbers, strings, parenthesized expressions)."""
        token = self._current_token()

        if not token:
            raise self._create_syntax_error("Unexpected end of input in expression")

        if token["value"] == "(":
            self._consume("PUNCTUATION", "(")
            result = self._parse_expression()  # Recursive expression parsing
            if not self._current_token() or self._current_token()["value"] != ")":
                raise self._create_syntax_error(
                    "Expected ')' to close expression", self._current_token(), "')'"
                )
            self._consume("PUNCTUATION", ")")
            return result

        if token["type"] == "STRING":
            value = self._consume("STRING")["value"]
            value = value[1:-1]  # Remove surrounding quotes
            return {
                "type": "string",
                "value": value,
                "line": token["line"],
                "col": token["col"],
            }

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

        elif token["type"] == "BOOLEAN":
            value = self._consume("BOOLEAN")["value"]
            return {
                "type": "boolean",
                "value": value.lower() == "true",  # Convert to boolean
                "line": token["line"],
                "col": token["col"],
            }

        elif token["type"] == "ENV_VAR":
            env_token = self._consume("ENV_VAR")["value"]
            env_content = env_token[2:-1]  # Remove ${ and } delimiters

            if ":-" in env_content:
                var_name, default_value = env_content.split(":-", 1)
                if default_value.startswith('"') and default_value.endswith('"'):
                    default_value = default_value[1:-1]  # Remove quotes from default
            else:
                var_name = env_content
                default_value = None

            env_value = os.getenv(var_name, default_value)
            if env_value is None:
                raise self._create_syntax_error(
                    f"Environment variable '{var_name}' is not set and no default provided",
                    token,
                )

            if env_value.lower() in ("true", "false"):
                return {
                    "type": "boolean",
                    "value": env_value.lower() == "true",
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }

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

            return {
                "type": "string",
                "value": env_value,
                "line": token["line"],
                "col": token["col"],
                "env_var": var_name,
            }

        elif token["type"] == "IDENTIFIER" and token["value"].lower() == "null":
            self._consume("IDENTIFIER", "null")
            return {
                "type": "null",
                "value": None,
                "line": token["line"],
                "col": token["col"],
            }

        raise self._create_syntax_error(
            f"Unexpected token in expression: {token['value']}", token
        )

    def _evaluate_binary_op(
        self, left: Dict[str, Any], operator: str, right: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a binary operation between two values."""
        left_val = left["value"]
        right_val = right["value"]
        left_type = left["type"]
        right_type = right["type"]

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

        # Numeric operations support mathematical computation, arithmetic evaluation, and numeric coordination while enabling
        if left_type in ["integer", "float"] and right_type in ["integer", "float"]:
            try:
                if operator == "+":
                    result_val = left_val + right_val
                elif operator == "-":
                    result_val = left_val - right_val
                elif operator == "*":
                    result_val = left_val * right_val
                elif operator == "/":
                    if right_val == 0:
                        raise self._create_syntax_error(
                            "Division by zero in expression"
                        )
                    result_val = left_val / right_val
                else:
                    raise self._create_syntax_error(f"Unsupported operator: {operator}")

                result_type = "float" if isinstance(result_val, float) else "integer"

                return {
                    "type": result_type,
                    "value": result_val,
                    "line": left.get("line", 1),
                    "col": left.get("col", 1),
                    "expression": True,
                }
            except Exception as e:
                raise self._create_syntax_error(
                    f"Error in expression evaluation: {str(e)}"
                )

        raise self._create_syntax_error(
            f"Cannot apply operator '{operator}' to {left_type} and {right_type}"
        )

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
        token = self._current_token()

        if token is None:
            expected = []
            if expected_type:
                expected.append(f"type '{expected_type}'")
            if expected_value:
                expected.append(f"value '{expected_value}'")
            expected_str = " or ".join(expected) or "token"

            raise self._create_syntax_error(
                message=f"Unexpected end of input, expected {expected_str}",
                expected=expected_str,
            )

        if expected_type is not None and token["type"] != expected_type:
            raise self._create_syntax_error(
                message=f"Got unexpected token type '{token['type']}'",
                token=token,
                expected=f"{expected_type}",
            )

        if expected_value is not None and token["value"] != expected_value:
            raise self._create_syntax_error(
                message=f"Got unexpected value '{token['value']}'",
                token=token,
                expected=f"'{expected_value}'",
            )

        self.pos += 1
        return token

    def _parse_parameter(self) -> tuple:
        """Parse a single parameter definition.

        Returns:
            A tuple containing:
            - The parameter name as a string
            - A dictionary with parameter information (type, is_array, value, line, col, etc.)
        """

        param_type, type_parts = self._parse_identifier(allow_namespace=True)

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

        if self._current_token() and self._current_token()["value"] == "[":
            self._consume("PUNCTUATION", "[")
            self._consume("PUNCTUATION", "]")
            is_array = True

        param_name = self._consume("IDENTIFIER")

        default_value = None
        if self._current_token() and self._current_token()["value"] == "=":
            self._consume("PUNCTUATION", "=")
            default_value = self._parse_value()

        param_info = {
            "type": param_type,  # Parameter type name
            "is_array": is_array,  # Array type flag
            "is_enum_type": is_enum_type,  # Enum type flag for constraint validation
            "value": default_value,  # Default value if specified
            "line": type_parts[0]["line"],  # Line number for error reporting
            "col": type_parts[0]["col"],  # Column position for location
        }

        if self._current_token() and self._current_token()["value"] == "(":
            param_info["nested"] = self._parse_object()

        return param_name["value"], param_info

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
        if not self._current_token() or self._current_token()["type"] != "IDENTIFIER":
            token = self._current_token()
            raise self._create_syntax_error(
                message="Expected an identifier", token=token, expected="identifier"
            )

        name_parts = [self._consume("IDENTIFIER")]

        if allow_namespace:
            while (
                self._current_token() and self._current_token()["type"] == "NAMESPACE"
            ):
                namespace_token = self._current_token()
                self._consume("NAMESPACE")

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

        full_name = "".join(
            part["value"] if isinstance(part, dict) else part for part in name_parts
        )
        return full_name, [part for part in name_parts if isinstance(part, dict)]

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
        full_name, name_parts = self._parse_identifier()

        start_line = name_parts[0]["line"]
        start_col = name_parts[0]["col"]

        params = {}
        if self._current_token() and self._current_token()["value"] == "(":
            self._consume("PUNCTUATION", "(")

            while self._current_token() and self._current_token()["value"] != ")":
                param_name, param_info = self._parse_parameter()
                params[param_name] = param_info

                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")
                else:
                    break

            self._consume("PUNCTUATION", ")")

        body = self._parse_object_body()

        # Note: Removed early return to ensure consistent object structure for nested parsing

        result = {
            "name": full_name,  # Object type name
            "body": body or {},  # Object properties
            "line": start_line,  # Line number for errors
            "col": start_col,  # Column position for location
        }

        if params:
            result["params"] = params

        if is_top_level and (
            self._current_token() is None
            or self._current_token()["value"] not in {",", ";", "="}
        ):
            return {"body": {full_name: result}}

        return result

    def _parse_value(self):
        """Parse a value, which can be a literal, array, object, constructor call, or expression.

        Returns:
            A dictionary containing the parsed value with type information.

        Raises:
            ConfigParseError: If there's a syntax error in the value
        """
        if not self._current_token():
            raise self._create_syntax_error(
                "Unexpected end of input while expecting a value"
            )

        if self._is_expression_start():
            return self._parse_expression()

        token = self._current_token()

        if token["type"] == "ENV_VAR":
            env_token = self._consume("ENV_VAR")["value"]
            env_content = env_token[2:-1]  # Remove ${ and } delimiters

            if ":-" in env_content:
                var_name, default_value = env_content.split(":-", 1)
                if default_value.startswith('"') and default_value.endswith('"'):
                    default_value = default_value[1:-1]  # Remove quotes from default
            else:
                var_name = env_content
                default_value = None

            env_value = os.getenv(var_name, default_value)

            if env_value is None:
                raise self._create_syntax_error(
                    f"Environment variable '{var_name}' is not set and no default provided",
                    token,
                )

            if env_value.lower() in ("true", "false"):
                return {
                    "type": "boolean",
                    "value": env_value.lower() == "true",
                    "line": token["line"],
                    "col": token["col"],
                    "env_var": var_name,
                }

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

            return {
                "type": "string",
                "value": env_value,
                "line": token["line"],
                "col": token["col"],
                "env_var": var_name,
            }

        elif token["type"] == "STRING":
            value = self._consume("STRING")["value"]
            value = value[1:-1]  # Remove surrounding quotes
            return {
                "type": "string",
                "value": value,
                "line": token["line"],
                "col": token["col"],
            }

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

        elif token["type"] == "BOOLEAN":
            value = self._consume("BOOLEAN")["value"]
            return {
                "type": "boolean",
                "value": value.lower() == "true",  # Convert to boolean
                "line": token["line"],
                "col": token["col"],
            }

        elif token["type"] == "IDENTIFIER" and token["value"].lower() == "null":
            self._consume("IDENTIFIER", "null")
            return {
                "type": "null",
                "value": None,
                "line": token["line"],
                "col": token["col"],
            }

        elif token["value"] == "[":
            return self._parse_array()

        elif token["value"] == "{":
            return self._parse_object(is_top_level=False)

        elif (
            token["type"] == "IDENTIFIER"
            and self._current_token(1)
            and self._current_token(1)["value"] == "("
        ):
            return self._parse_constructor_call()

        elif token["type"] == "IDENTIFIER":
            lookahead = 1
            while (
                self._current_token(lookahead)
                and self._current_token(lookahead)["type"] == "NAMESPACE"
                and self._current_token(lookahead + 1)
                and self._current_token(lookahead + 1)["type"] == "IDENTIFIER"
            ):
                lookahead += 2  # Skip namespace separator and identifier

            if (
                self._current_token(lookahead)
                and self._current_token(lookahead)["value"] == "{"
            ):
                # Parse as constructor call with direct property access
                obj_result = self._parse_object(is_top_level=False)

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

        else:
            raise self._create_syntax_error(
                f"Unexpected token: {token['type']} '{token['value']}'",
                token,
                expected="a value (string, number, boolean, null, array, object, or constructor call)",
            )

    def _parse_key_value_pair(self):
        """Parse a key-value pair like 'key = value' or 'TypeName name = value'.

        Returns:
            A tuple of (key_name, value_info) if a key-value pair was parsed,
            or (None, None) if the current position doesn't contain a key-value pair.
        """
        start_pos = self.pos

        try:
            type_name, _ = self._parse_identifier(allow_namespace=True)

            if self._current_token() and self._current_token()["type"] == "IDENTIFIER":
                key_name = self._consume("IDENTIFIER")[
                    "value"
                ]  # This is a typed declaration
                is_type_declaration = True
            else:
                self.pos = start_pos  # Reset position for regular key parsing
                key_name = self._consume("IDENTIFIER")["value"]
                is_type_declaration = False

            is_array = False
            if self._current_token() and self._current_token()["value"] == "[":
                self._consume("PUNCTUATION", "[")
                self._consume("PUNCTUATION", "]")  # Empty brackets indicate array type
                is_array = True

            if not (self._current_token() and self._current_token()["value"] == "="):
                self.pos = start_pos  # Not a key-value pair, backtrack
                return None, None

            self._consume("PUNCTUATION", "=")
            value = self._parse_value()

            result = {
                "value": value,
                "is_array": is_array,
                "line": self.tokens[start_pos]["line"],
                "col": self.tokens[start_pos]["col"],
            }

            # Elevate params to same level as value for test compatibility
            if isinstance(value, dict) and "params" in value:
                result["params"] = value["params"]

            if is_type_declaration:
                result["type"] = type_name

            return key_name, result

        except SyntaxError:
            self.pos = start_pos  # Rewind on syntax error

            if self._current_token() and self._current_token()["type"] == "IDENTIFIER":
                key_name = self._consume("IDENTIFIER")["value"]

                if not (
                    self._current_token() and self._current_token()["value"] == "="
                ):
                    self.pos = start_pos  # Not a valid pair, backtrack
                    return None, None

                self._consume("PUNCTUATION", "=")
                value = self._parse_value()

                result = {
                    "value": value,
                    "line": self.tokens[start_pos]["line"],
                    "col": self.tokens[start_pos]["col"],
                }

                # Elevate params to same level as value for test compatibility
                if isinstance(value, dict) and "params" in value:
                    result["params"] = value["params"]

                return key_name, result

        self.pos = start_pos  # Reset position if not a key-value pair
        return None, None

    def _parse_object_body(self) -> Dict:
        """Parse the body of an object.

        Returns:
            A dictionary containing the parsed key-value pairs and nested objects.
            Each value is a dictionary with at least 'value' and may include 'type', 'is_array', etc.
        """
        body: Dict[str, Any] = {}

        if not (self._current_token() and self._current_token()["value"] == "{"):
            return body  # Empty body if no opening brace

        self._consume("PUNCTUATION", "{")

        while self._current_token() and self._current_token()["value"] != "}":
            if self._current_token() and self._current_token()["type"] == "INCLUDE":
                include_token = self._consume("INCLUDE")

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

                included_data = self._process_include(include_path)

                if "body" in included_data:
                    for include_key, include_value in included_data["body"].items():
                        body[include_key] = include_value  # Merge body content
                else:
                    for include_key, include_value in included_data.items():
                        body[include_key] = include_value  # Merge entire result

                if self._current_token() and self._current_token()["value"] in [
                    ";",
                    ",",
                ]:
                    self._consume("PUNCTUATION")  # Skip optional separator

                continue  # Process next object member

            key, value = self._parse_key_value_pair()

            if key is not None:
                body[key] = value  # Add parsed pair to body

                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")  # Optional comma separator
            else:
                if (
                    self._current_token()
                    and self._current_token()["type"] == "IDENTIFIER"
                ):
                    nested_obj = self._parse_object(
                        is_top_level=False
                    )  # Parse nested object

                    if "name" in nested_obj:
                        obj_name = nested_obj["name"]

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
                    if self._current_token():
                        self._consume()  # Skip unrecognized token
                    else:
                        break  # End of input reached

            if self._current_token() and self._current_token()["value"] == ";":
                self._consume("PUNCTUATION", ";")  # Optional semicolon separator

        self._consume("PUNCTUATION", "}")
        return body

    def _parse_constructor_call(self):
        """Parse a constructor-style call like TypeName(arg1, arg2, ...)"""
        type_name, _ = self._parse_identifier()

        args = []
        if self._current_token() and self._current_token()["value"] == "(":
            self._consume("PUNCTUATION", "(")

            while self._current_token() and self._current_token()["value"] != ")":
                # Parse named parameter (key = value)
                key, value = self._parse_key_value_pair()
                args.append({"key": key, "value": value})

                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")  # Optional comma separator
                else:
                    # No comma found, we're done with arguments
                    break

            self._consume("PUNCTUATION", ")")  # Close parameter list

        body = {}
        if self._current_token() and self._current_token()["value"] == "{":
            body = self._parse_object_body()  # Parse optional constructor body

        return {"type": type_name, "body": body}

    def _parse_array(self) -> List:
        """Parse an array literal.

        Returns:
            List: The parsed array of values

        Raises:
            ConfigParseError: If there's a syntax error in the array
        """
        start_token = self._current_token()
        if start_token is None or start_token["value"] != "[":
            raise self._create_syntax_error(
                message="Expected '[' to start array", token=start_token, expected="'['"
            )

        self._consume("PUNCTUATION", "[")
        elements: List[Any] = []

        try:
            if self._current_token() and self._current_token()["value"] == "]":
                self._consume("PUNCTUATION", "]")  # Empty array case
                return elements

            elements.append(self._parse_value())  # Parse first element

            while self._current_token() and self._current_token()["value"] == ",":
                self._consume("PUNCTUATION", ",")  # Comma separator

                if self._current_token() and self._current_token()["value"] == "]":
                    break  # Allow trailing comma

                elements.append(self._parse_value())  # Parse next element

            if not self._current_token() or self._current_token()["value"] != "]":
                raise self._create_syntax_error(
                    message="Expected ']' to close array",
                    token=self._current_token(),
                    expected="']' or ','",
                )

            self._consume("PUNCTUATION", "]")
            return elements

        except ConfigParseError as e:
            raise e from None  # Re-raise custom errors without modification

        except Exception as e:
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
        values: List[str] = []

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

    def _parse_enum_definition(self) -> Tuple[str, Dict]:
        """Parse an enum definition: enum::EnumName { values = [...], default = "..." }"""
        try:
            self._consume("ENUM")

            if not self._current_token() or self._current_token()["value"] != "::":
                raise self._create_syntax_error(
                    "Expected '::' after 'enum'", self._current_token(), "'::'"
                )
            self._consume("NAMESPACE", "::")

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

            if not self._current_token() or self._current_token()["value"] != "{":
                raise self._create_syntax_error(
                    "Expected '{' to start enum body", self._current_token(), "'{'"
                )
            self._consume("PUNCTUATION", "{")

            enum_data = {
                "type": "enum_definition",
                "name": enum_name,
                "values": [],
                "default": None,
            }

            # Parse enum properties (values and default)
            while self._current_token() and self._current_token()["value"] != "}":
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

                if not self._current_token() or self._current_token()["value"] != "=":
                    raise self._create_syntax_error(
                        "Expected '=' after enum property name",
                        self._current_token(),
                        "'='",
                    )
                self._consume("PUNCTUATION", "=")

                if prop_name == "values":
                    enum_data["values"] = self._parse_enum_values_array()
                elif prop_name == "default":
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

                if self._current_token() and self._current_token()["value"] == ",":
                    self._consume("PUNCTUATION", ",")

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
            raise e from None

        except Exception as e:
            raise self._create_syntax_error(
                message=f"Error parsing enum definition: {str(e)}",
                token=self._current_token(),
                expected="enum definition syntax",
            ) from e


def parse_string(
    text: str, base_path: str = None, included_files: Set[Path] = None
) -> Dict:
    """
    Parse CFGPP configuration from a string.

    This is the primary parsing function for text content. Preferred over loads().

    Args:
        text: CFGPP configuration text to parse
        base_path: Base path for resolving includes
        included_files: Set of already included files (for circular detection)

    Returns:
        Parsed configuration as dictionary

    Examples:
        >>> config_text = '''
        ... AppConfig {
        ...     name = "MyApp",
        ...     port = 8080
        ... }
        ... '''
        >>> result = parse_string(config_text)
        >>> result['body']['AppConfig']['body']['name']['value']['value']
        'MyApp'

        >>> # Typed configuration
        >>> typed_config = 'Database::MySQL(string host="localhost", int port=3306)'
        >>> result = parse_string(typed_config)
        >>> params = result['body']['Database::MySQL']['params']
        >>> params['host']['value']['value']
        'localhost'
    """
    return _parse_text_internal(text, base_path, included_files)


def parse_file(file_path: str) -> Dict:
    """
    Parse CFGPP configuration from a file.

    Preferred over load() for clearer code.

    Args:
        file_path: Path to the CFGPP configuration file

    Returns:
        Parsed configuration as dictionary

    Examples:
        >>> # Parse application configuration
        >>> config = parse_file("app.cfgpp")
        >>> app_name = config['body']['AppConfig']['body']['name']['value']['value']

        >>> # Parse with error handling
        >>> try:
        ...     config = parse_file("config.cfgpp")
        ...     print("Configuration loaded successfully")
        ... except FileNotFoundError:
        ...     print("Configuration file not found")
        ... except ConfigParseError as e:
        ...     print(f"Parse error at line {e.line}: {e.message}")

        >>> # Parse microservice configuration
        >>> service_config = parse_file("microservice.cfgpp")
        >>> service_body = service_config['body']['ServiceConfig']['body']
        >>> port = service_body['port']['value']['value']
        >>> print(f"Service running on port {port}")
    """
    return _parse_file_internal(file_path)


# Legacy aliases for backwards compatibility
def loads(text: str, base_path: str = None, included_files: Set[Path] = None) -> Dict:
    """
    Legacy alias for parse_string() - use parse_string() instead for clearer API.

    Args:
        text: The configuration text to parse
        base_path: Base path for resolving include directives (defaults to current directory)
        included_files: Set of already included files to prevent circular includes

    Returns:
        Dict: The parsed configuration as a Python dictionary

    Raises:
        ConfigParseError: If there's a syntax error in the configuration
    """
    return parse_string(text, base_path, included_files)


def _parse_text_internal(
    text: str, base_path: str = None, included_files: Set[Path] = None
) -> Dict:
    """Internal implementation for parsing configuration text."""
    from .lexer import lex

    tokens = lex(text)

    base_path_obj = Path(base_path) if base_path else Path.cwd()

    parser = Parser(tokens, text.splitlines(), base_path_obj, included_files)

    try:
        return parser.parse()
    except Exception as e:
        if isinstance(e, ConfigParseError):
            raise  # Re-raise custom errors as-is
        raise ConfigParseError(f"Error parsing configuration: {str(e)}") from e


def load(file_path: str) -> Dict:
    """
    Legacy alias for parse_file() - use parse_file() instead.

    Args:
        file_path: Path to the CFGPP configuration file

    Returns:
        Parsed configuration as dictionary
    """
    return parse_file(file_path)


def _parse_file_internal(file_path: str) -> Dict:
    """Internal implementation for parsing configuration files."""
    file_path_obj = Path(file_path)

    included_files = {file_path_obj.resolve()}

    with open(file_path_obj, "r", encoding="utf-8") as f:
        return loads(f.read(), str(file_path_obj.parent), included_files)
