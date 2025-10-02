# CFGPP Comprehensive API Examples

## 🎯 **New Clear API (Recommended)**

### Core Parsing Functions

```python
from cfgpp import parse_string, parse_file
from cfgpp.core.parser import ConfigParseError

# Parse configuration from string
config_text = '''
DatabaseConfig::primary(
    string host = "localhost",
    int port = 5432,
    bool ssl_enabled = true
)

AppConfig {
    name = "MyApp",
    debug = true,
    database = DatabaseConfig::primary
}
'''

try:
    # Clear, self-documenting function name
    result = parse_string(config_text)
    print("✅ Parsed successfully!")
except ConfigParseError as e:
    print(f"❌ Parse error: {e}")

# Parse configuration from file
try:
    # Clear, self-documenting function name
    result = parse_file("config.cfgpp")
    print("✅ File parsed successfully!")
except ConfigParseError as e:
    print(f"❌ Parse error: {e}")
except FileNotFoundError:
    print("❌ Configuration file not found")
```

### Advanced Features (Optional)

```python
from cfgpp.core.formatter import format_string, FormatterConfig
from cfgpp.schema import load_schema, validate_config

# Format configuration with custom settings
config_text = '''
ComplexConfig {
    database = DatabaseConfig {
        string host = "prod-db.company.com"
        int port = 5432
    }
    cache = RedisConfig {
        hosts = ["redis1", "redis2", "redis3"]
        int timeout = 5000
    }
}
'''

# Format the configuration
formatted = format_string(config_text, formatter_config)
print("✅ Formatted configuration:")
print(formatted)
```

### Schema Validation

```python
from cfgpp.schema import load_schema, validate_config

# Load schema for validation
schema = load_schema("app_schema.cfgpp-schema")

# Parse and validate configuration
config = parse_file("app_config.cfgpp")
validation_result = validate_config(config, schema)

if validation_result.is_valid:
    print("✅ Configuration is valid!")
else:
    print("❌ Validation errors:")
    for error in validation_result.errors:
        print(f"  - {error.message} (line {error.line})")
```

### Formatting

```python
from cfgpp.core.formatter import format_string, CfgppFormatter, FormatterConfig

# Format configuration text
config_text = "App{name='test',port=8080}"

# Quick formatting
formatted = format_string(config_text)
print(formatted)

# Custom formatting
config = FormatterConfig(
    indent_size=4,
    brace_style="new_line"
)
formatter = CfgppFormatter(config)
formatted = formatter.format(config_text)
print(formatted)
```

### Error Handling Examples

```python
from cfgpp import parse_string, parse_file
from cfgpp.core.parser import ConfigParseError
from cfgpp.core.lexer import LexerError

def safe_parse_string(config_text: str):
    """Example of robust configuration parsing."""
    try:
        return parse_string(config_text), None
    except ConfigParseError as e:
        return None, f"Parse error at line {e.line}, col {e.column}: {e.message}"
    except LexerError as e:
        return None, f"Lexer error at line {e.line}, col {e.column}: {e.message}"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def safe_parse_file(file_path: str):
    """Example of robust file parsing."""
    try:
        return parse_file(file_path), None
    except FileNotFoundError:
        return None, f"Configuration file not found: {file_path}"
    except ConfigParseError as e:
        return None, f"Parse error in {file_path} at line {e.line}: {e.message}"
    except Exception as e:
        return None, f"Error reading {file_path}: {e}"

# Usage examples
config, error = safe_parse_string("App { name = 'test' }")
if error:
    print(f"❌ {error}")
else:
    print("✅ Parsed successfully")

config, error = safe_parse_file("config.cfgpp")
if error:
    print(f"❌ {error}")
else:
    print("✅ File parsed successfully")
```

## ⚠️ **Legacy API (Still Works)**

```python
from cfgpp import loads, load  # Old confusing names

# Legacy functions - still work but less clear
result = loads(config_text)    # Use parse_string() instead
result = load("config.cfgpp")  # Use parse_file() instead

# These work but are not recommended for new code
```

