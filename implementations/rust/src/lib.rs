//! # CFG++ Parser
//! 
//! High-performance parser for CFG++ configuration format.
//! 
//! ## Features
//! 
//! - **Zero-copy parsing** where possible
//! - **SIMD-optimized** lexing and parsing
//! - **Memory-mapped I/O** for large files
//! - **Schema validation** with detailed error reporting
//! - **Environment variable expansion**
//! - **Include directive support**
//! - **Thread-safe** operations
//! - **Serde integration** for seamless serialization
//! 
//! ## Quick Start
//! 
//! ```rust
//! use cfgpp::{CfgppValue, Parser};
//! 
//! let config = r#"
//! database {
//!     host = "localhost";
//!     port = 5432;
//!     ssl = true;
//! }
//! "#;
//! 
//! let mut parser = Parser::new();
//! let value: CfgppValue = parser.parse(config)?;
//! 
//! // Access values
//! if let Some(host) = value.get_path("database.host").as_string() {
//!     println!("Database host: {}", host);
//! }
//! # Ok::<(), Box<dyn std::error::Error>>(())
//! ```

pub mod ast;
pub mod error;
pub mod lexer;
pub mod parser;
pub mod schema;
pub mod value;

#[cfg(feature = "serde")]
pub mod serde_support;

pub use ast::*;
pub use error::*;
pub use parser::*;
pub use value::*;

/// Re-export of commonly used types
pub mod prelude {
    pub use crate::{CfgppValue, Parser, CfgppError, CfgppResult};
    
    #[cfg(feature = "schema-validation")]
    pub use crate::schema::{Schema, ValidationError};
}

/// Current version of the CFG++ parser
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
