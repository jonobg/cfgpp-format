//! Schema validation support for CFG++ format

#[cfg(feature = "schema-validation")]
use jsonschema::{JSONSchema, ValidationError as JsonValidationError};
use crate::{
    error::{CfgppError, CfgppResult},
    value::CfgppValue,
};
use std::collections::HashMap;
use regex::Regex;

/// Schema definition for CFG++ values
#[derive(Debug, Clone)]
pub struct Schema {
    /// Type definitions (name -> type)
    type_defs: HashMap<String, TypeDefinition>,
    /// Enum definitions (name -> possible values)
    enum_defs: HashMap<String, Vec<String>>,
    /// Object schemas (name -> field definitions)
    object_schemas: HashMap<String, HashMap<String, FieldDefinition>>,
    /// Root schema definition
    root_schema: Option<TypeDefinition>,
}

/// Type definition for schema validation
#[derive(Debug, Clone, PartialEq)]
pub enum TypeDefinition {
    /// Primitive types
    Null,
    Boolean,
    Integer,
    Double,
    String,
    /// Collection types
    Array(Box<TypeDefinition>),
    Object(String), // Reference to object schema
    /// Custom types
    Enum(String), // Reference to enum definition
    /// Union types
    Union(Vec<TypeDefinition>),
    /// Optional type
    Optional(Box<TypeDefinition>),
}

/// Field definition with constraints
#[derive(Debug, Clone)]
pub struct FieldDefinition {
    pub field_type: TypeDefinition,
    pub required: bool,
    pub default_value: Option<CfgppValue>,
    pub constraints: Vec<Constraint>,
}

/// Validation constraints
#[derive(Debug, Clone)]
pub enum Constraint {
    /// String length constraints
    MinLength(usize),
    MaxLength(usize),
    /// Numeric value constraints
    MinValue(f64),
    MaxValue(f64),
    /// Pattern matching
    Pattern(Regex),
    /// Custom validation function
    Custom(String), // Function name for custom validation
}

/// Validation error details
#[derive(Debug, Clone)]
pub struct ValidationError {
    pub path: String,
    pub message: String,
    pub expected_type: Option<String>,
    pub actual_type: Option<String>,
}

impl Schema {
    /// Create a new empty schema
    pub fn new() -> Self {
        Self {
            type_defs: HashMap::new(),
            enum_defs: HashMap::new(),
            object_schemas: HashMap::new(),
            root_schema: None,
        }
    }

    /// Parse schema from CFG++ schema definition string
    pub fn parse(schema_text: &str) -> CfgppResult<Self> {
        let mut schema = Self::new();
        
        // Simple parser for CFG++ schema format
        let lines: Vec<&str> = schema_text.lines().collect();
        let mut i = 0;
        
        while i < lines.len() {
            let line = lines[i].trim();
            
            // Skip empty lines and comments
            if line.is_empty() || line.starts_with("//") || line.starts_with('#') {
                i += 1;
                continue;
            }
            
            // Parse enum definitions
            if line.starts_with("enum ") {
                let (enum_def, consumed) = Self::parse_enum_definition(&lines[i..])?;
                schema.enum_defs.insert(enum_def.0, enum_def.1);
                i += consumed;
                continue;
            }
            
            // Parse object schemas
            if line.contains('{') && !line.starts_with("enum") {
                let (object_schema, consumed) = Self::parse_object_schema(&lines[i..])?;
                schema.object_schemas.insert(object_schema.0, object_schema.1);
                i += consumed;
                continue;
            }
            
            i += 1;
        }
        
        Ok(schema)
    }