## 🏗️ **Project Structure Examples**

### Core Library Usage
```python
# Direct access to core components
from cfgpp.core.parser import parse_string, ConfigParseError
from cfgpp.core.lexer import lex, LexerError, Token
from cfgpp.core.formatter import format_string

# Low-level parsing
tokens = lex("App { name = 'test' }")
for token in tokens:
    print(f"{token.type}: {token.value}")

# Direct formatter usage
formatted = format_string("App{name='test'}")
print(formatted)
```

### Tools & CLI Usage
```python
# Language server integration
from cfgpp.tools.language_server import CfgppLanguageServer

# CLI command integration
from cfgpp.tools.cli.format_commands import add_formatter_commands
from cfgpp.tools.cli.schema_commands import add_schema_commands
```

### Configuration Utilities
```python
# Feature flags for optional functionality
from cfgpp.core.feature_flags import FeatureFlags

# Configuration formatting
from cfgpp.core.formatter import format_string

# Format configuration for better readability
formatted_config = format_string(config_text)
print("Formatted configuration:")
print(formatted_config)
```

## 🚀 **Advanced Use Cases**

### Microservice Configuration
```python
from cfgpp import parse_file

# Load microservice configuration
config = parse_file("microservice.cfgpp")

# Extract service information
service_name = config["body"]["ServiceConfig"]["body"]["name"]["value"]["value"]
port = config["body"]["ServiceConfig"]["body"]["port"]["value"]["value"]

print(f"Service: {service_name} on port {port}")

# Validate configuration structure
if "ServiceConfig" in config["body"]:
    print("✅ Valid microservice configuration")
else:
    print("❌ Missing ServiceConfig section")
```

### Configuration Merging
```python
def merge_configurations(*config_files):
    """Merge multiple configuration files."""
    merged = {"body": {}}
    
    for file_path in config_files:
        try:
            config = parse_file(file_path)
            merged["body"].update(config["body"])
            print(f"✅ Merged {file_path}")
        except Exception as e:
            print(f"❌ Failed to merge {file_path}: {e}")
    
    return merged

# Usage
base_config = merge_configurations(
    "base.cfgpp",
    "environment.cfgpp", 
    "secrets.cfgpp"
)
```

### Development Workflow
```python
import os
from pathlib import Path
from cfgpp import parse_file
from cfgpp.core.formatter import format_string

def validate_project_configs(project_dir: str):
    """Validate all .cfgpp files in a project."""
    project_path = Path(project_dir)
    config_files = project_path.glob("**/*.cfgpp")
    
    results = []
    for config_file in config_files:
        try:
            config = parse_file(str(config_file))
            results.append({
                'file': config_file,
                'status': 'valid',
                'config': config
            })
            print(f"✅ {config_file.relative_to(project_path)}")
        except Exception as e:
            results.append({
                'file': config_file,
                'status': 'error',
                'error': str(e)
            })
            print(f"❌ {config_file.relative_to(project_path)}: {e}")
    
    return results

# Usage
results = validate_project_configs("./configs")
valid_configs = [r for r in results if r['status'] == 'valid']
print(f"Validated {len(valid_configs)} configuration files")
```

## 🎯 **Key Benefits of New API**

1. **Self-Documenting**: `parse_string()` vs `loads()` - immediately clear what it does
2. **Consistent**: `parse_file()` vs `load()` - follows same naming pattern  
3. **Professional**: Matches industry standards (similar to `json.loads()` → `json_parse()`)
4. **Maintainable**: Easier for new developers to understand the codebase
5. **Future-Proof**: Clear foundation for additional parsing methods

## 💡 **Migration Guide**

```python
# Old (confusing) → New (clear)
loads(text)        → parse_string(text)
load(file)         → parse_file(file)

# Import changes
from cfgpp import loads, load
# becomes
from cfgpp import parse_string, parse_file

# The old functions still work - no breaking changes!
```
