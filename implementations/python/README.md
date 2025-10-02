# CFG++ Python Implementation

Python code that parses and formats CFG++ configuration files. Seems to work reasonably well.

## What It Does

- **Formatter**: Makes configuration files look consistent
- **Schema validation**: Catches common mistakes
- **CLI tools**: Command-line utilities for basic tasks
- **Python API**: If you want to use it programmatically

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

# Run tests (should pass)
python -m pytest tests/

# Format code
python -m cfgpp.cli.format src/
```

## API Reference

See the [API documentation](../../docs/api-reference/python.md) if you need detailed usage examples.
