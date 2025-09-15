{{ ... }}

For a concise set of commands to set up a venv, run the CLI, and run tests, see the [QUICKSTART](./QUICKSTART.md). A convenience script is provided at `scripts/run_example.ps1`.

# CFG++ Format

A modern, high-performance configuration format with powerful features and multi-language support.

## 🚀 **Multi-Language Implementations**

| Language | Performance | Use Case | Location |
|----------|-------------|----------|----------|
| **Python** | Standard | Tooling, scripting, web apps | [`implementations/python/`](implementations/python/) |
| **Rust** | Blazing fast | High-performance applications | [`implementations/rust/`](implementations/rust/) |
| **C++ LabVIEW** | Optimized | LabVIEW integration, DLLs | [`implementations/cpp-labview/`](implementations/cpp-labview/) |

## ✨ **Features**

- **🎯 Intuitive Syntax**: Clean, readable configuration files
- **🛡️ Schema Validation**: Built-in validation with detailed error messages  
- **🔧 Environment Variables**: Dynamic configuration with `${VAR:-default}` syntax
- **📦 Include Directives**: Modular configuration with `@include`
- **🎪 Type Safety**: Strong typing with custom enum support
- **📝 Comments**: Full comment support for documentation
- **⚡ High Performance**: Zero-copy parsing where possible

## 📖 **Quick Example**

```cfgpp
database {
    host = ${DATABASE_HOST:-"localhost"};
    port = 5432;
    ssl = true;
    
    connection_pool {
        min_connections = 5;
        max_connections = 20;
    }
}

servers = ["web1", "web2", "web3"];
log_level = DEBUG;
```

## 🏗️ **Project Structure**

```
cfgpp-format/
├── implementations/          # Core parsers by language
│   ├── python/              # Python implementation + formatter
│   ├── rust/                # High-performance Rust parser  
│   └── cpp-labview/         # C++ LabVIEW integration
├── bindings/                # Language bindings & FFI
├── tools/                   # Command-line utilities
├── specification/           # Grammar & examples
├── tests/                   # Cross-language tests
├── docs/                    # Documentation
└── vscode-extension/        # VS Code extension
```

## 🚀 **Getting Started**

### Python
```bash
cd implementations/python
pip install -e .
```

### Rust
```bash
cd implementations/rust  
cargo build --release
```

### C++ LabVIEW
```bash
cd implementations/cpp-labview
mkdir build && cd build
cmake .. && make
```

## 📚 **Documentation**

- [Language Guide](docs/language-guide/) - CFG++ syntax and features
- [API References](docs/api-reference/) - Language-specific APIs
- [Integration Guides](docs/integration-guides/) - Usage examples
- [Grammar Specification](specification/grammar.ebnf) - Formal grammar

## 🛠️ **Tools**

- **VS Code Extension**: Syntax highlighting, validation, formatting
- **CLI Tools**: Formatting, validation, conversion utilities
- **Schema Validator**: Comprehensive configuration validation

## 🧪 **Testing**

```bash
# Cross-language conformance tests
./tests/run-conformance-tests.sh

# Performance benchmarks  
./tests/run-benchmarks.sh
```

## 🤝 **Contributing**

1. Choose your implementation language
2. Follow the coding standards in each directory
3. Add tests for new features
4. Update documentation

## 📄 **License**

MIT License - see [LICENSE](LICENSE) for details

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
- `enum`: Enumeration types with constrained value sets
- Custom types: User-defined objects

### Enum Types

Enums define a set of allowed values for type-safe configuration:

```cpp
// Define an enum with possible values
enum::Status {
    values = ["active", "inactive", "pending"]
}

// Define an enum with a default value
enum::LogLevel {
    values = ["debug", "info", "warning", "error"],
    default = "info"
}

// Use enum types in parameters
AppConfig(
    Status status = "active",
    LogLevel logLevel = "warning"
)

// Enum arrays are also supported
UserManager {
    setPermissions(Status[] statuses) {
        statuses = ["active", "pending"]
    }
}
```

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
