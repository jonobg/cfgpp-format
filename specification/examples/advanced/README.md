# Advanced CFGPP Examples

This directory contains sophisticated CFGPP configuration examples that demonstrate advanced features and complex use cases.

## Examples

### `complex-config.cfgpp`
A comprehensive example showcasing:
- Complex nested hierarchies
- Type system usage
- Real-world configuration patterns
- Schema validation integration

### `type-reusage.cfgpp`
Demonstrates CFGPP's type system:
- Type definitions with parameters
- Type inheritance and composition
- Reusable configuration patterns

## Features Demonstrated

- **Complex Nesting**: Deep object hierarchies
- **Type Safety**: Strong typing with validation
- **Schema Integration**: Working with `.cfgpp-schema` files
- **Real-world Patterns**: Production-ready configurations

## Usage

These examples require understanding of CFGPP's type system:

```bash
# Parse complex configuration
python -m cfgpp.cli advanced/complex-config.cfgpp

# Validate against schema
python -m cfgpp.cli advanced/complex-config.cfgpp --schema app.cfgpp-schema
```

## Prerequisites

- Familiarity with basic CFGPP syntax (see `../basic/`)
- Understanding of type systems and schema validation

## Next Steps

- Explore `../ai-aware/` for cutting-edge AI-native features
- Study the schema files to understand validation patterns