    /// Parse schema from file
    pub fn parse_file(path: &str) -> CfgppResult<Self> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| CfgppError::io_error(format!("Failed to read schema file: {}", e)))?;
        Self::parse(&content)
    }

    /// Add an enum definition to the schema
    pub fn add_enum(&mut self, name: String, values: Vec<String>) {
        self.enum_defs.insert(name, values);
    }

    /// Add an object schema definition
    pub fn add_object_schema(&mut self, name: String, fields: HashMap<String, FieldDefinition>) {
        self.object_schemas.insert(name, fields);
    }

    /// Set the root schema type
    pub fn set_root_schema(&mut self, type_def: TypeDefinition) {
        self.root_schema = Some(type_def);
    }

    /// Validate a CFG++ value against this schema
    pub fn validate(&self, value: &CfgppValue) -> Result<(), Vec<ValidationError>> {
        let mut errors = Vec::new();
        
        if let Some(ref root_schema) = self.root_schema {
            self.validate_type(value, root_schema, "", &mut errors);
        } else {
            // If no root schema, try to infer validation based on value structure
            self.validate_inferred(value, "", &mut errors);
        }
        
        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }

    /// Validate a specific field
    pub fn validate_field(&self, value: &CfgppValue, field_def: &FieldDefinition, path: &str) -> Result<(), Vec<ValidationError>> {
        let mut errors = Vec::new();
        self.validate_type(value, &field_def.field_type, path, &mut errors);
        
        // Apply constraints
        for constraint in &field_def.constraints {
            self.validate_constraint(value, constraint, path, &mut errors);
        }
        
        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }

    fn validate_type(&self, value: &CfgppValue, type_def: &TypeDefinition, path: &str, errors: &mut Vec<ValidationError>) {
        match (value, type_def) {
            (CfgppValue::Null, TypeDefinition::Null) => {}
            (CfgppValue::Boolean(_), TypeDefinition::Boolean) => {}
            (CfgppValue::Integer(_), TypeDefinition::Integer) => {}
            (CfgppValue::Double(_), TypeDefinition::Double) => {}
            (CfgppValue::String(_), TypeDefinition::String) => {}
            
            (CfgppValue::Array(arr), TypeDefinition::Array(element_type)) => {
                for (i, element) in arr.iter().enumerate() {
                    let element_path = format!("{}[{}]", path, i);
                    self.validate_type(element, element_type, &element_path, errors);
                }
            }
            
            (CfgppValue::Object(obj), TypeDefinition::Object(schema_name)) => {
                if let Some(schema_fields) = self.object_schemas.get(schema_name) {
                    // Check required fields
                    for (field_name, field_def) in schema_fields {
                        let field_path = if path.is_empty() {
                            field_name.clone()
                        } else {
                            format!("{}.{}", path, field_name)
                        };
                        
                        if let Some(field_value) = obj.get(field_name) {
                            self.validate_type(field_value, &field_def.field_type, &field_path, errors);
                            
                            // Apply field constraints
                            for constraint in &field_def.constraints {
                                self.validate_constraint(field_value, constraint, &field_path, errors);
                            }
                        } else if field_def.required {
                            errors.push(ValidationError {
                                path: field_path,
                                message: format!("Required field '{}' is missing", field_name),
                                expected_type: Some(format!("{:?}", field_def.field_type)),
                                actual_type: None,
                            });
                        }
                    }
                    
                    // Check for unexpected fields
                    for field_name in obj.keys() {
                        if !schema_fields.contains_key(field_name) {
                            let field_path = if path.is_empty() {
                                field_name.clone()
                            } else {
                                format!("{}.{}", path, field_name)
                            };
                            errors.push(ValidationError {
                                path: field_path,
                                message: format!("Unexpected field '{}'", field_name),
                                expected_type: None,
                                actual_type: Some(obj.get(field_name).unwrap().type_name().to_string()),
                            });
                        }
                    }
                } else {
                    errors.push(ValidationError {
                        path: path.to_string(),
                        message: format!("Unknown object schema '{}'", schema_name),
                        expected_type: Some(format!("object({})", schema_name)),
                        actual_type: Some(value.type_name().to_string()),
                    });
                }
            }
            
            (CfgppValue::Enum(enum_value), TypeDefinition::Enum(enum_name)) => {
                if let Some(valid_values) = self.enum_defs.get(enum_name) {
                    if !valid_values.contains(enum_value) {
                        errors.push(ValidationError {
                            path: path.to_string(),
                            message: format!("Invalid enum value '{}', expected one of: {}", enum_value, valid_values.join(", ")),
                            expected_type: Some(format!("enum({})", enum_name)),
                            actual_type: Some(format!("enum({})", enum_value)),
                        });
                    }
                } else {
                    errors.push(ValidationError {
                        path: path.to_string(),
                        message: format!("Unknown enum type '{}'", enum_name),
                        expected_type: Some(format!("enum({})", enum_name)),
                        actual_type: Some(value.type_name().to_string()),
                    });
                }
            }
            
            (value, TypeDefinition::Union(types)) => {
                let mut union_errors = Vec::new();
                let mut matched = false;
                
                for union_type in types {
                    let mut type_errors = Vec::new();
                    self.validate_type(value, union_type, path, &mut type_errors);
                    if type_errors.is_empty() {
                        matched = true;
                        break;
                    }
                    union_errors.extend(type_errors);
                }
                
                if !matched {
                    errors.push(ValidationError {
                        path: path.to_string(),
                        message: format!("Value does not match any type in union: {:?}", types),
                        expected_type: Some(format!("union({:?})", types)),
                        actual_type: Some(value.type_name().to_string()),
                    });
                }
            }
            
            (value, TypeDefinition::Optional(inner_type)) => {
                if !value.is_null() {
                    self.validate_type(value, inner_type, path, errors);
                }
            }
            
            _ => {
                errors.push(ValidationError {
                    path: path.to_string(),
                    message: format!("Type mismatch"),
                    expected_type: Some(format!("{:?}", type_def)),
                    actual_type: Some(value.type_name().to_string()),
                });
            }
        }
    }

    fn validate_constraint(&self, value: &CfgppValue, constraint: &Constraint, path: &str, errors: &mut Vec<ValidationError>) {
        match constraint {
            Constraint::MinLength(min_len) => {
                if let Some(s) = value.as_string() {
                    if s.len() < *min_len {
                        errors.push(ValidationError {
                            path: path.to_string(),
                            message: format!("String length {} is less than minimum {}", s.len(), min_len),
                            expected_type: None,
                            actual_type: None,
                        });
                    }
                }
            }
            
            Constraint::MaxLength(max_len) => {
                if let Some(s) = value.as_string() {
                    if s.len() > *max_len {
                        errors.push(ValidationError {
                            path: path.to_string(),
                            message: format!("String length {} exceeds maximum {}", s.len(), max_len),
                            expected_type: None,
                            actual_type: None,
                        });
                    }
                }
            }
            
            Constraint::MinValue(min_val) => {
                let num_val = match value {
                    CfgppValue::Integer(i) => Some(*i as f64),
                    CfgppValue::Double(d) => Some(*d),
                    _ => None,
                };
                
                if let Some(val) = num_val {
                    if val < *min_val {
                        errors.push(ValidationError {
                            path: path.to_string(),
                            message: format!("Value {} is less than minimum {}", val, min_val),
                            expected_type: None,
                            actual_type: None,
                        });
                    }
                }
            }
            
            Constraint::MaxValue(max_val) => {
                let num_val = match value {
                    CfgppValue::Integer(i) => Some(*i as f64),
                    CfgppValue::Double(d) => Some(*d),
                    _ => None,
                };
                
                if let Some(val) = num_val {
                    if val > *max_val {
                        errors.push(ValidationError {
                            path: path.to_string(),
                            message: format!("Value {} exceeds maximum {}", val, max_val),
                            expected_type: None,
                            actual_type: None,
                        });
                    }
                }
            }
            
            Constraint::Pattern(regex) => {
                if let Some(s) = value.as_string() {
                    if !regex.is_match(s) {
                        errors.push(ValidationError {
                            path: path.to_string(),
                            message: format!("String '{}' does not match pattern {}", s, regex.as_str()),
                            expected_type: None,
                            actual_type: None,
                        });
                    }
                }
            }
            
            Constraint::Custom(_function_name) => {
                // Custom validation would be implemented by the user
                // For now, we just skip it
            }
        }
    }

    fn validate_inferred(&self, value: &CfgppValue, path: &str, errors: &mut Vec<ValidationError>) {
        // Basic validation without explicit schema
        match value {
            CfgppValue::Object(obj) => {
                for (key, val) in obj {
                    let field_path = if path.is_empty() {
                        key.clone()
                    } else {
                        format!("{}.{}", path, key)
                    };
                    self.validate_inferred(val, &field_path, errors);
                }
            }
            CfgppValue::Array(arr) => {
                for (i, element) in arr.iter().enumerate() {
                    let element_path = format!("{}[{}]", path, i);
                    self.validate_inferred(element, &element_path, errors);
                }
            }
            _ => {
                // Basic value types are always valid
            }
        }
    }

    fn parse_enum_definition(lines: &[&str]) -> CfgppResult<((String, Vec<String>), usize)> {
        let first_line = lines[0].trim();
        
        // Parse "enum Name { value1, value2, value3 }"
        if let Some(name_start) = first_line.find("enum ") {
            let after_enum = &first_line[name_start + 5..];
            if let Some(brace_start) = after_enum.find('{') {
                let enum_name = after_enum[..brace_start].trim().to_string();
                
                // Handle single-line enum
                if let Some(brace_end) = after_enum.find('}') {
                    let values_str = &after_enum[brace_start + 1..brace_end];
                    let values: Vec<String> = values_str
                        .split(',')
                        .map(|s| s.trim().to_string())
                        .filter(|s| !s.is_empty())
                        .collect();
                    return Ok(((enum_name, values), 1));
                }
                
                // Handle multi-line enum
                let mut values = Vec::new();
                let mut line_count = 1;
                
                for line in &lines[1..] {
                    let trimmed = line.trim();
                    if trimmed.contains('}') {
                        break;
                    }
                    
                    if !trimmed.is_empty() && !trimmed.starts_with("//") {
                        let line_values: Vec<String> = trimmed
                            .split(',')
                            .map(|s| s.trim().to_string())
                            .filter(|s| !s.is_empty())
                            .collect();
                        values.extend(line_values);
                    }
                    line_count += 1;
                }
                
                return Ok(((enum_name, values), line_count + 1));
            }
        }
        
        Err(CfgppError::parse_error("Invalid enum definition"))
    }

    fn parse_object_schema(lines: &[&str]) -> CfgppResult<((String, HashMap<String, FieldDefinition>), usize)> {
        let first_line = lines[0].trim();
        
        // Parse "ObjectName {" or just "{"
        let object_name = if let Some(brace_pos) = first_line.find('{') {
            first_line[..brace_pos].trim().to_string()
        } else {
            "unnamed".to_string()
        };
        
        let mut fields = HashMap::new();
        let mut line_count = 1;
        
        for line in &lines[1..] {
            let trimmed = line.trim();
            
            if trimmed.contains('}') {
                break;
            }
            
            if trimmed.is_empty() || trimmed.starts_with("//") {
                line_count += 1;
                continue;
            }
            
            // Parse field definition: "field_name: type_name;"
            if let Some(colon_pos) = trimmed.find(':') {
                let field_name = trimmed[..colon_pos].trim().to_string();
                let type_part = trimmed[colon_pos + 1..].trim().trim_end_matches(';');
                
                let field_type = Self::parse_type_definition(type_part)?;
                let field_def = FieldDefinition {
                    field_type,
                    required: true, // Default to required
                    default_value: None,
                    constraints: Vec::new(),
                };
                
                fields.insert(field_name, field_def);
            }
            
            line_count += 1;
        }
        
        Ok(((object_name, fields), line_count + 1))
    }

    fn parse_type_definition(type_str: &str) -> CfgppResult<TypeDefinition> {
        let trimmed = type_str.trim();
        
        match trimmed {
            "null" => Ok(TypeDefinition::Null),
            "boolean" => Ok(TypeDefinition::Boolean),
            "integer" => Ok(TypeDefinition::Integer),
            "double" => Ok(TypeDefinition::Double),
            "string" => Ok(TypeDefinition::String),
            _ => {
                // Handle array types like "array<string>"
                if trimmed.starts_with("array<") && trimmed.ends_with('>') {
                    let inner_type = &trimmed[6..trimmed.len() - 1];
                    let element_type = Self::parse_type_definition(inner_type)?;
                    return Ok(TypeDefinition::Array(Box::new(element_type)));
                }
                
                // Handle optional types like "optional<string>"
                if trimmed.starts_with("optional<") && trimmed.ends_with('>') {
                    let inner_type = &trimmed[9..trimmed.len() - 1];
                    let element_type = Self::parse_type_definition(inner_type)?;
                    return Ok(TypeDefinition::Optional(Box::new(element_type)));
                }
                
                // Assume it's a custom type (object or enum)
                Ok(TypeDefinition::Object(trimmed.to_string()))
            }
        }
    }
}

