# CFG++ Examples

Working examples demonstrating CFG++ features and syntax.

## Available Examples

### Basic (`basic/`)

| File | Description |
|------|-------------|
| **hello-world.cfgpp** | Simple configuration with basic objects and properties |
| **data-types.cfgpp** | Strings, numbers, booleans, arrays |
| **comments.cfgpp** | Line and block comment styles |
| **environment-variables.cfgpp** | `${VAR:-default}` substitution syntax |

### Advanced (`advanced/`)

| File | Description |
|------|-------------|
| **complex-config.cfgpp** | Nested objects, arrays, namespaced types |
| **type-reusage.cfgpp** | Constructor syntax, type parameters |

### Other

| File | Description |
|------|-------------|
| **app.cfgpp-schema** | Schema validation example |
| **cfgpp-format-standard.json** | Standard formatting config (4 spaces) |
| **cfgpp-format-compact.json** | Compact formatting config (2 spaces) |

## Running Examples

```bash
cd implementations/python
pip install -e .

# Parse any example
python -c "from cfgpp import parse_file; print(parse_file('specification/examples/basic/hello-world.cfgpp'))"
```

## Additional Resources

- **[SYNTAX_REFERENCE.md](../../SYNTAX_REFERENCE.md)** - Complete syntax guide
- **[Grammar Specification](../grammar.ebnf)** - Formal grammar definition
