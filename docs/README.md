# CFGPP Documentation

Welcome to the CFGPP (Configuration Plus Plus) parser documentation. This directory contains comprehensive documentation for understanding, using, and extending the CFGPP configuration format and parser.

## Documentation Structure

- [**Getting Started**](getting-started.md) - Quick start guide and installation instructions
- [**Language Specification**](language-specification.md) - Complete CFGPP language syntax and features
- [**API Reference**](api-reference.md) - Python API documentation
- [**Examples**](examples.md) - Practical examples and use cases
- [**Error Handling**](error-handling.md) - Understanding and handling parser errors
- [**Contributing**](contributing.md) - Guidelines for contributing to the project

## What is CFGPP?

CFGPP is a modern, structured configuration format designed to be:

- **Human-readable**: Clean, intuitive syntax
- **Flexible**: Support for complex data structures and namespacing
- **Type-safe**: Built-in type validation and error reporting
- **Extensible**: Support for comments, includes, and expressions

## Quick Example

```cfgpp
// Application Configuration
AppConfig {
    name = "MyApp"
    version = "1.0.0"
    
    server = ServerConfig {
        host = "localhost"
        port = 8080
        ssl = true
    }
    
    database = Database::PostgreSQL {
        host = "db.example.com"
        port = 5432
        credentials = {
            username = "admin"
            password = "${DB_PASSWORD}"
        }
    }
    
    features = ["auth", "logging", "metrics"]
}
```

## Key Features

- **Nested Objects**: Hierarchical configuration structure
- **Namespaced Types**: Organize types with namespace qualifiers
- **Arrays**: Support for lists of values
- **Type Declarations**: Explicit type information for better validation
- **Comments**: Single-line and multi-line comment support
- **Error Reporting**: Detailed error messages with line and column information

## Getting Help

If you need help or have questions:

1. Check the [Getting Started](getting-started.md) guide
2. Look at the [Examples](examples.md) for common patterns
3. Refer to the [API Reference](api-reference.md) for detailed function documentation
4. Check the [Error Handling](error-handling.md) guide for troubleshooting

## License

This project is open source. See the main README for license information.
