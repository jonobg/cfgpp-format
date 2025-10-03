# CFG++ Language Support for VS Code

Language support for CFG++ configuration files. Another VS Code extension? Probably useful if you're working with CFG++ files and want syntax highlighting, validation, and auto-completion.

## When This Extension Might Be Useful

- **Large configuration files** where JSON becomes unwieldy
- **Type safety** to prevent configuration errors  
- **Schema validation** for complex configurations
- **Teams using CFG++** for microservice deployments

## When You Probably Don't Need This

- **Simple JSON/YAML configs** work fine for your use case
- **Your team** isn't using CFG++ format
- **You prefer** existing configuration formats

## Why CFG++ Was Created

CFGPP's initial goal was to create a configuration format with **more features than JSON** but **without YAML's indentation dependency**. This makes CFG++ particularly useful in **field environments** - at industrial plants, remote sites, or anywhere you might need to edit configs **without IDE assistance**.

### Practical Field Advantages

- **No indentation sensitivity** - Works fine in basic text editors
- **Explicit braces** - Clear structure without whitespace dependency  
- **Type safety** - Prevents configuration errors in production environments
- **Comments supported** - Document complex industrial configurations
- **Schema validation** - Catch errors before deployment to remote systems

**Perfect for**: Industrial automation, IoT deployments, field engineering, remote system configuration where you can't rely on fancy IDE features.

## What It Does

- **Syntax highlighting** - Colors for `.cfgpp` and `.cfgpp-schema` files
- **Auto-completion** - Suggests identifiers, enum values, and schema elements
- **Validation** - Shows syntax and schema errors
- **Language server** - LSP integration for IDE features
- **Schema support** - Works with `.cfgpp-schema` files for type checking

## Syntax Support

Supports the CFG++ syntax including:

- ✅ **Basic objects**: `ObjectName { property = value }`
- ✅ **Nested objects**: Deep nesting with clean syntax
- ✅ **Arrays**: `[1, 2, 3, "mixed", true]`
- ✅ **Enums**: `enum::Status { values = ["active", "inactive"] }`
- ✅ **Type safety**: Strong typing with validation
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
        host = "localhost"
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
