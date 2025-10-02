# CFGPP Examples

Welcome to the CFGPP example library. This collection demonstrates working CFGPP features and syntax.

## 📁 **Available Examples**

| File | Description | Features Demonstrated |
|------|-------------|----------------------|
| **hello-world.cfgpp** | Simple configuration | Basic objects, properties |
| **type-reusage.cfgpp** | Type definitions and reusage | Constructor syntax, parameters |
| **environment-variables.cfgpp** | Environment variable substitution | `${VAR:-default}` syntax |
| **complex_config.cfgpp** | More complex configuration | Nested objects, arrays |
| **app.cfgpp-schema** | Schema validation example | Schema definition syntax |

## 🔧 **Formatter Configuration**

| File | Description |
|------|-------------|
| **cfgpp-format-standard.json** | Standard formatting (4 spaces) |
| **cfgpp-format-compact.json** | Compact formatting (2 spaces) |

## 🚀 **Getting Started**

### **Basic Configuration**
```cfgpp
// Clean, intuitive syntax
AppConfig {
    name = "My App",
    version = "1.0.0",
    port = 8080
}
```

### **Type System Example**
```cfgpp
// Define reusable types with parameters
ServerConfig(
    string host = "localhost",
    int port = 8080
) {
    max_connections = 100
}

// Reuse types with custom parameters
AppConfig {
    web_server = ServerConfig(
        host = "web.example.com",
        port = 443
    )
}
```

## 🔧 **Running Examples**

```bash
# Install CFGPP parser
cd implementations/python
pip install -e .

# Parse any example
python -c "from cfgpp import parse_file; print(parse_file('specification/examples/hello-world.cfgpp'))"

# Format an example
python -c "from cfgpp import format_string; print(format_string('Config{name=\"test\"}'))"
```

## ✅ **All Examples Tested**

Every example in this directory:
- ✅ **Parses correctly** with the current CFGPP parser
- ✅ **Uses working syntax** only (no unimplemented features)
- ✅ **Demonstrates real functionality** you can use today

Have a great CFGPP configuration pattern? We'd love to include it!

1. **Choose the right category** based on complexity and use case
2. **Follow naming conventions** (kebab-case, descriptive names)
3. **Add comprehensive comments** explaining the configuration
4. **Include a corresponding test** to ensure it works
5. **Update the category README** with your example
## 📚 **Additional Resources**

- **[SYNTAX_REFERENCE.md](../../SYNTAX_REFERENCE.md)** - Complete syntax guide
- **[Grammar Specification](../grammar.ebnf)** - Formal grammar definition
- **[Implementation Guide](../../implementations/)** - Parser implementations

----

*A collection of working CFGPP examples demonstrating the features that actually work. Start with hello-world.cfgpp and work your way up.* 🌲
