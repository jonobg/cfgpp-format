//! Abstract Syntax Tree definitions for CFG++ format

use crate::value::CfgppValue;
use std::collections::HashMap;

/// AST node types for CFG++ format
#[derive(Debug, Clone, PartialEq)]
pub enum AstNode {
    /// Root configuration object
    Root {
        objects: Vec<AstNode>,
    },
    
    /// Named object definition
    Object {
        name: Option<String>,
        fields: HashMap<String, AstNode>,
    },
    
    /// Array literal
    Array {
        elements: Vec<AstNode>,
    },
    
    /// Enum definition
    EnumDef {
        name: String,
        values: Vec<String>,
    },
    
    /// Include directive
    Include {
        path: String,
    },
    
    /// Environment variable reference
    EnvVar {
        name: String,
        default: Option<String>,
    },
    
    /// Field assignment
    Assignment {
        key: String,
        value: Box<AstNode>,
    },
    
    /// Literal values
    Literal {
        value: CfgppValue,
    },
    
    /// Expression with operators
    Expression {
        operator: BinaryOperator,
        left: Box<AstNode>,
        right: Box<AstNode>,
    },
    
    /// Namespace reference
    Namespace {
        parts: Vec<String>,
    },
}

/// Binary operators supported in CFG++
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BinaryOperator {
    Add,
    Subtract,
    Multiply,
    Divide,
}

impl AstNode {
    /// Create a new root node
    pub fn root(objects: Vec<AstNode>) -> Self {
        Self::Root { objects }
    }
    
    /// Create a new object node
    pub fn object(name: Option<String>, fields: HashMap<String, AstNode>) -> Self {
        Self::Object { name, fields }
    }
    
    /// Create a new array node
    pub fn array(elements: Vec<AstNode>) -> Self {
        Self::Array { elements }
    }
    
    /// Create a new literal node
    pub fn literal(value: CfgppValue) -> Self {
        Self::Literal { value }
    }
    
    /// Create a new assignment node
    pub fn assignment(key: String, value: AstNode) -> Self {
        Self::Assignment {
            key,
            value: Box::new(value),
        }
    }
    
    /// Create a new include node
    pub fn include(path: String) -> Self {
        Self::Include { path }
    }
    
    /// Create a new environment variable node
    pub fn env_var(name: String, default: Option<String>) -> Self {
        Self::EnvVar { name, default }
    }
    
    /// Create a new enum definition node
    pub fn enum_def(name: String, values: Vec<String>) -> Self {
        Self::EnumDef { name, values }
    }
    
    /// Create a new expression node
    pub fn expression(operator: BinaryOperator, left: AstNode, right: AstNode) -> Self {
        Self::Expression {
            operator,
            left: Box::new(left),
            right: Box::new(right),
        }
    }
    
    /// Create a new namespace node
    pub fn namespace(parts: Vec<String>) -> Self {
        Self::Namespace { parts }
    }
    
