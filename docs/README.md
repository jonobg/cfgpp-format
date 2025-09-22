# CFGPP Documentation

This directory contains comprehensive documentation for the CFGPP configuration format.

## Documentation Structure

### Core Documentation
- **[Getting Started](getting-started.md)** - Basic introduction and setup
- **[Syntax Examples](syntax-examples.md)** - Practical configuration examples  
- **[API Reference](api-reference.md)** - Programming APIs
- **[Language Server Design](language-server-design.md)** - LSP implementation details
- **[Error Handling](error-handling.md)** - Error handling and debugging guide

### Reference Materials
- **[Language Specification](language-specification.md)** - Formal language specification
- **[Contributing](contributing.md)** - How to contribute to CFGPP

### Development Documentation
- **[Development](development/)** - Analysis, resolutions, and meta-documentation

## Quick Links

- **📖 [Syntax Reference](../SYNTAX_REFERENCE.md)** - THE authoritative syntax guide (main reference)
- **🚀 [Quick Start](../QUICKSTART.md)** - Get up and running quickly  
- **📝 [Formal Grammar](../specification/grammar.ebnf)** - EBNF grammar specification

## External Resources

### Language Servers
- **[VS Code Extension](../vscode-extension/)** - Editor support with syntax highlighting and validation
- **[LSP Implementation](language-server-design.md)** - Language Server Protocol details

### Libraries and Bindings
- **[Python Implementation](../implementations/python/)** - Complete Python parser and formatter
- **[Rust Implementation](../implementations/rust/)** - High-performance Rust parser
- **[C++ LabVIEW Implementation](../implementations/cpp-labview/)** - LabVIEW integration

## Documentation Quality Standards

### Testing-First Documentation
All syntax examples in this documentation have been **tested against the actual parser implementation**. This ensures:

- **✅ Accurate syntax patterns** - Every example works with the real parser
- **✅ Reliable user experience** - Users can copy/paste examples with confidence
- **✅ Implementation consistency** - Documentation matches what the code actually does
- **✅ Professional quality** - Zero tolerance for syntax errors in examples

### Single Source of Truth
- **Primary Reference**: [SYNTAX_REFERENCE.md](../SYNTAX_REFERENCE.md) is the authoritative syntax guide
- **Grammar Specification**: [grammar.ebnf](../specification/grammar.ebnf) is the formal language definition
- **Tested Examples**: All examples verified against parser implementation

### Documentation Maintenance

**Critical Rule**: When updating syntax or adding features:
1. **Update the authoritative reference first** ([SYNTAX_REFERENCE.md](../SYNTAX_REFERENCE.md))
2. **Test new syntax against parser** to ensure accuracy
3. **Update related documentation** to maintain consistency
4. **Validate all examples still parse** with the updated implementation

## Getting Help

**Documentation Issues**:
- Syntax examples not working? Check against [SYNTAX_REFERENCE.md](../SYNTAX_REFERENCE.md)
- Parser behavior different than documented? File an issue with the specific example
- Need more examples? Check [syntax-examples.md](syntax-examples.md) first

**Development Questions**:
If you need help or have questions:

1. Check the [Getting Started](getting-started.md) guide
2. Look at the [Examples](examples.md) for common patterns
3. Refer to the [API Reference](api-reference.md) for detailed function documentation
4. Check the [Error Handling](error-handling.md) guide for troubleshooting

## License

This documentation is part of the CFGPP project and follows the same license terms.
