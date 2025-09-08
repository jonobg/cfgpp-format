# CFGPP Language Specification

This document provides the complete specification for the CFGPP (Configuration Plus Plus) language syntax.

## Table of Contents

1. [Lexical Elements](#lexical-elements)
2. [Basic Types](#basic-types)
3. [Objects](#objects)
4. [Arrays](#arrays)
5. [Namespaced Identifiers](#namespaced-identifiers)
6. [Comments](#comments)
7. [Grammar](#grammar)
8. [Examples](#examples)

## Lexical Elements

### Identifiers

Identifiers are used for object names, property names, and type names.

```
identifier := [a-zA-Z_][a-zA-Z0-9_]*
```

Examples:
- `AppConfig`
- `database_host`
- `_internal`
- `Config2`

### Keywords

CFGPP has the following reserved keywords:
- `true` - Boolean true value
- `false` - Boolean false value  
- `null` - Null value

### Operators and Punctuation

- `=` - Assignment operator
- `{` `}` - Object delimiters
- `[` `]` - Array delimiters
- `(` `)` - Parameter delimiters (future use)
- `,` - Separator
- `;` - Statement terminator (optional)
- `::` - Namespace separator

### Whitespace

Whitespace (spaces, tabs, newlines) is ignored except for line/column tracking in error reporting.

## Basic Types

### Strings

String literals are enclosed in double quotes and support escape sequences:

```cfgpp
name = "Hello, World!"
path = "C:\\Program Files\\MyApp"
multiline = "Line 1\nLine 2\nLine 3"
```

Supported escape sequences:
- `\"` - Double quote
- `\\` - Backslash
- `\n` - Newline
- `\r` - Carriage return
- `\t` - Tab

### Numbers

Numbers can be integers or floating-point values:

```cfgpp
port = 8080
timeout = 30.5
scientific = 1.23e-4
```

### Booleans

Boolean values are `true` and `false`:

```cfgpp
debug = true
production = false
```

### Null

The `null` value represents absence of a value:

```cfgpp
optional_field = null
```

## Objects

Objects are the primary structural element in CFGPP. They contain key-value pairs and can be nested.

### Basic Object Syntax

```cfgpp
ObjectName {
    property = value
    another_property = "string value"
}
```

### Typed Properties

Properties can have explicit type declarations:

```cfgpp
Config {
    string name = "MyApp"
    int port = 8080
    bool debug = true
}
```

### Nested Objects

Objects can contain other objects:

```cfgpp
AppConfig {
    server = ServerConfig {
        host = "localhost"
        port = 8080
        ssl = SSLConfig {
            enabled = true
            cert_path = "/etc/ssl/cert.pem"
        }
    }
}
```

### Object Constructors

Objects can be constructed with type names:

```cfgpp
Config {
    database = PostgreSQLConfig {
        host = "db.example.com"
        port = 5432
    }
}
```

## Arrays

Arrays contain ordered lists of values of any type:

### Basic Arrays

```cfgpp
Config {
    ports = [80, 443, 8080]
    hosts = ["web1.example.com", "web2.example.com"]
    flags = [true, false, true]
}
```

### Mixed Type Arrays

```cfgpp
Config {
    mixed = [42, "string", true, null]
}
```

### Arrays of Objects

```cfgpp
Config {
    servers = [
        ServerConfig { host = "server1", port = 8080 },
        ServerConfig { host = "server2", port = 8081 }
    ]
}
```

### Trailing Commas

Trailing commas are allowed in arrays:

```cfgpp
Config {
    items = [
        "item1",
        "item2",
        "item3",  // trailing comma allowed
    ]
}
```

## Namespaced Identifiers

Namespaces provide a way to organize types and avoid naming conflicts:

### Namespace Syntax

```cfgpp
namespace_name::type_name
```

### Examples

```cfgpp
Config {
    // Namespaced type declarations
    Database::MySQL db1 = Database::MySQL {
        host = "mysql.example.com"
        port = 3306
    }
    
    Database::PostgreSQL db2 = Database::PostgreSQL {
        host = "postgres.example.com"
        port = 5432
    }
    
    // Nested namespaces
    cache = Storage::Memory::Redis {
        host = "redis.example.com"
        port = 6379
    }
}
```

### Namespace Rules

1. Namespaces are separated by `::`
2. Multiple namespace levels are supported
3. Namespaces can contain letters, numbers, and underscores
4. Namespaces are case-sensitive

## Comments

Comments provide documentation and are ignored during parsing:

### Single-line Comments

```cfgpp
// This is a single-line comment
Config {
    name = "MyApp"  // End-of-line comment
    port = 8080
}
```

### Multi-line Comments

```cfgpp
/*
 * This is a multi-line comment
 * spanning multiple lines
 */
Config {
    /*
     * Detailed configuration for
     * the application server
     */
    server = ServerConfig {
        host = "localhost"
        port = 8080
    }
}
```

## Grammar

Here's the formal grammar for CFGPP in EBNF notation:

```ebnf
configuration ::= object

object ::= identifier "{" object_body "}"

object_body ::= (property | nested_object)*

property ::= [type_declaration] identifier "=" value

type_declaration ::= namespaced_identifier

value ::= string | number | boolean | null | array | object_constructor

array ::= "[" [value ("," value)* [","]] "]"

object_constructor ::= namespaced_identifier "{" object_body "}"

namespaced_identifier ::= identifier ("::" identifier)*

identifier ::= [a-zA-Z_][a-zA-Z0-9_]*

string ::= '"' (escape_sequence | [^"\\])* '"'

number ::= integer | float

integer ::= [+-]?[0-9]+

float ::= [+-]?[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?

boolean ::= "true" | "false"

null ::= "null"

comment ::= single_line_comment | multi_line_comment

single_line_comment ::= "//" [^\r\n]* [\r\n]

multi_line_comment ::= "/*" .* "*/"
```

## Examples

### Complete Application Configuration

```cfgpp
// Main application configuration
AppConfig {
    // Basic application metadata
    string name = "MyWebApp"
    string version = "2.1.0"
    bool debug = false
    
    // Server configuration
    server = Network::HTTP::Server {
        host = "0.0.0.0"
        port = 8080
        ssl = true
        max_connections = 1000
        
        // SSL configuration
        ssl_config = Security::SSL {
            cert_file = "/etc/ssl/certs/app.crt"
            key_file = "/etc/ssl/private/app.key"
            protocols = ["TLSv1.2", "TLSv1.3"]
        }
    }
    
    // Database configurations
    databases = [
        Database::PostgreSQL {
            name = "primary"
            host = "db1.example.com"
            port = 5432
            pool_size = 20
        },
        Database::Redis {
            name = "cache"
            host = "redis.example.com"
            port = 6379
            db = 0
        }
    ]
    
    // Feature flags
    features = Features::Manager {
        enabled_features = [
            "authentication",
            "logging",
            "metrics",
            "rate_limiting"
        ]
        
        feature_configs = [
            Features::Auth {
                provider = "oauth2"
                timeout = 30.0
            },
            Features::Logging {
                level = "INFO"
                format = "json"
                outputs = ["console", "file"]
            }
        ]
    }
    
    // Environment-specific overrides
    environments = Environments::Config {
        development = DevConfig {
            debug = true
            log_level = "DEBUG"
            hot_reload = true
        }
        
        production = ProdConfig {
            debug = false
            log_level = "WARN"
            compression = true
            caching = true
        }
    }
}
```

This specification covers the complete CFGPP language syntax. For practical usage examples, see the [Examples](examples.md) documentation.
