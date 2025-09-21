# CFG++ Format

A modern, high-performance configuration format with powerful features and multi-language support.

**📖 For complete syntax documentation, see [SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)**  
**🚀 For quick setup, see [QUICKSTART.md](QUICKSTART.md)**

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

## 🔧 **Installation**

Choose your preferred implementation:

```bash
# Clone the repository
git clone https://github.com/yourusername/cfgpp-format.git
cd cfgpp-format

# Python implementation
cd implementations/python
pip install -e .

# Rust implementation  
cd implementations/rust
cargo build --release

# C++ LabVIEW implementation
cd implementations/cpp-labview
mkdir build && cd build
cmake .. && cmake --build . --config Release
```

## 📋 **Language Reference**

CFG++ uses a clean, intuitive syntax:

```cfgpp
// Comments start with //
database {
    host = "localhost";
    port = 5432;
    ssl = true;
    
    connection_pool {
        min_connections = 5;
        max_connections = 20;
    }
}

// Environment variables with defaults
api_endpoint = ${API_URL:-"https://api.example.com"};

// Arrays
servers = ["web1", "web2", "web3"];
ports = [80, 443, 8080];

// Include other files
@include "secrets.cfgpp";

// Schema validation with .cfgpp-schema files
```

### **Data Types**
- **Strings**: `"text values"`
- **Numbers**: `42`, `3.14`  
- **Booleans**: `true`, `false`
- **Arrays**: `[1, 2, 3]`, `["a", "b"]`
- **Objects**: `{ key = value; }`
- **Environment Variables**: `${VAR:-default}`

## 📝 **Examples**

See [`specification/examples/`](specification/examples/) for configuration examples and schema definitions.

## 🔧 **Development**

Each implementation has its own development workflow:

- **Python**: See [implementations/python/README.md](implementations/python/README.md)
- **Rust**: See [implementations/rust/README.md](implementations/rust/README.md)  
- **C++ LabVIEW**: See [implementations/cpp-labview/README.md](implementations/cpp-labview/README.md)

## 🤝 **Contributing**

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
