# CFGPP API Reference

This document provides detailed reference information for the CFGPP Python parser API.

## Table of Contents

1. [Core Functions](#core-functions)
2. [Parser Classes](#parser-classes)
3. [Lexer Classes](#lexer-classes)
4. [Exception Classes](#exception-classes)
5. [Data Structures](#data-structures)

## Core Functions

### `parse_string(text: str) -> Dict` 🆕 **Recommended**

Parse a CFGPP configuration string into a Python dictionary.

**Parameters:**
- `text` (str): The configuration text to parse

**Returns:**
- `Dict`: Parsed configuration as a structured dictionary

**Raises:**
- `ConfigParseError`: If there's a syntax error in the configuration
- `LexerError`: If there's an invalid character in the input

### `parse_file(file_path: str) -> Dict` 🆕 **Recommended**

Parse a CFGPP configuration file into a Python dictionary.

**Parameters:**
- `file_path` (str): Path to the configuration file to parse

**Returns:**
- `Dict`: Parsed configuration as a structured dictionary

**Raises:**
- `ConfigParseError`: If there's a syntax error in the configuration
- `FileNotFoundError`: If the specified file doesn't exist

### `loads(text: str) -> Dict` ⚠️ **Legacy**

Legacy alias for `parse_string()`. Use `parse_string()` for clearer code.

**Note:** This function is maintained for backward compatibility but `parse_string()` is preferred for new code.

### `load(file_path: str) -> Dict` ⚠️ **Legacy**

Legacy alias for `parse_file()`. Use `parse_file()` for clearer code.

**Note:** This function is maintained for backward compatibility but `parse_file()` is preferred for new code.

**Example (New Clear API):**
```python
from cfgpp import parse_string, parse_file

# Parse from string
config_text = """
AppConfig {
    name = "MyApp"
    port = 8080
}
"""
result = parse_string(config_text)

# Parse from file
result = parse_file("config.cfgpp")
```

**Example (Legacy API - still works):**
```python
from cfgpp import loads, load

# Legacy aliases (less clear)
result = loads(config_text)  # Use parse_string() instead
result = load("config.cfgpp")  # Use parse_file() instead
```


## Parser Classes

### `Parser`

The main parser class that converts tokens into a structured representation.

#### Constructor

```python
Parser(tokens: List[Dict] = None)
```

**Parameters:**
- `tokens` (List[Dict], optional): List of token dictionaries from the lexer

#### Methods

##### `parse(text: str = None) -> Dict`

Parse the configuration.

**Parameters:**
- `text` (str, optional): Text to parse if tokens weren't provided in constructor

**Returns:**
- `Dict`: Parsed configuration structure

**Example:**
```python
from cfgpp.parser import Parser
from cfgpp.lexer import lex

tokens = lex("Config { name = 'test' }")
parser = Parser(tokens)
result = parser.parse()
```

## Lexer Classes

### `Token`

Represents a single token in the configuration text.

#### Constructor

```python
Token(type_: str, value: str, line: int, column: int)
```

**Parameters:**
- `type_` (str): Token type (e.g., 'IDENTIFIER', 'STRING', 'NUMBER')
- `value` (str): Token value
- `line` (int): Line number (1-based)
- `column` (int): Column number (1-based)

#### Methods

##### `to_dict() -> Dict[str, Any]`

Convert token to dictionary representation.

**Returns:**
- `Dict`: Dictionary with 'type', 'value', 'line', and 'col' keys

### `lex(text: str) -> List[Dict[str, Any]]`

Convert input text into a list of tokens.

**Parameters:**
- `text` (str): Input text to tokenize

**Returns:**
- `List[Dict]`: List of token dictionaries

**Raises:**
- `LexerError`: If an unexpected character is encountered

**Example:**
```python
from cfgpp.lexer import lex

tokens = lex("Config { name = 'test' }")
for token in tokens:
    print(f"{token['type']}: {token['value']}")
```

## Exception Classes

### `ConfigParseError`

Exception raised when there's a syntax error during parsing.

#### Constructor

```python
ConfigParseError(message: str, line: int = None, column: int = None, context: str = None)
```

**Parameters:**
- `message` (str): Error description
- `line` (int, optional): Line number where error occurred
- `column` (int, optional): Column number where error occurred
- `context` (str, optional): Additional context information

#### Properties

- `message` (str): The error message
- `line` (int): Line number (if available)
- `column` (int): Column number (if available)  
- `context` (str): Additional context (if available)

**Example:**
```python
from cfgpp import loads
from cfgpp.parser import ConfigParseError

try:
    result = loads("invalid {")
except ConfigParseError as e:
    print(f"Parse error at line {e.line}, column {e.column}: {e.message}")
```

### `LexerError`

Exception raised when the lexer encounters an invalid character.

#### Constructor

```python
LexerError(message: str, line: int, column: int)
```

**Parameters:**
- `message` (str): Error description
- `line` (int): Line number where error occurred
- `column` (int): Column number where error occurred

#### Properties

- `message` (str): The error message
- `line` (int): Line number
- `column` (int): Column number

**Example:**
```python
from cfgpp.lexer import lex, LexerError

try:
    tokens = lex("Config { invalid:::syntax }")
except LexerError as e:
    print(f"Lexer error at line {e.line}, column {e.column}: {e.message}")
```

## Data Structures

### Parsed Configuration Structure

The parser returns a nested dictionary with the following structure:

```python
{
    "body": {
        "ObjectName": {
            "name": "ObjectName",
            "body": {
                "property_name": {
                    "value": {
                        "type": "string|integer|float|boolean|null",
                        "value": actual_value,
                        "line": line_number,
                        "col": column_number
                    },
                    "is_array": false,
                    "line": property_line,
                    "col": property_column,
                    "type": "optional_type_declaration"
                }
            },
            "line": object_line,
            "col": object_column
        }
    }
}
```

### Value Types

#### String Values
```python
{
    "type": "string",
    "value": "actual string content",
    "line": 1,
    "col": 10
}
```

#### Numeric Values
```python
{
    "type": "integer",  # or "float"
    "value": 42,
    "line": 1,
    "col": 10
}
```

#### Boolean Values
```python
{
    "type": "boolean",
    "value": True,  # or False
    "line": 1,
    "col": 10
}
```

#### Null Values
```python
{
    "type": "null",
    "value": None,
    "line": 1,
    "col": 10
}
```

#### Array Values
```python
[
    {
        "type": "string",
        "value": "item1",
        "line": 1,
        "col": 15
    },
    {
        "type": "string", 
        "value": "item2",
        "line": 1,
        "col": 24
    }
]
```

#### Nested Objects
```python
{
    "name": "NestedObject",
    "body": {
        "nested_property": {
            "value": {...},
            "is_array": false,
            "line": 2,
            "col": 5
        }
    },
    "line": 1,
    "col": 20
}
```

### Token Types

The lexer produces tokens of the following types:

- `IDENTIFIER`: Variable names, type names (e.g., `Config`, `name`)
- `STRING`: String literals (e.g., `"hello world"`)
- `NUMBER`: Numeric literals (e.g., `42`, `3.14`)
- `BOOLEAN`: Boolean literals (`true`, `false`)
- `NULL`: Null literal (`null`)
- `NAMESPACE`: Namespace separator (`::`)
- `PUNCTUATION`: Structural characters (`{`, `}`, `[`, `]`, `=`, `,`, `;`)
- `COMMENT`: Comments (`// comment`, `/* comment */`)
- `WHITESPACE`: Whitespace characters (filtered out in final token list)

## Usage Examples

### Basic Parsing

```python
from cfgpp import loads

config = """
Database {
    host = "localhost"
    port = 5432
    ssl = true
}
"""

result = loads(config)
db_config = result['body']['Database']['body']
host = db_config['host']['value']['value']  # "localhost"
port = db_config['port']['value']['value']  # 5432
```

### Error Handling

```python
from cfgpp import loads
from cfgpp.parser import ConfigParseError
from cfgpp.lexer import LexerError

def safe_parse(config_text):
    try:
        return loads(config_text)
    except ConfigParseError as e:
        print(f"Parse error at line {e.line}: {e.message}")
        return None
    except LexerError as e:
        print(f"Lexer error at line {e.line}: {e.message}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Working with Arrays

```python
from cfgpp import loads

config = """
Config {
    servers = ["web1", "web2", "web3"]
    ports = [80, 443, 8080]
}
"""

result = loads(config)
config_body = result['body']['Config']['body']

# Get array values
servers = [item['value'] for item in config_body['servers']['value']]
ports = [item['value'] for item in config_body['ports']['value']]
```

### Namespaced Types

```python
from cfgpp import loads

config = """
App {
    Database::MySQL db = Database::MySQL {
        host = "mysql.example.com"
        port = 3306
    }
}
"""

result = loads(config)
app_body = result['body']['App']['body']
db_type = app_body['db']['type']  # "Database::MySQL"
db_config = app_body['db']['value']
```

This API reference provides comprehensive information for working with the CFGPP parser programmatically.