impl Default for Schema {
    fn default() -> Self {
        Self::new()
    }
}

impl FieldDefinition {
    /// Create a new field definition
    pub fn new(field_type: TypeDefinition, required: bool) -> Self {
        Self {
            field_type,
            required,
            default_value: None,
            constraints: Vec::new(),
        }
    }
    
    /// Add a constraint to this field
    pub fn with_constraint(mut self, constraint: Constraint) -> Self {
        self.constraints.push(constraint);
        self
    }
    
    /// Set the default value for this field
    pub fn with_default(mut self, default: CfgppValue) -> Self {
        self.default_value = Some(default);
        self
    }
}

impl std::fmt::Display for ValidationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Validation error at '{}': {}", self.path, self.message)
    }
}

impl std::error::Error for ValidationError {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_schema_validation() {
        let mut schema = Schema::new();
        
        // Add enum definition
        schema.add_enum("Status".to_string(), vec!["active".to_string(), "inactive".to_string()]);
        
        // Add object schema
        let mut fields = HashMap::new();
        fields.insert("name".to_string(), FieldDefinition::new(TypeDefinition::String, true));
        fields.insert("status".to_string(), FieldDefinition::new(TypeDefinition::Enum("Status".to_string()), true));
        schema.add_object_schema("User".to_string(), fields);
        
