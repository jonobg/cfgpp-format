# CFGPP Syntax Reference - AUTHORITATIVE

**⚠️ THIS IS THE DEFINITIVE SYNTAX REFERENCE ⚠️**

This document describes the **actual working syntax** as implemented in the parser, based on analysis of the source code and test suite. This supersedes all other syntax documentation until they are updated to match this reference.

---

## **VERIFIED WORKING SYNTAX**

### **1. Basic Object Definition**

**✅ CONFIRMED WORKING:**
```cfgpp
AppConfig {
    name = "test",
    port = 8080,
    debug = true
}
```

**Key Rules:**
- Object name followed by `{` and `}`
- Properties are `key = value` pairs
- Values can be strings (in quotes), numbers, or booleans (`true`/`false`)
- Commas are optional but recommended for clarity
- Semicolons are optional

### **2. Nested Objects**

**✅ CONFIRMED WORKING:**
```cfgpp
ServerConfig {
    host = "localhost"
    port = 8080
    db = DatabaseConfig {
        name = "mydb"
        user = "admin"
    }
}
```

**Key Rules:**
- Nested objects can be assigned to properties
- Nesting can be arbitrarily deep
- Each nested object follows the same syntax rules

### **3. Arrays**

**✅ CONFIRMED WORKING:**
```cfgpp
ArrayTest {
    values = [1, 2, 3, "test", true]
    mixed_types = [42, "string", true, null]
    servers = ["web1", "web2", "web3"]
}
```

**Key Rules:**
- Arrays use `[` and `]`
- Elements separated by commas
- Mixed types allowed in same array
- Trailing commas are allowed

### **4. Enum Definitions**

**✅ CONFIRMED WORKING:**
```cfgpp
enum::Status {
    values = ["active", "inactive", "pending"]
}

enum::Priority {
    values = ["low", "medium", "high", "critical"],
    default = "medium"
}
```

**Key Rules:**
- Enum syntax: `enum::EnumName { ... }`
- Must have `values = [...]` array
- Optional `default = "value"` property
- Default value must be one of the values in the array

### **5. Namespaced Identifiers**

**✅ CONFIRMED WORKING:**
```cfgpp
Config {
    database = Database::PostgreSQL {
        host = "localhost"
        port = 5432
    }
    
    cache = Storage::Memory::Redis {
        host = "redis.example.com"
        port = 6379
    }
}
```

**Key Rules:**
- Namespaces separated by `::`
- Multiple namespace levels supported
- Used for type organization and avoiding naming conflicts

### **6. Comments**

**✅ CONFIRMED WORKING:**
```cfgpp
// Single-line comment
Config {
    name = "MyApp"  // End-of-line comment
    /*
     * Multi-line comment
     * spanning multiple lines
     */
    port = 8080
}
```

**Key Rules:**
- Single-line: `// comment`
- Multi-line: `/* comment */`
- Comments are ignored during parsing
- Can appear anywhere whitespace is allowed

---

### **7. Type Annotations**

**✅ CONFIRMED WORKING:**
```cfgpp
Config {
    string name = "MyApp"
    int port = 8080
    bool debug = true
    
    // Type annotations help with validation
    string database_url = "localhost:5432"
    string api_key = "your-api-key-here"
}
```

**Key Rules:**
- Type annotations: `string`, `int`, `bool`
- Help with schema validation and IDE support
- Optional but recommended for clarity
- Types must match the assigned values

---

### **8. Include Directives**

**✅ CONFIRMED WORKING:**
```cfgpp
// Include other configuration files
@include "database.cfgpp"
@include "server.cfgpp"

MainConfig {
    name = "MyApp"
}
```

**Key Rules:**
- Use `@include "filename.cfgpp"` syntax
- Included file contents are merged into the current file
- Include directives can appear at the top level
- Files included are parsed and their objects added to the result
- **Note**: `@import` syntax was NOT tested and may not work

---

## **ADVANCED FEATURES**

### **9. Constructor-Style Syntax**

**✅ CONFIRMED WORKING:**
```cfgpp
// Simple constructor
AppConfig(string name = "test") {
    value = "configured"
}

// Complex constructor with multiple typed parameters  
ComplexConfig(
    string appName = "My App",
    string version = "1.0.0", 
    bool debug = true
) {
    server = ServerConfig {
        host = "localhost"
        port = 8080
    }
}
```

**Key Rules:**
- Object name followed by parameter list in parentheses
- Parameters can have type annotations: `string`, `bool`, `int`
- Parameters can have default values with `=`
- Constructor body follows normal object syntax
- This is a more advanced feature for typed configurations

### **Expression Evaluation** ❓
```cfgpp
// UNVERIFIED - claimed in documentation
max_connections = ${CPU_COUNT} * 2 + 10;
service_name = "app-" + ${ENVIRONMENT} + "-v" + ${VERSION};
```

---

## **CONFIRMED WORKING SYNTAX** ✅

Based on **direct testing against the parser**, the following syntax is **verified and working**:

✅ **Basic objects** with properties  
✅ **Nested objects** with arbitrary depth  
✅ **Arrays** with mixed types  
✅ **Enum definitions** with values and defaults  
✅ **Namespaced identifiers** with multiple levels  
✅ **Comments** (single-line and multi-line)  
✅ **Type annotations** with `string`, `int`, `bool`  
✅ **Include directives** with `@include "file.cfgpp"`  
✅ **Constructor syntax** with typed parameters  

## **STILL NEEDS VERIFICATION**

❓ **Expression evaluation** - Mathematical and string operations  
❓ **@import directive** - Alternative to @include (untested)  
❓ **Advanced type validation** - Schema integration features    

---

## **FOR DEVELOPERS**

**If you're implementing CFGPP support:**
- Use the **✅ CONFIRMED WORKING** syntax patterns
- **Avoid** the ❓ unverified patterns until they're tested
- Test any syntax from other documentation files against the actual parser

**If you're writing CFGPP files:**
- Stick to the basic syntax patterns shown above
- They are guaranteed to work with the current parser implementation

---

**Last Updated:** 2025-09-20  
**Based On:** Direct analysis of parser implementation and test suite  
**Status:** Authoritative for confirmed syntax, needs verification for advanced features  