    /// Get the type name of this AST node
    pub fn type_name(&self) -> &'static str {
        match self {
            Self::Root { .. } => "root",
            Self::Object { .. } => "object",
            Self::Array { .. } => "array",
            Self::EnumDef { .. } => "enum_def",
            Self::Include { .. } => "include",
            Self::EnvVar { .. } => "env_var",
            Self::Assignment { .. } => "assignment",
            Self::Literal { .. } => "literal",
            Self::Expression { .. } => "expression",
            Self::Namespace { .. } => "namespace",
        }
    }
    
    /// Check if this is a literal node
    pub fn is_literal(&self) -> bool {
        matches!(self, Self::Literal { .. })
    }
    
    /// Check if this is an object node
    pub fn is_object(&self) -> bool {
        matches!(self, Self::Object { .. })
    }
    
    /// Check if this is an array node
    pub fn is_array(&self) -> bool {
        matches!(self, Self::Array { .. })
    }
    
    /// Check if this is an assignment node
    pub fn is_assignment(&self) -> bool {
        matches!(self, Self::Assignment { .. })
    }
    
    /// Get the literal value if this is a literal node
    pub fn as_literal(&self) -> Option<&CfgppValue> {
        match self {
            Self::Literal { value } => Some(value),
            _ => None,
        }
    }
    
    /// Get the object fields if this is an object node
    pub fn as_object(&self) -> Option<&HashMap<String, AstNode>> {
        match self {
            Self::Object { fields, .. } => Some(fields),
            _ => None,
        }
    }
    
    /// Get the array elements if this is an array node
    pub fn as_array(&self) -> Option<&Vec<AstNode>> {
        match self {
            Self::Array { elements } => Some(elements),
            _ => None,
        }
    }
    
    /// Convert this AST node to a CFG++ value
    pub fn to_value(&self) -> crate::error::CfgppResult<CfgppValue> {
        match self {
            Self::Literal { value } => Ok(value.clone()),
            
            Self::Object { fields, .. } => {
                let mut object = HashMap::new();
                for (key, node) in fields {
                    object.insert(key.clone(), node.to_value()?);
                }
                Ok(CfgppValue::object_with_values(object))
            }
            
            Self::Array { elements } => {
                let mut array = Vec::new();
                for element in elements {
                    array.push(element.to_value()?);
                }
                Ok(CfgppValue::array_with_values(array))
            }
            
            Self::Assignment { value, .. } => value.to_value(),
            
            Self::Root { objects } => {
                let mut root_object = HashMap::new();
                for obj in objects {
                    if let Self::Object { name: Some(name), fields } = obj {
                        let mut object = HashMap::new();
                        for (key, node) in fields {
                            object.insert(key.clone(), node.to_value()?);
                        }
                        root_object.insert(name.clone(), CfgppValue::object_with_values(object));
                    } else if let Self::Assignment { key, value } = obj {
                        root_object.insert(key.clone(), value.to_value()?);
                    }
                }
                Ok(CfgppValue::object_with_values(root_object))
            }
            
            _ => Err(crate::error::CfgppError::parse_error(
                format!("Cannot convert {} to value", self.type_name())
            )),
        }
    }
    
    /// Pretty print this AST node for debugging
    pub fn pretty_print(&self, indent: usize) -> String {
        let spacing = "  ".repeat(indent);
        
        match self {
            Self::Root { objects } => {
                let mut result = format!("{}Root {{\n", spacing);
                for obj in objects {
                    result.push_str(&obj.pretty_print(indent + 1));
                }
                result.push_str(&format!("{}}}\n", spacing));
                result
            }
            
            Self::Object { name, fields } => {
                let mut result = if let Some(name) = name {
                    format!("{}Object {} {{\n", spacing, name)
                } else {
                    format!("{}Object {{\n", spacing)
                };
                
                for (key, node) in fields {
                    result.push_str(&format!("{}  {}: ", spacing, key));
                    if node.is_literal() {
                        result.push_str(&format!("{}\n", node.as_literal().unwrap()));
                    } else {
                        result.push('\n');
                        result.push_str(&node.pretty_print(indent + 2));
                    }
                }
                result.push_str(&format!("{}}}\n", spacing));
                result
            }
            
            Self::Array { elements } => {
                let mut result = format!("{}Array [\n", spacing);
                for element in elements {
                    result.push_str(&element.pretty_print(indent + 1));
                }
                result.push_str(&format!("{}]\n", spacing));
                result
            }
            
            Self::Literal { value } => {
                format!("{}Literal({})\n", spacing, value)
            }
            
            Self::Assignment { key, value } => {
                let mut result = format!("{}Assignment {} = ", spacing, key);
                if value.is_literal() {
                    result.push_str(&format!("{}\n", value.as_literal().unwrap()));
                } else {
                    result.push('\n');
                    result.push_str(&value.pretty_print(indent + 1));
                }
                result
            }
            
            Self::Include { path } => {
                format!("{}Include \"{}\"\n", spacing, path)
            }
            
            Self::EnvVar { name, default } => {
                if let Some(default) = default {
                    format!("{}EnvVar ${{{}:-{}}}\n", spacing, name, default)
                } else {
                    format!("{}EnvVar ${{{}}}\n", spacing, name)
                }
            }
            
            Self::EnumDef { name, values } => {
                format!("{}EnumDef {} {{ {} }}\n", spacing, name, values.join(", "))
            }
            
            Self::Expression { operator, left, right } => {
                let op_str = match operator {
                    BinaryOperator::Add => "+",
                    BinaryOperator::Subtract => "-",
                    BinaryOperator::Multiply => "*",
                    BinaryOperator::Divide => "/",
                };
                
                let mut result = format!("{}Expression {} {{\n", spacing, op_str);
                result.push_str(&left.pretty_print(indent + 1));
                result.push_str(&right.pretty_print(indent + 1));
                result.push_str(&format!("{}}}\n", spacing));
                result
            }
            
            Self::Namespace { parts } => {
                format!("{}Namespace {}\n", spacing, parts.join("::"))
            }
        }
    }
}

impl std::fmt::Display for AstNode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.pretty_print(0))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ast_construction() {
        let mut fields = HashMap::new();
        fields.insert("host".to_string(), AstNode::literal(CfgppValue::string("localhost")));
        fields.insert("port".to_string(), AstNode::literal(CfgppValue::integer(5432)));
        
        let obj = AstNode::object(Some("database".to_string()), fields);
        let root = AstNode::root(vec![obj]);
        
        assert!(root.type_name() == "root");
        
        let value = root.to_value().unwrap();
        assert!(value.is_object());
        assert_eq!(value.get_path("database.host").unwrap().as_string(), Some("localhost"));
    }
    
    #[test]
    fn test_pretty_print() {
        let literal = AstNode::literal(CfgppValue::string("test"));
        let output = literal.pretty_print(0);
        assert!(output.contains("Literal"));
        assert!(output.contains("test"));
    }
}
