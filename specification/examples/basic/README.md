# Basic CFGPP Examples

This directory contains fundamental CFGPP configuration examples that demonstrate core syntax and features.

## Examples

### `hello-world.cfgpp`
The simplest possible CFGPP configuration. Perfect for getting started.

### `data-types.cfgpp`
Demonstrates all supported CFGPP data types:
- Strings, numbers, booleans
- Arrays (homogeneous and mixed)
- Nested objects

### `comments.cfgpp`
Shows comment syntax and documentation patterns:
- Single-line comments (`//`)
- Multi-line comments (`/* */`)
- Inline comments
- Documentation best practices

### `environment-variables.cfgpp`
Environment variable usage patterns for different deployment environments.

## Usage

Parse any example with the CFGPP CLI:

```bash
# Parse to JSON
python -m cfgpp.cli basic/hello-world.cfgpp

# Parse to YAML
python -m cfgpp.cli basic/data-types.cfgpp --format yaml
```

## Next Steps

- Check out `../advanced/` for complex type system examples
- See `../ai-aware/` for AI-native features like hash validation and compression