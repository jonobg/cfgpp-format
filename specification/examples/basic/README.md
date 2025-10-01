# Basic CFGPP Examples

**Perfect starting point for learning CFGPP!** ⭐

These examples demonstrate fundamental CFGPP concepts with simple, clear configurations. Start here if you're new to CFGPP or configuration management in general.

## 📚 **Examples in This Category**

| File | Description | Concepts Covered |
|------|-------------|------------------|
| **[hello-world.cfgpp](hello-world.cfgpp)** | Simplest possible configuration | Basic objects, key-value pairs |
| **[data-types.cfgpp](data-types.cfgpp)** | All supported data types | Strings, numbers, booleans, arrays |
| **[comments.cfgpp](comments.cfgpp)** | Comment patterns and documentation | Single-line, multi-line, inline comments |
| **[environment-variables.cfgpp](environment-variables.cfgpp)** | Environment variable usage | `${VAR:-default}` syntax patterns |

## 🎯 **Learning Path**

### **1. Start with Hello World**
The absolute basics - a simple application configuration:
```cfgpp
AppConfig {
    name = "Hello CFGPP",
    version = "1.0.0",
    port = 8080
}
```

### **2. Explore Data Types**
Learn all the types CFGPP supports:
```cfgpp
DataTypes {
    text = "Hello World",           // String
    number = 42,                    // Integer
    decimal = 3.14,                 // Float
    flag = true,                    // Boolean
    items = ["a", "b", "c"],        // Array
    config = { key = "value" }      // Nested object
}
```

### **3. Master Comments**
Document your configurations effectively:
```cfgpp
// Single-line comment
Config {
    setting = "value"  // End-of-line comment
    
    /* Multi-line comment
       for detailed explanations */
}
```

### **4. Use Environment Variables**
Make configurations dynamic and environment-aware:
```cfgpp
Config {
    database_url = ${DATABASE_URL:-"localhost:5432"},
    api_key = ${API_KEY},  // Required environment variable
    debug = ${DEBUG:-false}
}
```

## ✅ **What You'll Learn**

After working through these examples, you'll understand:

- **Basic syntax** - Objects, properties, values
- **Data types** - All supported types and their usage
- **Comments** - How to document configurations effectively  
- **Environment variables** - Dynamic configuration patterns
- **Best practices** - Clean, readable configuration structure

## 🚀 **Next Steps**

Once you're comfortable with these basics:

1. **[Advanced Examples](../advanced/)** - Complex type systems and validation
2. **[AI-Aware Examples](../ai-aware/)** - Revolutionary AI-native features
3. **[Real-World Examples](../real-world/)** - Production use cases

## 🧪 **Testing These Examples**

```bash
# Parse any basic example
cd implementations/python
python -c "from cfgpp.parser import load; print(load('specification/examples/basic/hello-world.cfgpp'))"

# Validate syntax
python -m cfgpp.tools.validate specification/examples/basic/hello-world.cfgpp
```

---

*Master these fundamentals and you'll be ready to explore CFGPP's advanced capabilities!* 🎓
