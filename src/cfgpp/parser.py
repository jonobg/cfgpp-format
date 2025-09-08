"""
A simple parser for the CFG++ configuration format.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from .lexer import lex, Token, LexerError

class ConfigParseError(SyntaxError):
    """Custom exception for configuration parsing errors."""
    def __init__(self, message: str, line: int = None, column: int = None, context: str = None):
        self.message = message
        self.line = line
        self.column = column
        self.context = context
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
    
    def __init__(self, tokens: List[Dict[str, Any]], source_lines: List[str], base_path: Optional[Path] = None, included_files: Optional[Set[Path]] = None):
        self.tokens = tokens
        self.source_lines = source_lines
        self.pos = 0
        self.base_path = base_path or Path.cwd()
        self.included_files = included_files or set()
    
    def parse(self, text: str = None) -> Dict:
        """Parse the given cfgpp configuration text into a Python dictionary.
        
        Args:
            text: Optional text to parse. If not provided, tokens must be set in the constructor.
            
        Returns:
            Dict: The parsed configuration
            
        Raises:
            ValueError: If no tokens are provided and no text is given to parse
        """
        if text is not None:
            self.tokens = self._tokenize(text)
        elif not self.tokens:
            raise ValueError("No tokens provided and no text to parse")
            
        self.pos = 0
        
        # Check if we have a simple key-value assignment at the top level
        if (self._current_token() and 
            self._current_token()['type'] == 'IDENTIFIER' and
            self._current_token(1) and 
            self._current_token(1)['value'] == '='):
            # Parse as a simple key-value pair
            key, value = self._parse_key_value_pair()
            return {'body': {key: value}}
        
        # Parse multiple top-level objects
        body = {}
        while self._current_token():
            # Check for top-level include directives
            if self._current_token()['type'] == 'INCLUDE':
                include_token = self._consume('INCLUDE')
                
                # Expect a string with the file path
                if not self._current_token() or self._current_token()['type'] != 'STRING':
                    raise self._create_syntax_error("Expected string path after include directive", self._current_token(), "string path")
                
                path_token = self._consume('STRING')
                include_path = path_token['value'][1:-1]  # Remove quotes
                
                # Process the include and merge the result
                included_data = self._process_include(include_path)
                
                # Merge included data into the current body
                if 'body' in included_data:
                    for include_key, include_value in included_data['body'].items():
                        body[include_key] = include_value
                        
            elif self._current_token()['type'] == 'IDENTIFIER':
                # Try to parse as an object
                obj = self._parse_object(is_top_level=True)
                if 'body' in obj:
                    # Merge all objects from the parsed result
                    for obj_key, obj_value in obj['body'].items():
                        body[obj_key] = obj_value
                else:
                    # Single object result
                    if 'name' in obj:
                        body[obj['name']] = obj
                    else:
                        # Use a generated key if no name
                        body[f'object_{len(body)}'] = obj
            else:
                raise self._create_syntax_error(f"Unexpected token at top level: {self._current_token()['type']} '{self._current_token()['value']}'", self._current_token(), "object name or include directive")
        
        return {'body': body}
    
    def _tokenize(self, text: str) -> List[Dict]:
        """Convert the input text into a list of tokens."""
        # Define token patterns
        token_spec = [
            ('COMMENT', r'//.*?$'),
            ('STRING', r'"(?:\\.|[^"\\])*"'),
            ('NUMBER', r'\d+(\.\d+)?'),
            ('BOOLEAN', r'true|false'),
            ('NAMESPACE', r'::'),  # Handle namespace operator
            ('IDENTIFIER', r'[a-zA-Z_]\w*'),
            ('PUNCTUATION', r'[\{\}\(\)\[\],;=]'),  # Removed : from PUNCTUATION
            ('WHITESPACE', r'\s+'),
            ('NEWLINE', r'\n'),
            ('OTHER', r'.'),
        ]
        
        # Compile the regex patterns
        token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
        
        # Tokenize the input
        tokens = []
        line_num = 1
        line_start = 0
        
        for mo in re.finditer(token_regex, text, re.MULTILINE | re.DOTALL):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start
            
            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'WHITESPACE':
                continue
            elif kind == 'COMMENT':
                continue
            elif kind == 'OTHER':
                raise SyntaxError(f'Unexpected character: {value} at line {line_num}, column {column + 1}')
            
            tokens.append({
                'type': kind,
                'value': value,
                'line': line_num,
                'col': column + 1
            })
        
        return tokens
    
    def _current_token(self, offset: int = 0) -> Optional[Dict]:
        """Get the current token with an optional offset.
        
        Returns:
            The token at the current position + offset, or None if beyond the end
        """
        pos = self.pos + offset
        if 0 <= pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def _create_syntax_error(
        self, 
        message: str, 
        token: Optional[Dict] = None,
        expected: Optional[str] = None
    ) -> ConfigParseError:
        """Create a syntax error with detailed context information."""
        line = token.get('line', 1) if token else None
        col = token.get('col', 1) if token else None
        
        # Enhance the message with what was expected if provided
        if expected:
            if message.startswith(("Expected", "Unexpected")):
                message = f"Expected {expected}, {message[8:].lower()}"
            else:
                message = f"Expected {expected}, {message}"
        
        return ConfigParseError(message, line, col)
    
    def _process_include(self, include_path: str) -> Dict[str, Any]:
        """Process an include/import directive."""
        # Resolve the include path relative to the base path
        if not include_path.endswith('.cfgpp'):
            include_path += '.cfgpp'
            
        resolved_path = (self.base_path / include_path).resolve()
        
        # Check for circular includes
        if resolved_path in self.included_files:
            raise ConfigParseError(f"Circular include detected: {include_path}")
        
        # Check if file exists
        if not resolved_path.exists():
            raise ConfigParseError(f"Include file not found: {include_path}")
        
        # Read and parse the included file
        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                included_content = f.read()
        except IOError as e:
            raise ConfigParseError(f"Failed to read include file '{include_path}': {e}")
        
        # Create a new parser for the included file with updated included_files set
        new_included_files = self.included_files.copy()
        new_included_files.add(resolved_path)
        
        return loads(included_content, str(resolved_path.parent), new_included_files)
    
    def _is_expression_start(self) -> bool:
        """Check if the current position starts an expression by looking ahead for operators."""
        # Save current position
        original_pos = self.pos
        
        try:
            # Skip the first token (which should be a value)
            if not self._current_token():
                return False
            
            # Check if it's a parenthesized expression
            if self._current_token()['value'] == '(':
                return True
            
            # Skip literals, env vars, identifiers
            if self._current_token()['type'] in ['STRING', 'NUMBER', 'BOOLEAN', 'ENV_VAR', 'IDENTIFIER']:
                self.pos += 1
                # Check if there's an operator following
                if (self._current_token() and 
                    self._current_token()['type'] == 'OPERATOR' and 
                    self._current_token()['value'] in ['+', '-', '*', '/']):
                    return True
            
            return False
        finally:
            # Restore original position
            self.pos = original_pos
    
    def _parse_expression(self) -> Dict[str, Any]:
        """Parse a mathematical or string expression."""
        return self._parse_addition()
    
    def _parse_addition(self) -> Dict[str, Any]:
        """Parse addition and subtraction operations."""
        left = self._parse_multiplication()
        
        while (self._current_token() and 
               self._current_token()['type'] == 'OPERATOR' and 
               self._current_token()['value'] in ['+', '-']):
            op_token = self._consume('OPERATOR')
            right = self._parse_multiplication()
            
            # Evaluate the expression
            left = self._evaluate_binary_op(left, op_token['value'], right)
        
        return left
    
    def _parse_multiplication(self) -> Dict[str, Any]:
        """Parse multiplication and division operations."""
        left = self._parse_primary()
        
        while (self._current_token() and 
               self._current_token()['type'] == 'OPERATOR' and 
               self._current_token()['value'] in ['*', '/']):
            op_token = self._consume('OPERATOR')
            right = self._parse_primary()
            
            # Evaluate the expression
            left = self._evaluate_binary_op(left, op_token['value'], right)
        
        return left
    
    def _parse_primary(self) -> Dict[str, Any]:
        """Parse primary expressions (numbers, strings, parenthesized expressions)."""
        token = self._current_token()
        
        if not token:
            raise self._create_syntax_error("Unexpected end of input in expression")
        
        # Handle parenthesized expressions
        if token['value'] == '(':
            self._consume('PUNCTUATION', '(')
            result = self._parse_expression()
            if not self._current_token() or self._current_token()['value'] != ')':
                raise self._create_syntax_error("Expected ')' to close expression", self._current_token(), "')'")
            self._consume('PUNCTUATION', ')')
            return result
        
        # Handle literals directly (avoid recursion)
        if token['type'] == 'STRING':
            value = self._consume('STRING')['value']
            value = value[1:-1]  # Remove quotes
            return {
                'type': 'string',
                'value': value,
                'line': token['line'],
                'col': token['col']
            }
        
        elif token['type'] == 'NUMBER':
            value = self._consume('NUMBER')['value']
            try:
                value = int(value)
                value_type = 'integer'
            except ValueError:
                try:
                    value = float(value)
                    value_type = 'float'
                except ValueError:
                    raise self._create_syntax_error("Invalid number format", token)
            return {
                'type': value_type,
                'value': value,
                'line': token['line'],
                'col': token['col']
            }
        
        elif token['type'] == 'BOOLEAN':
            value = self._consume('BOOLEAN')['value']
            return {
                'type': 'boolean',
                'value': value.lower() == 'true',
                'line': token['line'],
                'col': token['col']
            }
        
        elif token['type'] == 'ENV_VAR':
            env_token = self._consume('ENV_VAR')['value']
            env_content = env_token[2:-1]  # Remove ${ and }
            if ':-' in env_content:
                var_name, default_value = env_content.split(':-', 1)
                if default_value.startswith('"') and default_value.endswith('"'):
                    default_value = default_value[1:-1]
            else:
                var_name = env_content
                default_value = None
            
            env_value = os.getenv(var_name, default_value)
            if env_value is None:
                raise self._create_syntax_error(f"Environment variable '{var_name}' is not set and no default provided", token)
            
            # Type inference for env vars
            if env_value.lower() in ('true', 'false'):
                return {
                    'type': 'boolean',
                    'value': env_value.lower() == 'true',
                    'line': token['line'],
                    'col': token['col'],
                    'env_var': var_name
                }
            
            try:
                int_value = int(env_value)
                return {
                    'type': 'integer',
                    'value': int_value,
                    'line': token['line'],
                    'col': token['col'],
                    'env_var': var_name
                }
            except ValueError:
                pass
            
            try:
                float_value = float(env_value)
                return {
                    'type': 'float',
                    'value': float_value,
                    'line': token['line'],
                    'col': token['col'],
                    'env_var': var_name
                }
            except ValueError:
                pass
            
            return {
                'type': 'string',
                'value': env_value,
                'line': token['line'],
                'col': token['col'],
                'env_var': var_name
            }
        
        # Handle identifiers (could be variable references in the future)
        elif token['type'] == 'IDENTIFIER' and token['value'].lower() == 'null':
            self._consume('IDENTIFIER', 'null')
            return {
                'type': 'null',
                'value': None,
                'line': token['line'],
                'col': token['col']
            }
        
        raise self._create_syntax_error(f"Unexpected token in expression: {token['value']}", token)
    
    def _evaluate_binary_op(self, left: Dict[str, Any], operator: str, right: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a binary operation between two values."""
        left_val = left['value']
        right_val = right['value']
        left_type = left['type']
        right_type = right['type']
        
        # String concatenation
        if operator == '+' and (left_type == 'string' or right_type == 'string'):
            result_val = str(left_val) + str(right_val)
            return {
                'type': 'string',
                'value': result_val,
                'line': left.get('line', 1),
                'col': left.get('col', 1),
                'expression': True
            }
        
        # Numeric operations
        if left_type in ['integer', 'float'] and right_type in ['integer', 'float']:
            try:
                if operator == '+':
                    result_val = left_val + right_val
                elif operator == '-':
                    result_val = left_val - right_val
                elif operator == '*':
                    result_val = left_val * right_val
                elif operator == '/':
                    if right_val == 0:
                        raise self._create_syntax_error("Division by zero in expression")
                    result_val = left_val / right_val
                else:
                    raise self._create_syntax_error(f"Unsupported operator: {operator}")
                
                # Determine result type
                result_type = 'float' if isinstance(result_val, float) else 'integer'
                
                return {
                    'type': result_type,
                    'value': result_val,
                    'line': left.get('line', 1),
                    'col': left.get('col', 1),
                    'expression': True
                }
            except Exception as e:
                raise self._create_syntax_error(f"Error in expression evaluation: {str(e)}")
        
        raise self._create_syntax_error(f"Cannot apply operator '{operator}' to {left_type} and {right_type}")

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
            expected_str = ' or '.join(expected) or 'token'
            
            raise self._create_syntax_error(
                message=f"Unexpected end of input, expected {expected_str}",
                expected=expected_str
            )
        
        if expected_type is not None and token['type'] != expected_type:
            raise self._create_syntax_error(
                message=f"Got unexpected token type '{token['type']}'",
                token=token,
                expected=f"{expected_type}"
            )
            
        if expected_value is not None and token['value'] != expected_value:
            raise self._create_syntax_error(
                message=f"Got unexpected value '{token['value']}'",
                token=token,
                expected=f"'{expected_value}'"
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
        # Parse parameter type (which could be a namespaced identifier)
        param_type, type_parts = self._parse_identifier(allow_namespace=True)
        is_array = False
        
        # Check for array notation
        if self._current_token() and self._current_token()['value'] == '[':
            self._consume('PUNCTUATION', '[')
            self._consume('PUNCTUATION', ']')
            is_array = True
            
        param_name = self._consume('IDENTIFIER')
        
        # Check for default value
        default_value = None
        if self._current_token() and self._current_token()['value'] == '=':
            self._consume('PUNCTUATION', '=')
            default_value = self._parse_value()
        
        param_info = {
            'type': param_type,
            'is_array': is_array,
            'value': default_value,
            'line': type_parts[0]['line'],
            'col': type_parts[0]['col']
        }
        
        # Handle nested type definitions
        if self._current_token() and self._current_token()['value'] == '(':
            param_info['nested'] = self._parse_object()
        
        return param_name['value'], param_info

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
        if not self._current_token() or self._current_token()['type'] != 'IDENTIFIER':
            token = self._current_token()
            raise self._create_syntax_error(
                message="Expected an identifier",
                token=token,
                expected="identifier"
            )
            
        name_parts = [self._consume('IDENTIFIER')]
        
        # Check for namespace separator (::)
        if allow_namespace:
            while self._current_token() and self._current_token()['type'] == 'NAMESPACE':
                namespace_token = self._current_token()
                self._consume('NAMESPACE')
                
                # The next token must be an identifier
                if not self._current_token() or self._current_token()['type'] != 'IDENTIFIER':
                    raise self._create_syntax_error(
                        message="Incomplete namespaced identifier",
                        token=namespace_token,
                        expected="identifier after '::'"
                    )
                    
                name_parts.append('::')
                name_parts.append(self._consume('IDENTIFIER'))
        
        full_name = ''.join(part['value'] if isinstance(part, dict) else part for part in name_parts)
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
        # Handle namespaced identifiers (e.g., Namespace::Type)
        full_name, name_parts = self._parse_identifier()
        
        # Store the start position for error reporting
        start_line = name_parts[0]['line']
        start_col = name_parts[0]['col']
        
        # Parse parameters if they exist
        params = {}
        if self._current_token() and self._current_token()['value'] == '(':
            self._consume('PUNCTUATION', '(')
            
            while self._current_token() and self._current_token()['value'] != ')':
                param_name, param_info = self._parse_parameter()
                params[param_name] = param_info
                
                # Check for more parameters
                if self._current_token() and self._current_token()['value'] == ',':
                    self._consume('PUNCTUATION', ',')
                else:
                    break
            
            self._consume('PUNCTUATION', ')')
        
        # Parse object body if it exists
        body = self._parse_object_body()
        
        # If this is a parameter with a body, treat the body as the value
        if not is_top_level and body and not params:
            return body
            
        # Create the result object
        result = {
            'name': full_name,
            'body': body or {},
            'line': start_line,
            'col': start_col
        }
        
        # If there are parameters, add them to the result
        if params:
            result['parameters'] = params
        
        # If this is a top-level object, wrap it in the body with its name as the key
        if is_top_level and (self._current_token() is None or self._current_token()['value'] not in {',', ';', '='}):
            return {
                'body': {
                    full_name: result
                }
            }
            
        return result
    
    def _parse_value(self):
        """Parse a value, which can be a literal, array, object, constructor call, or expression.
        
        Returns:
            A dictionary containing the parsed value with type information.
            
        Raises:
            ConfigParseError: If there's a syntax error in the value
        """
        if not self._current_token():
            raise self._create_syntax_error("Unexpected end of input while expecting a value")
        
        # Check if this could be an expression by looking ahead for operators
        if self._is_expression_start():
            return self._parse_expression()
            
        token = self._current_token()
        
        # Handle different token types
        if token['type'] == 'ENV_VAR':
            env_token = self._consume('ENV_VAR')['value']
            # Parse ${VAR_NAME} or ${VAR_NAME:-default_value}
            env_content = env_token[2:-1]  # Remove ${ and }
            if ':-' in env_content:
                var_name, default_value = env_content.split(':-', 1)
                # Remove quotes from default value if present
                if default_value.startswith('"') and default_value.endswith('"'):
                    default_value = default_value[1:-1]
            else:
                var_name = env_content
                default_value = None
            
            # Get environment variable value
            env_value = os.getenv(var_name, default_value)
            
            if env_value is None:
                raise self._create_syntax_error(f"Environment variable '{var_name}' is not set and no default provided", token)
            
            # Try to infer the type from the value
            # Check for boolean
            if env_value.lower() in ('true', 'false'):
                return {
                    'type': 'boolean',
                    'value': env_value.lower() == 'true',
                    'line': token['line'],
                    'col': token['col'],
                    'env_var': var_name
                }
            
            # Check for integer
            try:
                int_value = int(env_value)
                return {
                    'type': 'integer',
                    'value': int_value,
                    'line': token['line'],
                    'col': token['col'],
                    'env_var': var_name
                }
            except ValueError:
                pass
            
            # Check for float
            try:
                float_value = float(env_value)
                return {
                    'type': 'float',
                    'value': float_value,
                    'line': token['line'],
                    'col': token['col'],
                    'env_var': var_name
                }
            except ValueError:
                pass
            
            # Default to string
            return {
                'type': 'string',
                'value': env_value,
                'line': token['line'],
                'col': token['col'],
                'env_var': var_name
            }
            
        elif token['type'] == 'STRING':
            value = self._consume('STRING')['value']
            # Remove surrounding quotes
            value = value[1:-1]
            return {
                'type': 'string',
                'value': value,
                'line': token['line'],
                'col': token['col']
            }
            
        elif token['type'] == 'NUMBER':
            value = self._consume('NUMBER')['value']
            # Try to parse as int first, then float
            try:
                value = int(value)
                value_type = 'integer'
            except ValueError:
                try:
                    value = float(value)
                    value_type = 'float'
                except ValueError:
                    raise self._create_syntax_error("Invalid number format", token)
                    
            return {
                'type': value_type,
                'value': value,
                'line': token['line'],
                'col': token['col']
            }
            
        elif token['type'] == 'BOOLEAN':
            value = self._consume('BOOLEAN')['value']
            return {
                'type': 'boolean',
                'value': value.lower() == 'true',
                'line': token['line'],
                'col': token['col']
            }
            
        elif token['type'] == 'IDENTIFIER' and token['value'].lower() == 'null':
            self._consume('IDENTIFIER', 'null')
            return {
                'type': 'null',
                'value': None,
                'line': token['line'],
                'col': token['col']
            }
            
        elif token['value'] == '[':
            # Array literal
            return self._parse_array()
            
        elif token['value'] == '{':
            # Object literal
            return self._parse_object(is_top_level=False)
            
        elif token['type'] == 'IDENTIFIER' and self._current_token(1) and self._current_token(1)['value'] == '(':
            # Constructor call
            return self._parse_constructor_call()
            
        elif token['type'] == 'IDENTIFIER':
            # Check if this is followed by { (simple identifier) or :: followed by more identifiers and then {
            lookahead = 1
            while (self._current_token(lookahead) and 
                   self._current_token(lookahead)['type'] == 'NAMESPACE' and
                   self._current_token(lookahead + 1) and
                   self._current_token(lookahead + 1)['type'] == 'IDENTIFIER'):
                lookahead += 2  # Skip :: and identifier
            
            if (self._current_token(lookahead) and 
                self._current_token(lookahead)['value'] == '{'):
                # Object constructor call like DatabaseConfig { ... } or Namespace::Type { ... }
                return self._parse_object(is_top_level=False)
            
        else:
            raise self._create_syntax_error(
                f"Unexpected token: {token['type']} '{token['value']}'",
                token,
                expected="a value (string, number, boolean, null, array, object, or constructor call)"
            )
    
    def _parse_key_value_pair(self):
        """Parse a key-value pair like 'key = value' or 'TypeName name = value'.
        
        Returns:
            A tuple of (key_name, value_info) if a key-value pair was parsed,
            or (None, None) if the current position doesn't contain a key-value pair.
        """
        start_pos = self.pos
        
        try:
            # Try to parse a type (which could be namespaced)
            type_name, _ = self._parse_identifier(allow_namespace=True)
            
            # Check if this is a type-name pair (e.g., 'string name' or 'Namespace::Type value')
            if (self._current_token() and 
                self._current_token()['type'] == 'IDENTIFIER'):
                # This is a type-name pair
                key_name = self._consume('IDENTIFIER')['value']
                is_type_declaration = True
            else:
                # Not a type declaration, reset and parse as a regular key
                self.pos = start_pos
                key_name = self._consume('IDENTIFIER')['value']
                is_type_declaration = False
            
            # Check for array notation
            is_array = False
            if self._current_token() and self._current_token()['value'] == '[':
                self._consume('PUNCTUATION', '[')
                self._consume('PUNCTUATION', ']')
                is_array = True
            
            # Must have an '=' for a key-value pair
            if not (self._current_token() and self._current_token()['value'] == '='):
                self.pos = start_pos
                return None, None
                
            self._consume('PUNCTUATION', '=')
            value = self._parse_value()
            
            # Create the result
            result = {
                'value': value,
                'is_array': is_array,
                'line': self.tokens[start_pos]['line'],
                'col': self.tokens[start_pos]['col']
            }
            
            # If this was a type declaration, include the type
            if is_type_declaration:
                result['type'] = type_name
            
            return key_name, result
            
        except SyntaxError:
            # If we encountered a syntax error, rewind and try parsing as a regular key
            self.pos = start_pos
            
            # Try to parse a simple key-value pair
            if self._current_token() and self._current_token()['type'] == 'IDENTIFIER':
                key_name = self._consume('IDENTIFIER')['value']
                
                # Must have an '=' for a key-value pair
                if not (self._current_token() and self._current_token()['value'] == '='):
                    self.pos = start_pos
                    return None, None
                    
                self._consume('PUNCTUATION', '=')
                value = self._parse_value()
                
                return key_name, {
                    'value': value,
                    'line': self.tokens[start_pos]['line'],
                    'col': self.tokens[start_pos]['col']
                }
        
        # If we get here, it's not a key-value pair
        self.pos = start_pos
        return None, None
    
    def _parse_object_body(self) -> Dict:
        """Parse the body of an object.
        
        Returns:
            A dictionary containing the parsed key-value pairs and nested objects.
            Each value is a dictionary with at least 'value' and may include 'type', 'is_array', etc.
        """
        body = {}
        if not (self._current_token() and self._current_token()['value'] == '{'):
            return body
            
        self._consume('PUNCTUATION', '{')
        
        while self._current_token() and self._current_token()['value'] != '}':
            # Check for include directives first
            if self._current_token() and self._current_token()['type'] == 'INCLUDE':
                include_token = self._consume('INCLUDE')
                
                # Expect a string with the file path
                if not self._current_token() or self._current_token()['type'] != 'STRING':
                    raise self._create_syntax_error("Expected string path after include directive", self._current_token(), "string path")
                
                path_token = self._consume('STRING')
                include_path = path_token['value'][1:-1]  # Remove quotes
                
                # Process the include and merge the result
                included_data = self._process_include(include_path)
                
                # Merge included data into the current body
                if 'body' in included_data:
                    for include_key, include_value in included_data['body'].items():
                        body[include_key] = include_value
                else:
                    # If no body key, merge the entire result
                    for include_key, include_value in included_data.items():
                        body[include_key] = include_value
                
                # Skip optional semicolon or comma
                if self._current_token() and self._current_token()['value'] in [';', ',']:
                    self._consume('PUNCTUATION')
                    
                continue
            
            # First, try to parse as a key-value pair
            key, value = self._parse_key_value_pair()
            
            if key is not None:
                # We have a valid key-value pair
                body[key] = value
            else:
                # Try to parse as a nested object
                if self._current_token() and self._current_token()['type'] == 'IDENTIFIER':
                    try:
                        # Parse the nested object (not a top-level object)
                        nested_obj = self._parse_object(is_top_level=False)
                        
                        # If the object has a name, use it as the key
                        if 'name' in nested_obj:
                            obj_name = nested_obj['name']
                            # If we already have this key, convert to a list if needed
                            if obj_name in body:
                                if not isinstance(body[obj_name]['value'], list):
                                    body[obj_name] = {
                                        'value': [body[obj_name]['value']],
                                        'is_array': True,
                                        'line': body[obj_name]['line'],
                                        'col': body[obj_name]['col']
                                    }
                                body[obj_name]['value'].append(nested_obj)
                            else:
                                body[obj_name] = {
                                    'value': nested_obj,
                                    'is_array': False,
                                    'line': nested_obj.get('line', 0),
                                    'col': nested_obj.get('col', 0)
                                }
                    except (SyntaxError, ConfigParseError):
                        # If we can't parse it as an object, consume the token and continue
                        if self._current_token():
                            self._consume()
                        else:
                            break
                else:
                    # If we can't parse it as a key-value pair or object, skip the token
                    if self._current_token():
                        self._consume()
                    else:
                        break
            
            # Consume semicolon if present
            if self._current_token() and self._current_token()['value'] == ';':
                self._consume('PUNCTUATION', ';')
        
        self._consume('PUNCTUATION', '}')
        return body
    
    def _parse_constructor_call(self):
        """Parse a constructor-style call like TypeName(arg1, arg2, ...)"""
        # Parse the type name (could be namespaced)
        type_name, _ = self._parse_identifier()
        
        # Parse the arguments
        args = []
        if self._current_token() and self._current_token()['value'] == '(':
            self._consume('PUNCTUATION', '(')
            
            while self._current_token() and self._current_token()['value'] != ')':
                # Parse the argument value
                arg_value = self._parse_value()
                args.append(arg_value)
                
                # Check for more arguments
                if self._current_token() and self._current_token()['value'] == ',':
                    self._consume('PUNCTUATION', ',')
                
            self._consume('PUNCTUATION', ')')
        
        # If there's a body, parse it
        body = {}
        if self._current_token() and self._current_token()['value'] == '{':
            body = self._parse_object_body()
        
        return {
            'type': type_name,
            'body': body
        }
    
    def _parse_array(self) -> List:
        """Parse an array literal.
        
        Returns:
            List: The parsed array of values
            
        Raises:
            ConfigParseError: If there's a syntax error in the array
        """
        start_token = self._current_token()
        if start_token is None or start_token['value'] != '[':
            raise self._create_syntax_error(
                message="Expected '[' to start array",
                token=start_token,
                expected="'['"
            )
            
        self._consume('PUNCTUATION', '[')
        elements = []
        
        try:
            # Handle empty array
            if self._current_token() and self._current_token()['value'] == ']':
                self._consume('PUNCTUATION', ']')
                return elements
                
            # Parse first element
            elements.append(self._parse_value())
            
            # Parse additional elements
            while self._current_token() and self._current_token()['value'] == ',':
                self._consume('PUNCTUATION', ',')
                
                # Check for trailing comma
                if self._current_token() and self._current_token()['value'] == ']':
                    break
                    
                elements.append(self._parse_value())
            
            # Consume the closing bracket
            if not self._current_token() or self._current_token()['value'] != ']':
                raise self._create_syntax_error(
                    message="Expected ']' to close array",
                    token=self._current_token(),
                    expected="']' or ','"
                )
                
            self._consume('PUNCTUATION', ']')
            return elements
            
        except ConfigParseError as e:
            # Re-raise our custom errors as-is
            raise e from None
            
        except Exception as e:
            # Wrap other exceptions in our custom error
            raise self._create_syntax_error(
                message=f"Error parsing array: {str(e)}",
                token=self._current_token(),
                expected="a value or ']'"
            ) from e

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
    from .lexer import lex
    
    # Tokenize the input
    tokens = lex(text)
    
    # Convert base_path to Path object if provided
    base_path_obj = Path(base_path) if base_path else Path.cwd()
    
    # Create parser with tokens and source lines
    parser = Parser(tokens, text.splitlines(), base_path_obj, included_files)
    
    try:
        return parser.parse()  # Don't pass text here since we already have tokens
    except Exception as e:
        if isinstance(e, ConfigParseError):
            raise
        raise ConfigParseError(f"Error parsing configuration: {str(e)}") from e

def load(file_path: str) -> Dict:
    """Parse a cfgpp configuration file into a Python dictionary."""
    file_path_obj = Path(file_path)
    included_files = {file_path_obj.resolve()}
    with open(file_path_obj, 'r', encoding='utf-8') as f:
        return loads(f.read(), str(file_path_obj.parent), included_files)
