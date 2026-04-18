# CFG++ Python Implementation

Python parser and formatter for CFG++ configuration files.

## Installation

```bash
cd implementations/python
pip install -e .
```

## Quick Start

```python
from cfgpp import parse_file, parse_string, format_string

# Parse a configuration file
config = parse_file("config.cfgpp")

# Parse from string
config = parse_string('AppConfig { name = "test", port = 8080 }')

# Format a configuration string
formatted = format_string(config_text)
```

## CLI Usage

```bash
# Parse and output as JSON
cfgpp config.cfgpp

# Output as YAML
cfgpp config.cfgpp -f yaml

# Validate configuration structure
cfgpp config.cfgpp --validate

# Validate against schema
cfgpp validate config.cfgpp --schema schema.cfgpp-schema

# Read from stdin
echo 'App { name = "test" }' | cfgpp -
```

## Project Structure

```
python/
├── src/cfgpp/
│   ├── __init__.py          # Public API exports
│   ├── core/
│   │   ├── parser.py        # Configuration parser
│   │   ├── lexer.py         # Tokenizer
│   │   └── formatter.py     # Code formatter
│   ├── schema/
│   │   ├── schema_parser.py     # Schema file parser
│   │   ├── schema_validator.py  # Validation engine
│   │   └── integration.py       # Schema-aware parsing
│   └── tools/
│       ├── cli/             # Command-line interface
│       └── language_server.py   # LSP implementation
├── tests/                   # Test suite (98 tests)
└── pyproject.toml           # Package configuration
```

## Development

```bash
pip install -e .[dev]

# Run tests
python -m pytest tests/ -v

# Format code
black src/ tests/

# Lint
flake8 src/ tests/
```

## API Reference

See the [API documentation](../../docs/api-reference.md) for detailed usage.
