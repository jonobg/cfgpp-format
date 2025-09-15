# CFG++ Python Implementation

The original Python implementation providing formatting, parsing, and tooling for CFG++ configuration files.

## Features

- **Fast Formatter**: Clean, consistent code formatting
- **Schema Validation**: Validate configurations against schemas
- **CLI Tools**: Command-line utilities for common tasks
- **Python API**: Programmatic access to parser and formatter

## Installation

```bash
# From source
pip install -e .

# From PyPI (when published)
pip install cfgpp
```

## Quick Start

```python
import cfgpp

# Parse a configuration file
config = cfgpp.parse_file("config.cfgpp")

# Format a configuration string
formatted = cfgpp.format_string(config_text)

# Validate against schema
schema = cfgpp.load_schema("schema.cfgpp-schema")
errors = cfgpp.validate(config, schema)
```

## CLI Usage

```bash
# Format files
cfgpp-format config.cfgpp

# Validate configuration
cfgpp-validate --schema schema.cfgpp-schema config.cfgpp

# Convert to JSON
cfgpp-convert --to json config.cfgpp
```

## Project Structure

```
python/
├── src/cfgpp/           # Python package
│   ├── __init__.py      # Main API
│   ├── formatter.py     # Code formatter
│   ├── parser.py        # Configuration parser
│   ├── validator.py     # Schema validation
│   └── cli/             # Command-line tools
├── tests/               # Python-specific tests
├── setup.py             # Package setup
└── requirements.txt     # Dependencies
```

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run formatter on itself
python -m cfgpp.cli.format src/
```

## API Reference

See the [full API documentation](../../docs/api-reference/python.md) for detailed usage examples.
