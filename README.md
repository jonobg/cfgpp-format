## Quickstart

For a concise set of commands to set up a venv, run the CLI, and run tests, see the [QUICKSTART](./QUICKSTART.md). A convenience script is provided at `scripts/run_example.ps1`.

# cfgpp-format

**cfgpp-format** is a free, open configuration language inspired by C++ for deeply nested, typed settings. This repository contains both the language specification and a Python implementation of a parser.

## Features

- **Familiar syntax:** C++-style declarations and nesting
- **Strong typing:** Type-safe configuration with support for custom types
- **Nested objects:** Hierarchical configuration structure
- **Arrays and containers:** For lists of values or objects
- **Comments:** Both single-line (`//`) and multi-line (`/* */`) comments
- **Human-readable:** Designed to be both machine and human friendly

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cfgpp-format.git
cd cfgpp-format

# Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Unix/macOS

# Install in development mode
pip install -e .
```

## Usage

### Basic Usage

```python
from cfgpp.parser import loads

config = """
AppConfig(
    string name = "test",
    int port = 8080,
    bool debug = true
)
"""

parsed = loads(config)
print(parsed['parameters']['name']['value'])  # Output: test
```

### Command Line Interface

The package includes a CLI tool for parsing cfgpp files:

```bash
# Parse a file and output as JSON
cfgpp examples/complex_config.cfgpp

# Output as YAML (requires PyYAML)
cfgpp examples/complex_config.cfgpp --format yaml

# Read from stdin
echo 'AppConfig(string name="test")' | cfgpp -
```

## Language Reference

### Basic Syntax

```cpp
// Comments start with //
/* Or can be multi-line */

// Basic configuration with parameters
AppConfig(
    string name = "myapp",
    int port = 3000,
    bool debug = true
)

// Arrays
ServerConfig(
    string[] hosts = ["primary", "secondary"],
    int[] ports = [80, 443, 8080]
)

// Nested objects
DatabaseConfig(
    string host = "localhost",
    int port = 5432
) {
    // Object body with nested configuration
    ConnectionPool::pool(
        int min = 5,
        int max = 50
    );
}
```

### Data Types

- `string`: Text values in double quotes (`"text"`)
- `int`: Integer numbers (`42`)
- `float`: Floating-point numbers (`3.14`)
- `bool`: Boolean values (`true` or `false`)
- `array`: Ordered lists of values (`[1, 2, 3]` or `["a", "b", "c"]`)
- Custom types: User-defined objects

## Examples

See the [examples](./examples) directory for more complex configuration examples.

## Development

### Setting Up

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies:

```bash
pip install -r requirements.txt
```

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black src tests

# Check types
mypy src

# Lint code
pylint src
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
