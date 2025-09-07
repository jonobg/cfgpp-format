"""
A simple parser for the cfgpp configuration format.
"""
import re
from typing import Dict, List, Union, Optional, Any

class Parser:
    """Parser for the cfgpp configuration format."""
    
    def __init__(self):
        self.tokens = []
        self.current = 0
    
    def parse(self, text: str) -> Dict:
        """Parse the given cfgpp configuration text into a Python dictionary."""
        self.tokens = self._tokenize(text)
        self.current = 0
        return self._parse_object()
    
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
    
    def _current_token(self) -> Optional[Dict]:
        """Get the current token or None if at the end."""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None
    
    def _create_syntax_error(self, message: str, token: Dict = None) -> SyntaxError:
        """Create a syntax error with line and column information."""
        if token:
            line = token.get('line', 'unknown')
            col = token.get('col', 'unknown')
            return SyntaxError(f"{message} at line {line}, column {col}")
        return SyntaxError(message)

    def _consume(self, expected_type: str = None, expected_value: str = None) -> Dict:
        """Consume the current token if it matches the expected type and/or value."""
        token = self._current_token()
        
        if token is None:
            raise self._create_syntax_error(
                f"Unexpected end of input, expected {expected_type or 'any token'}"
            )
        
        if expected_type is not None and token['type'] != expected_type:
            raise self._create_syntax_error(
                f"Expected {expected_type}, got {token['type']}",
                token
            )
            
        if expected_value is not None and token['value'] != expected_value:
            raise self._create_syntax_error(
                f"Expected '{expected_value}', got '{token['value']}'",
                token
            )
        
        self.current += 1
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
            allow_namespace: If True, allows parsing of namespaced identifiers (e.g., 'Namespace::Name')
            
        Returns:
            A tuple containing:
            - The full identifier as a string (e.g., 'Namespace::Name')
            - A list of token dictionaries for each part of the identifier
            
        Raises:
            SyntaxError: If the identifier is invalid or incomplete
        """
        if not self._current_token() or self._current_token()['type'] != 'IDENTIFIER':
            token = self._current_token()
            raise self._create_syntax_error("Expected identifier", token)
            
        name_parts = [self._consume('IDENTIFIER')]
        
        # Check for namespace separator (::)
        if allow_namespace:
            while self._current_token() and self._current_token()['type'] == 'NAMESPACE':
                # Consume the '::' token
                self._consume('NAMESPACE')
                
                # The next token must be an identifier
                if not self._current_token() or self._current_token()['type'] != 'IDENTIFIER':
                    raise self._create_syntax_error(
                        "Expected identifier after '::' namespace operator",
                        self._current_token() or name_parts[-1]
                    )
                    
                name_parts.append(self._consume('IDENTIFIER'))
        
        # Combine the namespace parts with '::' as separator
        full_name = '::'.join(part['value'] for part in name_parts)
        return full_name, name_parts

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
    
    def _parse_key_value_pair(self):
        """Parse a key-value pair like 'key = value' or 'TypeName name = value'.
        
        Returns:
            A tuple of (key_name, value_info) if a key-value pair was parsed,
            or (None, None) if the current position doesn't contain a key-value pair.
        """
        start_pos = self.current
        
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
                self.current = start_pos
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
                self.current = start_pos
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
            self.current = start_pos
            
            # Try to parse a simple key-value pair
            if self._current_token() and self._current_token()['type'] == 'IDENTIFIER':
                key_name = self._consume('IDENTIFIER')['value']
                
                # Must have an '=' for a key-value pair
                if not (self._current_token() and self._current_token()['value'] == '='):
                    self.current = start_pos
                    return None, None
                    
                self._consume('PUNCTUATION', '=')
                value = self._parse_value()
                
                return key_name, {
                    'value': value,
                    'line': self.tokens[start_pos]['line'],
                    'col': self.tokens[start_pos]['col']
                }
        
        # If we get here, it's not a key-value pair
        self.current = start_pos
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
                    except SyntaxError:
                        # If we can't parse it as an object, try to consume and continue
                        self._consume()
                else:
                    # If we can't parse it as a key-value pair or object, skip the token
                    self._consume()
            
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
            'args': args,
            'body': body
        }
    
    def _parse_value(self) -> Any:
        """Parse a value (string, number, boolean, array, or object)."""
        token = self._current_token()
        if token is None:
            raise self._create_syntax_error("Unexpected end of input while expecting a value")
        
        try:
            if token['type'] == 'STRING':
                self._consume('STRING')
                # Handle escape sequences in strings
                return bytes(token['value'][1:-1], 'utf-8').decode('unicode_escape')
            elif token['type'] == 'NUMBER':
                self._consume('NUMBER')
                return float(token['value']) if '.' in token['value'] else int(token['value'])
            elif token['type'] == 'BOOLEAN':
                self._consume('BOOLEAN')
                return token['value'] == 'true'
            elif token['value'] == '[':
                return self._parse_array()
            elif token['value'] == '{':
                # Handle empty object literal
                self._consume('PUNCTUATION', '{')
                if self._current_token() and self._current_token()['value'] == '}':
                    self._consume('PUNCTUATION', '}')
                    return {}
                # Handle non-empty object literal
                obj = self._parse_object()
                self._consume('PUNCTUATION', '}')
                return obj
            elif token['type'] == 'IDENTIFIER':
                # This could be a reference to another object, a constructor call,
                # or a special value like 'null' (if we decide to support it)
                if token['value'] == 'null':
                    self._consume('IDENTIFIER')
                    return None
                    
                # Check if this is a constructor call (followed by '(')
                next_token = self.tokens[self.current + 1] if (self.current + 1) < len(self.tokens) else None
                if next_token and next_token['value'] == '(':
                    return self._parse_constructor_call()
                    
                # Otherwise parse as an object
                return self._parse_object()
            else:
                raise self._create_syntax_error(f"Unexpected token: {token['value']}", token)
        except SyntaxError:
            raise
        except Exception as e:
            raise self._create_syntax_error(f"Error parsing value: {str(e)}", token) from e
    
    def _parse_array(self) -> List:
        """Parse an array literal."""
        self._consume('PUNCTUATION', '[')
        elements = []
        
        try:
            if self._current_token() and self._current_token()['value'] != ']':
                elements.append(self._parse_value())
                while self._current_token() and self._current_token()['value'] == ',':
                    self._consume('PUNCTUATION', ',')
                    elements.append(self._parse_value())
            
            self._consume('PUNCTUATION', ']')
            return elements
        except Exception as e:
            raise self._create_syntax_error(f"Error parsing array: {str(e)}", self._current_token()) from e

def loads(text: str) -> Dict:
    """Parse a cfgpp configuration string into a Python dictionary."""
    return Parser().parse(text)

def load(file_path: str) -> Dict:
    """Parse a cfgpp configuration file into a Python dictionary."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return loads(f.read())