        // Create test value
        let mut user_obj = HashMap::new();
        user_obj.insert("name".to_string(), CfgppValue::string("John"));
        user_obj.insert("status".to_string(), CfgppValue::enum_value("active"));
        let user_value = CfgppValue::object_with_values(user_obj);
        
        // Validate - this should pass
        schema.set_root_schema(TypeDefinition::Object("User".to_string()));
        let result = schema.validate(&user_value);
        assert!(result.is_ok());
    }

    #[test]
    fn test_schema_parsing() {
        let schema_text = r#"
        enum Status {
            active, inactive, pending
        }
        
        User {
            name: string;
            age: integer;
            status: Status;
        }
        "#;
        
        let schema = Schema::parse(schema_text).unwrap();
        
        assert!(schema.enum_defs.contains_key("Status"));
        assert!(schema.object_schemas.contains_key("User"));
        
        let status_values = &schema.enum_defs["Status"];
        assert_eq!(status_values.len(), 3);
        assert!(status_values.contains(&"active".to_string()));
    }

    #[test]
    fn test_validation_errors() {
        let mut schema = Schema::new();
        
        let mut fields = HashMap::new();
        fields.insert("required_field".to_string(), FieldDefinition::new(TypeDefinition::String, true));
        schema.add_object_schema("Test".to_string(), fields);
        schema.set_root_schema(TypeDefinition::Object("Test".to_string()));
        
        // Missing required field
        let empty_obj = CfgppValue::object();
        let result = schema.validate(&empty_obj);
        
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(!errors.is_empty());
        assert!(errors[0].message.contains("Required field"));
    }
}
