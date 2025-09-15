//! Error handling for CFG++ parser

use std::fmt;
use thiserror::Error;

/// Result type alias for CFG++ operations
pub type CfgppResult<T> = Result<T, CfgppError>;

/// Comprehensive error type for CFG++ parsing operations
#[derive(Error, Debug, Clone, PartialEq)]
pub enum CfgppError {
    /// Syntax errors during parsing
    #[error("Syntax error at line {line}, column {column}: {message}")]
    SyntaxError {
        message: String,
        line: usize,
        column: usize,
    },

    /// Type errors when accessing values
    #[error("Type error: expected {expected}, found {actual}")]
    TypeError {
        expected: String,
        actual: String,
    },

    /// Key not found in object
    #[error("Key not found: {key}")]
    KeyNotFound { key: String },

    /// Index out of bounds for arrays
    #[error("Index out of bounds: {index}")]
    IndexOutOfBounds { index: usize },

    /// File I/O errors
    #[error("I/O error: {message}")]
    IoError { message: String },

    /// Include directive errors
    #[error("Include error: {path} - {message}")]
    IncludeError { path: String, message: String },

    /// Environment variable expansion errors
    #[error("Environment variable error: {var} - {message}")]
    EnvVarError { var: String, message: String },

    /// Schema validation errors
    #[cfg(feature = "schema-validation")]
    #[error("Schema validation error: {message}")]
    ValidationError { message: String },

    /// Memory allocation errors
    #[error("Memory error: {message}")]
    MemoryError { message: String },

    /// Generic parsing errors
    #[error("Parse error: {message}")]
    ParseError { message: String },
}

impl CfgppError {
    /// Create a new syntax error
    pub fn syntax_error(message: impl Into<String>, line: usize, column: usize) -> Self {
        Self::SyntaxError {
            message: message.into(),
            line,
            column,
        }
    }

    /// Create a new type error
    pub fn type_error(expected: impl Into<String>, actual: impl Into<String>) -> Self {
        Self::TypeError {
            expected: expected.into(),
            actual: actual.into(),
        }
    }

    /// Create a new key not found error
    pub fn key_not_found(key: impl Into<String>) -> Self {
        Self::KeyNotFound { key: key.into() }
    }

    /// Create a new index out of bounds error
    pub fn index_out_of_bounds(index: usize) -> Self {
        Self::IndexOutOfBounds { index }
    }

    /// Create a new I/O error
    pub fn io_error(message: impl Into<String>) -> Self {
        Self::IoError {
            message: message.into(),
        }
    }

    /// Create a new parse error
    pub fn parse_error(message: impl Into<String>) -> Self {
        Self::ParseError {
            message: message.into(),
        }
    }

    /// Check if this is a syntax error
    pub fn is_syntax_error(&self) -> bool {
        matches!(self, CfgppError::SyntaxError { .. })
    }

    /// Check if this is a type error
    pub fn is_type_error(&self) -> bool {
        matches!(self, CfgppError::TypeError { .. })
    }

    /// Get the line number if this is a syntax error
    pub fn line(&self) -> Option<usize> {
        match self {
            CfgppError::SyntaxError { line, .. } => Some(*line),
            _ => None,
        }
    }

    /// Get the column number if this is a syntax error
    pub fn column(&self) -> Option<usize> {
        match self {
            CfgppError::SyntaxError { column, .. } => Some(*column),
            _ => None,
        }
    }
}

impl From<std::io::Error> for CfgppError {
    fn from(err: std::io::Error) -> Self {
        Self::io_error(err.to_string())
    }
}

impl From<std::env::VarError> for CfgppError {
    fn from(err: std::env::VarError) -> Self {
        match err {
            std::env::VarError::NotPresent => {
                Self::env_var_error("unknown", "environment variable not found")
            }
            std::env::VarError::NotUnicode(_) => {
                Self::env_var_error("unknown", "environment variable contains invalid UTF-8")
            }
        }
    }
}

impl CfgppError {
    /// Create a new environment variable error
    pub fn env_var_error(var: impl Into<String>, message: impl Into<String>) -> Self {
        Self::EnvVarError {
            var: var.into(),
            message: message.into(),
        }
    }

    /// Create a new include error
    pub fn include_error(path: impl Into<String>, message: impl Into<String>) -> Self {
        Self::IncludeError {
            path: path.into(),
            message: message.into(),
        }
    }

    #[cfg(feature = "schema-validation")]
    /// Create a new validation error
    pub fn validation_error(message: impl Into<String>) -> Self {
        Self::ValidationError {
            message: message.into(),
        }
    }
}
