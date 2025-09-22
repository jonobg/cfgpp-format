# Getting Started with CFGPP

This guide will help you quickly get up and running with the CFGPP configuration parser.

## Installation

### From Source

1. Clone the repository:
```bash
git clone <repository-url>
cd cfgpp-format
```

2. Install in development mode:
```bash
pip install -e .
```

### From PyPI (when available)

```bash
pip install cfgpp
```

## Basic Usage

### Parsing Configuration Strings

```python
from cfgpp import parse_string

# Parse a configuration string
config_text = """
AppConfig {
    name = "MyApp"
    port = 8080
    debug = true
}
"""

# New clear API (recommended)
result = parse_string(config_text)
print(result)
```

### Parsing Configuration Files

**New Clear API (Recommended):**
```python
from cfgpp import parse_file

# Parse a configuration file  
result = parse_file('config.cfgpp')
```

**Legacy API (Still works):**
```python
from cfgpp import load

# Legacy function (less clear naming)
result = load('config.cfgpp')  # Use parse_file() instead
```

## Understanding the Output Format

The parser returns a structured dictionary with detailed metadata:

```python
{
    "body": {
        "AppConfig": {
            "name": "AppConfig",
            "body": {
                "name": {
                    "value": {
                        "type": "string",
                        "value": "MyApp",
                        "line": 2,
                        "col": 12
                    },
                    "is_array": false,
                    "line": 2,
                    "col": 5
                },
                "port": {
                    "value": {
                        "type": "integer",
                        "value": 8080,
                        "line": 3,
                        "col": 12
                    },
                    "is_array": false,
                    "line": 3,
                    "col": 5
                }
            },
            "line": 1,
            "col": 1
        }
    }
}
```

### Accessing Values

```python
# Get the main configuration object
app_config = result['body']['AppConfig']['body']

# Access simple values
app_name = app_config['name']['value']['value']  # "MyApp"
port = app_config['port']['value']['value']      # 8080

# Access nested objects
if 'database' in app_config:
    db_config = app_config['database']['value']
    # Access nested properties...
```

## Error Handling

The parser provides detailed error information when parsing fails:

```python
from cfgpp import parse_string
from cfgpp.core.parser import ConfigParseError

try:
    result = parse_string("invalid syntax {")
except ConfigParseError as e:
    print(f"Parse error: {e}")
    print(f"Line: {e.line}, Column: {e.column}")
```

## Configuration File Structure

CFGPP files typically follow this structure:

```cfgpp
// Top-level configuration object
MainConfig {
    // Simple key-value pairs
    name = "value"
    number = 42
    flag = true
    
    // Nested objects
    section = SectionType {
        nested_value = "test"
    }
    
    // Arrays
    items = ["item1", "item2", "item3"]
    
    // Namespaced types
    database = Database::PostgreSQL {
        host = "localhost"
        port = 5432
    }
}
```

## Next Steps

- Read the [Language Specification](language-specification.md) for complete syntax details
- Check out [Examples](examples.md) for common configuration patterns
- Review the [API Reference](api-reference.md) for detailed function documentation
- Learn about [Error Handling](error-handling.md) for robust applications

## Common Patterns

### Environment Variables
```cfgpp
Config {
    database_url = "${DATABASE_URL}"
    api_key = "${API_KEY}"
}
```

### Conditional Configuration
```cfgpp
Config {
    environment = "development"
    
    development = DevConfig {
        debug = true
        log_level = "DEBUG"
    }
    
    production = ProdConfig {
        debug = false
        log_level = "INFO"
    }
}
```

### Modular Configuration
```cfgpp
// Use namespaced types for organization
AppConfig {
    server = Network::Server {
        host = "0.0.0.0"
        port = 8080
    }
    
    cache = Storage::Redis {
        host = "redis.example.com"
        port = 6379
    }
}
```
