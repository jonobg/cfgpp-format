//! CFG++ Value representation and manipulation

use std::collections::HashMap;
use std::fmt;
use crate::error::{CfgppError, CfgppResult};

#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};

/// Represents a CFG++ value - the core data type
#[derive(Debug, Clone, PartialEq)]

pub enum CfgppValue {
    /// Null value
    Null,
    /// Boolean value
    Boolean(bool),
    /// Integer value (i64 for maximum compatibility)
    Integer(i64),
    /// Floating-point value
    Double(f64),
    /// String value
    String(String),
    /// Enum value (represented as a string)
    Enum(String),
    /// Array of values
    Array(Vec<CfgppValue>),
    /// Object (key-value pairs)
    Object(HashMap<String, CfgppValue>),
}

impl CfgppValue {
    /// Create a new null value
    pub fn null() -> Self {
        Self::Null
    }

    /// Create a new boolean value
    pub fn boolean(value: bool) -> Self {
        Self::Boolean(value)
    }

    /// Create a new integer value
    pub fn integer(value: i64) -> Self {
        Self::Integer(value)
    }

    /// Create a new double value
    pub fn double(value: f64) -> Self {
        Self::Double(value)
    }

    /// Create a new string value
    pub fn string(value: impl Into<String>) -> Self {
        Self::String(value.into())
    }

    /// Create a new enum value
    pub fn enum_value(value: impl Into<String>) -> Self {
        Self::Enum(value.into())
    }

    /// Create a new empty array
    pub fn array() -> Self {
        Self::Array(Vec::new())
    }

    /// Create a new array with values
    pub fn array_with_values(values: Vec<CfgppValue>) -> Self {
        Self::Array(values)
    }

    /// Create a new empty object
    pub fn object() -> Self {
        Self::Object(HashMap::new())
    }

    /// Create a new object with values
    pub fn object_with_values(values: HashMap<String, CfgppValue>) -> Self {
        Self::Object(values)
    }

    /// Get the type of this value as a string
    pub fn type_name(&self) -> &'static str {
        match self {
            Self::Null => "null",
            Self::Boolean(_) => "boolean",
            Self::Integer(_) => "integer",
            Self::Double(_) => "double",
            Self::String(_) => "string",
            Self::Enum(_) => "enum",
            Self::Array(_) => "array",
            Self::Object(_) => "object",
        }
    }

    /// Check if this value is null
    pub fn is_null(&self) -> bool {
        matches!(self, Self::Null)
    }

    /// Check if this value is a boolean
    pub fn is_boolean(&self) -> bool {
        matches!(self, Self::Boolean(_))
    }

    /// Check if this value is an integer
    pub fn is_integer(&self) -> bool {
        matches!(self, Self::Integer(_))
    }

    /// Check if this value is a double
    pub fn is_double(&self) -> bool {
        matches!(self, Self::Double(_))
    }

    /// Check if this value is a string
    pub fn is_string(&self) -> bool {
        matches!(self, Self::String(_))
    }

    /// Check if this value is an enum
    pub fn is_enum(&self) -> bool {
        matches!(self, Self::Enum(_))
    }

    /// Check if this value is an array
    pub fn is_array(&self) -> bool {
        matches!(self, Self::Array(_))
    }

    /// Check if this value is an object
    pub fn is_object(&self) -> bool {
        matches!(self, Self::Object(_))
    }

    /// Get this value as a boolean, if possible
    pub fn as_boolean(&self) -> Option<bool> {
        match self {
            Self::Boolean(b) => Some(*b),
            _ => None,
        }
    }

    /// Get this value as an integer, if possible
    pub fn as_integer(&self) -> Option<i64> {
        match self {
            Self::Integer(i) => Some(*i),
            _ => None,
        }
    }

    /// Get this value as a double, if possible
    pub fn as_double(&self) -> Option<f64> {
        match self {
            Self::Double(d) => Some(*d),
            _ => None,
        }
    }

    /// Get this value as a string, if possible
    pub fn as_string(&self) -> Option<&str> {
        match self {
            Self::String(s) | Self::Enum(s) => Some(s),
            _ => None,
        }
    }

    /// Get this value as an array, if possible
    pub fn as_array(&self) -> Option<&Vec<CfgppValue>> {
        match self {
            Self::Array(arr) => Some(arr),
            _ => None,
        }
    }

    /// Get this value as a mutable array, if possible
    pub fn as_array_mut(&mut self) -> Option<&mut Vec<CfgppValue>> {
        match self {
            Self::Array(arr) => Some(arr),
            _ => None,
        }
    }

    /// Get this value as an object, if possible
    pub fn as_object(&self) -> Option<&HashMap<String, CfgppValue>> {
        match self {
            Self::Object(obj) => Some(obj),
            _ => None,
        }
    }

    /// Get this value as a mutable object, if possible
    pub fn as_object_mut(&mut self) -> Option<&mut HashMap<String, CfgppValue>> {
        match self {
            Self::Object(obj) => Some(obj),
            _ => None,
        }
    }

    /// Get a value by key (for objects)
    pub fn get(&self, key: &str) -> Option<&CfgppValue> {
        self.as_object()?.get(key)
    }

    /// Get a mutable value by key (for objects)
    pub fn get_mut(&mut self, key: &str) -> Option<&mut CfgppValue> {
        self.as_object_mut()?.get_mut(key)
    }

    /// Get a value by index (for arrays)
    pub fn get_index(&self, index: usize) -> Option<&CfgppValue> {
        self.as_array()?.get(index)
    }

    /// Get a mutable value by index (for arrays)
    pub fn get_index_mut(&mut self, index: usize) -> Option<&mut CfgppValue> {
        self.as_array_mut()?.get_mut(index)
    }

    /// Get a value by path (e.g., "database.host" or "servers[0].name")
    pub fn get_path(&self, path: &str) -> Option<&CfgppValue> {
        let mut current = self;
        
        for part in path.split('.') {
            if part.contains('[') && part.ends_with(']') {
                // Handle array indexing like "servers[0]"
                let bracket_pos = part.find('[')?;
                let field = &part[..bracket_pos];
                let index_str = &part[bracket_pos + 1..part.len() - 1];
                let index: usize = index_str.parse().ok()?;
                
                if !field.is_empty() {
                    current = current.get(field)?;
                }
                current = current.get_index(index)?;
            } else {
                current = current.get(part)?;
            }
        }
        
        Some(current)
    }

    /// Set a value by key (for objects)
    pub fn set(&mut self, key: impl Into<String>, value: CfgppValue) -> CfgppResult<()> {
        match self {
            Self::Object(obj) => {
                obj.insert(key.into(), value);
                Ok(())
            }
            _ => Err(CfgppError::type_error("object", self.type_name())),
        }
    }

    /// Push a value to an array
    pub fn push(&mut self, value: CfgppValue) -> CfgppResult<()> {
        match self {
            Self::Array(arr) => {
                arr.push(value);
                Ok(())
            }
            _ => Err(CfgppError::type_error("array", self.type_name())),
        }
    }

    /// Get the length of an array or object
    pub fn len(&self) -> usize {
        match self {
            Self::Array(arr) => arr.len(),
            Self::Object(obj) => obj.len(),
            _ => 0,
        }
    }

    /// Check if an array or object is empty
    pub fn is_empty(&self) -> bool {
        match self {
            Self::Array(arr) => arr.is_empty(),
            Self::Object(obj) => obj.is_empty(),
            _ => false,
        }
    }

    /// Convert this value to a JSON-compatible representation
    #[cfg(feature = "serde")]
    pub fn to_json(&self) -> CfgppResult<String> {
        serde_json::to_string_pretty(self)
            .map_err(|e| CfgppError::parse_error(e.to_string()))
    }

    /// Create a value from JSON
    #[cfg(feature = "serde")]
    pub fn from_json(json: &str) -> CfgppResult<Self> {
        serde_json::from_str(json)
            .map_err(|e| CfgppError::parse_error(e.to_string()))
    }
}

