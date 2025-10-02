# Error Handling in CFGPP

This document explains how to understand and handle errors when parsing CFGPP configuration files.

## Table of Contents

1. [Types of Errors](#types-of-errors)
2. [Error Information](#error-information)
3. [Common Error Scenarios](#common-error-scenarios)
4. [Best Practices](#best-practices)
5. [Debugging Tips](#debugging-tips)

## Types of Errors

CFGPP can encounter two main types of errors during parsing:

### Lexer Errors (`LexerError`)

Lexer errors occur when the parser encounters invalid characters or token sequences that don't match the CFGPP syntax.

**Common causes:**
- Invalid characters (e.g., `@`, `#`, `$` outside of string contexts)
- Malformed namespace separators (e.g., `:::`)
- Unclosed string literals
- Invalid escape sequences

**Example:**
```python
from cfgpp import loads
from cfgpp.lexer import LexerError

try:
    loads("Config { invalid:::syntax }")
except LexerError as e:
    print(f"Lexer error at line {e.line}, column {e.column}: {e.message}")
    # Output: Lexer error at line 1, column 12: Unexpected character: :
```

### Parser Errors (`ConfigParseError`)

Parser errors occur when the tokens are valid but don't form a valid CFGPP structure.

**Common causes:**
- Missing closing braces `}`
- Missing assignment operators `=`
- Invalid value types
- Incomplete namespaced identifiers
- Malformed arrays

**Example:**
```python
from cfgpp import loads
from cfgpp.parser import ConfigParseError

try:
    loads("Config { name = }")
except ConfigParseError as e:
    print(f"Parse error at line {e.line}, column {e.column}: {e.message}")
    # Output: Parse error at line 1, column 16: Expected a value
```

## Error Information

Both error types provide detailed information to help you locate and fix issues:

### Error Properties

- **`message`**: Description of what went wrong
- **`line`**: Line number where the error occurred (1-based)
- **`column`**: Column number where the error occurred (1-based)
- **`context`**: Additional context information (when available)

### Example Error Handler

```python
from cfgpp import loads
from cfgpp.parser import ConfigParseError
from cfgpp.lexer import LexerError

def parse_with_error_handling(config_text, filename="<string>"):
    try:
        return loads(config_text)
    except ConfigParseError as e:
        print(f"Parse error in {filename}:")
        print(f"  Line {e.line}, Column {e.column}: {e.message}")
        if e.context:
            print(f"  Context: {e.context}")
        return None
    except LexerError as e:
        print(f"Lexer error in {filename}:")
        print(f"  Line {e.line}, Column {e.column}: {e.message}")
        return None
    except Exception as e:
        print(f"Unexpected error in {filename}: {e}")
        return None
```

## Common Error Scenarios

### 1. Missing Closing Braces

**Invalid:**
```cfgpp
Config {
    name = "MyApp"
    server = ServerConfig {
        port = 8080
    // Missing closing brace for Config
```

**Error:** `Expected '}' to close object at line X, column Y`

**Fix:** Add the missing closing brace:
```cfgpp
Config {
    name = "MyApp"
    server = ServerConfig {
        port = 8080
    }
}
```

### 2. Missing Assignment Operator

**Invalid:**
```cfgpp
Config {
    name "MyApp"  // Missing =
    port = 8080
}
```

**Error:** `Expected '=' after property name at line 2, column 10`

**Fix:** Add the assignment operator:
```cfgpp
Config {
    name = "MyApp"
    port = 8080
}
```

### 3. Invalid Value Types

**Invalid:**
```cfgpp
Config {
    port = unknown_value  // Undefined identifier
}
```

**Error:** `Expected a value (string, number, boolean, null, array, object, or constructor call) at line 2, column 12`

**Fix:** Use a valid value type:
```cfgpp
Config {
    port = 8080           // Number
    // or
    port = "8080"         // String
    // or
    port = 8080           // Static value
}
```

### 4. Incomplete Namespaced Identifiers

**Invalid:**
```cfgpp
Config {
    Database:: db = Database::MySQL { }  // Trailing ::
}
```

**Error:** `Expected identifier after '::' at line 2, column 14`

**Fix:** Complete the namespace:
```cfgpp
Config {
    Database::MySQL db = Database::MySQL { }
}
```

### 5. Malformed Arrays

**Invalid:**
```cfgpp
Config {
    ports = [80, 443,]    // Trailing comma with no element
    hosts = [80, 443      // Missing closing bracket
}
```

**Error:** `Expected ']' to close array at line X, column Y`

**Fix:** Properly format the array:
```cfgpp
Config {
    ports = [80, 443]     // Remove trailing comma
    hosts = [80, 443]     // Add closing bracket
}
```

### 6. Unclosed String Literals

**Invalid:**
```cfgpp
Config {
    name = "MyApp         // Missing closing quote
    port = 8080
}
```

**Error:** `Unterminated string literal at line 2, column 12`

**Fix:** Close the string literal:
```cfgpp
Config {
    name = "MyApp"
    port = 8080
}
```

### 7. Invalid Escape Sequences

**Invalid:**
```cfgpp
Config {
    path = "C:\Users\App"  // Invalid escape sequence \U
}
```

**Error:** `Invalid escape sequence at line 2, column 15`

**Fix:** Use proper escape sequences:
```cfgpp
Config {
    path = "C:\\Users\\App"     // Escaped backslashes
    // or
    path = "C:/Users/App"       // Forward slashes
}
```

## Best Practices

### 1. Validate Configuration Early

```python
def load_config(config_path):
    try:
        with open(config_path, 'r') as f:
            return loads(f.read())
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return None
    except (ConfigParseError, LexerError) as e:
        print(f"Invalid configuration in {config_path}:")
        print(f"  Line {e.line}, Column {e.column}: {e.message}")
        return None

# Load and validate at startup
config = load_config('app.cfgpp')
if config is None:
    print("Failed to load configuration. Exiting.")
    sys.exit(1)
```

### 2. Provide Context in Error Messages

```python
def parse_config_section(config_text, section_name):
    try:
        return loads(config_text)
    except (ConfigParseError, LexerError) as e:
        raise ConfigParseError(
            f"Error in {section_name} configuration: {e.message}",
            e.line,
            e.column,
            f"Section: {section_name}"
        ) from e
```

### 3. Use Schema Validation

```python
def validate_config_structure(config):
    """Validate the parsed configuration has expected structure."""
    errors = []
    
    if 'body' not in config:
        errors.append("Missing root 'body' element")
        return errors
    
    # Validate required sections
    required_sections = ['AppConfig', 'Database', 'Server']
    for section in required_sections:
        if section not in config['body']:
            errors.append(f"Missing required section: {section}")
    
    # Validate specific properties
    if 'AppConfig' in config['body']:
        app_config = config['body']['AppConfig']['body']
        if 'name' not in app_config:
            errors.append("AppConfig.name is required")
        if 'port' not in app_config:
            errors.append("AppConfig.port is required")
    
    return errors

# Usage
config = loads(config_text)
validation_errors = validate_config_structure(config)
if validation_errors:
    for error in validation_errors:
        print(f"Validation error: {error}")
```

### 4. Gradual Parsing for Large Configs

```python
def parse_config_sections(config_text):
    """Parse configuration in sections to isolate errors."""
    sections = {}
    errors = []
    
    try:
        full_config = loads(config_text)
        return full_config, []
    except (ConfigParseError, LexerError) as e:
        errors.append(f"Global parse error: {e}")
        
        # Try to parse individual sections if full parse fails
        # This would require splitting the config text by sections
        # Implementation depends on your specific needs
        
    return sections, errors
```

## Debugging Tips

### 1. Use Line Numbers

When debugging, always pay attention to line and column numbers in error messages. Most text editors can show line numbers and help you navigate to the exact location.

### 2. Check Bracket Matching

Use an editor with bracket matching to ensure all `{`, `[`, and `(` have corresponding closing brackets.

### 3. Validate JSON Structure

If you're familiar with JSON, remember that CFGPP has similar structural requirements but with different syntax:

| JSON | CFGPP |
|------|-------|
| `{"key": "value"}` | `Object { key = "value" }` |
| `[1, 2, 3]` | `[1, 2, 3]` |
| `true`, `false`, `null` | `true`, `false`, `null` |

### 4. Start Simple

When debugging complex configurations, start with a minimal version and gradually add complexity:

```cfgpp
// Start with this:
Config {
    name = "test"
}

// Then add sections one by one:
Config {
    name = "test"
    server = ServerConfig {
        port = 8080
    }
}

// Continue adding until you find the problematic section
```

### 5. Use Configuration Linters

Consider creating or finding linting tools that can validate CFGPP syntax and common patterns before runtime.

### 6. Enable Detailed Logging

```python
import logging

# Enable debug logging for parsing
logging.basicConfig(level=logging.DEBUG)

# Your parsing code here
try:
    config = loads(config_text)
except Exception as e:
    logging.error(f"Failed to parse configuration: {e}")
    # Log the problematic configuration section
    lines = config_text.split('\n')
    if hasattr(e, 'line') and e.line <= len(lines):
        logging.error(f"Problematic line: {lines[e.line - 1]}")
```

## Error Recovery Strategies

### 1. Default Values

```python
def get_config_value(config, path, default=None):
    """Safely get a configuration value with fallback."""
    try:
        parts = path.split('.')
        current = config
        for part in parts:
            current = current[part]
        return current
    except (KeyError, TypeError):
        return default

# Usage
port = get_config_value(config, 'body.AppConfig.body.port.value.value', 8080)
```

### 2. Partial Parsing

```python
def parse_with_fallbacks(config_text, fallback_config):
    """Parse configuration with fallback to defaults on error."""
    try:
        return loads(config_text)
    except (ConfigParseError, LexerError) as e:
        print(f"Configuration parse failed: {e}")
        print("Using fallback configuration")
        return fallback_config
```

### 3. Configuration Validation

```python
def safe_config_access(config, accessor_func):
    """Safely access configuration with error handling."""
    try:
        return accessor_func(config)
    except (KeyError, TypeError, AttributeError) as e:
        print(f"Configuration access error: {e}")
        return None

# Usage
def get_database_config(config):
    return config['body']['Database']['body']

db_config = safe_config_access(config, get_database_config)
```

By following these error handling practices, you can build robust applications that gracefully handle configuration parsing errors and provide helpful feedback to users and developers.
