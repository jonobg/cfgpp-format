# CFG++ Language Support for VS Code & Windsurf

Professional language support for CFG++ configuration files, providing syntax highlighting, validation, auto-completion, and error checking.

## Features

- **Syntax Highlighting** - Full syntax highlighting for `.cfgpp` and `.cfgpp-schema` files
- **Auto-completion** - Smart completion for identifiers, enum values, and schema elements
- **Validation** - Real-time syntax and schema validation with detailed error messages
- **Language Server** - Full Language Server Protocol (LSP) integration
- **Schema Support** - Integration with `.cfgpp-schema` files for type validation

## Supported Syntax

This extension supports the complete CFG++ syntax including:

- ✅ **Basic objects**: `ObjectName { property = value }`
- ✅ **Nested objects**: Deep nesting with clean syntax
- ✅ **Arrays**: `[1, 2, 3, "mixed", true]`
- ✅ **Enums**: `enum::Status { values = ["active", "inactive"] }`
- ✅ **Environment variables**: `${VAR:-"default"}`
- ✅ **Include directives**: `@include "other.cfgpp"`
- ✅ **Constructor syntax**: `Config(string name = "app") { ... }`
- ✅ **Namespaced identifiers**: `Database::PostgreSQL`
- ✅ **Comments**: Single-line `//` and multi-line `/* */`

## Quick Start

1. Install the extension
2. Create a new `.cfgpp` file
3. Start writing CFG++ configuration:

```cfgpp
// Example CFG++ configuration
AppConfig {
    name = "MyApp"
    version = "1.0.0"
    
    server = ServerConfig {
        host = "localhost"
        port = 8080
        ssl = true
    }
    
    database = Database::PostgreSQL {
        host = ${DB_HOST:-"localhost"}
        port = 5432
    }
}
```

## Documentation

- **📖 [Complete Syntax Reference](../SYNTAX_REFERENCE.md)** - Authoritative syntax guide
- **🚀 [Quick Start Guide](../QUICKSTART.md)** - Get up and running quickly
- **📝 [Examples](../docs/syntax-examples.md)** - Practical configuration examples
- **🔧 [API Reference](../docs/api-reference.md)** - Programming interface documentation

## Requirements

- VS Code 1.75.0 or later (or Windsurf IDE)
- Python 3.8+ (for Language Server features)

## Language Server Features

The extension includes a full Language Server Protocol implementation providing:

- **Real-time validation** with detailed error messages
- **Auto-completion** for identifiers, properties, and enum values
- **Hover information** for schema elements
- **Go to definition** for included files and schema references
- **Document formatting** with configurable styles

## Extension Settings

This extension contributes the following settings:

- `cfgpp.validation.enabled`: Enable/disable syntax validation
- `cfgpp.completion.enabled`: Enable/disable auto-completion
- `cfgpp.formatting.enabled`: Enable/disable document formatting

## Release Notes

### 1.1.0 (Latest)

- **Major Update**: Synchronized with authoritative syntax documentation
- **Verified Syntax**: All syntax patterns tested against actual parser
- **Updated Grammar**: TextMate grammar aligned with parser implementation
- **Better Documentation**: Links to authoritative syntax reference
- **Improved Reliability**: Extension now reflects verified working syntax

### 1.0.4

- Previous release with basic language support

## Contributing

This extension is part of the CFG++ Format project. See the main [Contributing Guide](../CONTRIBUTING.md) for information on how to contribute.

## License

This extension is released under the same license as the main CFG++ Format project. See [LICENSE](../LICENSE) for details.