impl fmt::Display for CfgppValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Null => write!(f, "null"),
            Self::Boolean(b) => write!(f, "{}", b),
            Self::Integer(i) => write!(f, "{}", i),
            Self::Double(d) => write!(f, "{}", d),
            Self::String(s) => write!(f, "\"{}\"", s),
            Self::Enum(e) => write!(f, "{}", e),
            Self::Array(arr) => {
                write!(f, "[")?;
                for (i, item) in arr.iter().enumerate() {
                    if i > 0 {
                        write!(f, ", ")?;
                    }
                    write!(f, "{}", item)?;
                }
                write!(f, "]")
            }
            Self::Object(obj) => {
                write!(f, "{{")?;
                for (i, (key, value)) in obj.iter().enumerate() {
                    if i > 0 {
                        write!(f, ", ")?;
                    }
                    write!(f, "{}: {}", key, value)?;
                }
                write!(f, "}}")
            }
        }
    }
}

// Convenient From implementations
impl From<bool> for CfgppValue {
    fn from(value: bool) -> Self {
        Self::Boolean(value)
    }
}

impl From<i32> for CfgppValue {
    fn from(value: i32) -> Self {
        Self::Integer(value as i64)
    }
}

impl From<i64> for CfgppValue {
    fn from(value: i64) -> Self {
        Self::Integer(value)
    }
}

impl From<f32> for CfgppValue {
    fn from(value: f32) -> Self {
        Self::Double(value as f64)
    }
}

impl From<f64> for CfgppValue {
    fn from(value: f64) -> Self {
        Self::Double(value)
    }
}

impl From<String> for CfgppValue {
    fn from(value: String) -> Self {
        Self::String(value)
    }
}

impl From<&str> for CfgppValue {
    fn from(value: &str) -> Self {
        Self::String(value.to_string())
    }
}

impl From<Vec<CfgppValue>> for CfgppValue {
    fn from(value: Vec<CfgppValue>) -> Self {
        Self::Array(value)
    }
}

impl From<HashMap<String, CfgppValue>> for CfgppValue {
    fn from(value: HashMap<String, CfgppValue>) -> Self {
        Self::Object(value)
    }
}
