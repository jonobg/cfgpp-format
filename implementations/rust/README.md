# CFG++ Rust Implementation

High-performance Rust implementation of the CFG++ parser with zero-copy parsing and advanced optimizations.

## Features

- **🚀 Blazing Fast**: Zero-copy parsing with SIMD optimizations
- **🛡️ Memory Safe**: Rust's ownership system prevents memory errors
- **🔧 Schema Validation**: Built-in schema validation with detailed errors
- **📦 Serde Integration**: Seamless JSON/TOML/YAML conversion
- **🧵 Thread Safe**: Concurrent parsing and processing
- **📊 Benchmarked**: Comprehensive performance test suite

## Performance

```
Basic Config (1KB):     ~50μs
Large Config (100KB):   ~2ms  
Nested Objects:         ~100μs
Schema Validation:      ~200μs
```

## Installation

```bash
# Add to Cargo.toml
[dependencies]
cfgpp = "0.1.0"

# Or install CLI
cargo install cfgpp-cli
```

## Quick Start

```rust
use cfgpp::{Parser, CfgppValue};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = r#"
    database {
        host = "localhost";
        port = 5432;
        ssl = true;
    }
    "#;

    let mut parser = Parser::new();
    let value: CfgppValue = parser.parse(config)?;
    
    // Access values with type safety
    if let Some(host) = value.get_path("database.host").as_string() {
        println!("Database host: {}", host);
    }
    
    Ok(())
}
```

## Advanced Features

```rust
use cfgpp::{Parser, ParserOptions, Schema};

// Custom parser options
let options = ParserOptions {
    expand_env_vars: true,
    process_includes: true,
    max_include_depth: 5,
    ..Default::default()
};

let mut parser = Parser::with_options(options);

// Schema validation
let schema = Schema::parse_file("config.schema")?;
let config = parser.parse_file("config.cfgpp")?;
schema.validate(&config)?;

// Convert to JSON
let json = config.to_json()?;
```

## Benchmarks

```bash
# Run performance benchmarks
cargo bench

# View benchmark results
open target/criterion/report/index.html
```

## Features

Available features:
- `std` (default): Standard library support
- `serde`: JSON/TOML/YAML serialization  
- `schema-validation`: Schema validation support
- `parallel`: Parallel processing with rayon
- `mmap`: Memory-mapped file I/O
- `simd`: SIMD optimizations

```bash
# Enable all features
cargo build --all-features

# Minimal build
cargo build --no-default-features --features std
```

## API Reference

See the [Rust API documentation](../../docs/api-reference/rust.md) for complete details.
