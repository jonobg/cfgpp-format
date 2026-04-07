# CFG++ Format

## Another Configuration Format

We ran into some annoying problems with existing formats and built something that might be slightly less problematic. Has a working Python implementation and VS Code extension.

**For complete syntax documentation, see [SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)**  
**For quick setup, see [QUICKSTART.md](QUICKSTART.md)**

---

## Current Status

**Python Implementation** (~5,700 lines) - working parser, formatter, schema validation  
**VS Code Extension** published on both marketplaces:
   - [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=cfgpp-format.cfgpp-language-support)
   - [Open VSX Registry](https://open-vsx.org/extension/cfgpp/cfgpp-language-support)  
**98 Tests Passing**

### What's Actually There
- **~1,400 lines** Python parser
- **~800 lines** formatter
- **~500 lines** Language Server (basic IDE integration)
- **~1,400 lines** schema validation

---

## Implementations

| Language | Status | Location |
|----------|--------|----------|
| **Python** | Working | [`implementations/python/`](implementations/python/) |
| **Rust** | In progress | [`implementations/rust/`](implementations/rust/) |
| **C++ LabVIEW** | Planned | [`implementations/cpp-labview/`](implementations/cpp-labview/) |

---

## What It Does

- **Readable syntax**: C-like nested configuration with `()` for declarations and `{}` for children
- **Schema validation**: Catches mistakes before they cause problems
- **Type annotations**: `string name = "value"` syntax for type safety
- **Namespaced identifiers**: `Database::PostgreSQL` for organization
- **Comments**: `//` and `/* */` style, like C
- **VS Code support**: Syntax highlighting

---

## Quick Example

```cfgpp
database {
    host = "localhost"
    port = 5432
    ssl = true
    
    connection_pool {
        min_connections = 5
        max_connections = 20
    }
}

servers = ["web1", "web2", "web3"]
log_level = "DEBUG"
```

### Constructor Style
```cfgpp
// Define types with parameters and nested children
DatabaseConfig(
    string host = "localhost",
    int port = 5432
) {
    connection_pool {
        min_connections = 5
        max_connections = 50
    }
}

// Instantiate with custom parameters
DatabaseConfig::primary(
    host = "db.example.com",
    port = 5432
)
```

## Repository Structure

```
cfgpp-format/
├── implementations/          # Code that does the parsing
│   ├── python/              # Working (~5.7K lines)
│   ├── rust/                # In progress
│   └── cpp-labview/         # Planned
├── specification/           # Grammar (EBNF) and examples
├── vscode-extension/        # VS Code extension (syntax highlighting)
└── docs/                    # Documentation
```

---

## Getting Started

### Install
```bash
cd implementations/python
pip install -e .
```

### Quick Test
```bash
python -c "from cfgpp import load; print('CFG++ loaded')"
```

### Run Tests
```bash
cd implementations/python
python -m pytest tests/ -v
# Expected: 98 tests passing
```

### VS Code Extension
Available on VS Code Marketplace and Eclipse Open VSX Registry - search for "cfgpp".

---

## Documentation

- **[SYNTAX_REFERENCE.md](SYNTAX_REFERENCE.md)** - Complete syntax guide
- **[QUICKSTART.md](QUICKSTART.md)** - Get running quickly
- **[specification/examples/](specification/examples/)** - Working examples
- **[specification/grammar.ebnf](specification/grammar.ebnf)** - Formal grammar specification
- **[docs/api-reference.md](docs/api-reference.md)** - API documentation

---

## Contributing

```bash
# Set up development environment
cd implementations/python
pip install -e .[dev]

# Run quality checks before committing
black src/ tests/
flake8 src/ tests/
mypy src/
python -m pytest tests/ -v
```

---

## License

**MIT License** - see [LICENSE](LICENSE) for details.
