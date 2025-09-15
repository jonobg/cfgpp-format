//! High-performance recursive descent parser for CFG++ format

use crate::{
    error::{CfgppError, CfgppResult},
    lexer::{Lexer, Token, TokenType},
    value::CfgppValue,
};
use std::collections::HashMap;
use std::path::Path;

/// Parser configuration options
#[derive(Debug, Clone)]
pub struct ParserOptions {
    /// Enable environment variable expansion
    pub expand_env_vars: bool,
    /// Enable include directive processing
    pub process_includes: bool,
    /// Maximum include depth to prevent infinite recursion
    pub max_include_depth: usize,
    /// Include search paths
    pub include_paths: Vec<String>,
    /// Validate syntax only (don't build value tree)
    pub syntax_only: bool,
}

impl Default for ParserOptions {
    fn default() -> Self {
        Self {
            expand_env_vars: true,
            process_includes: true,
            max_include_depth: 10,
            include_paths: vec![".".to_string()],
            syntax_only: false,
        }
    }
}

/// High-performance CFG++ parser
pub struct Parser {
    options: ParserOptions,
    tokens: Vec<Token>,
    current: usize,
    include_depth: usize,
}

impl Parser {
    /// Create a new parser with default options
    pub fn new() -> Self {
        Self::with_options(ParserOptions::default())
    }

    /// Create a new parser with custom options
    pub fn with_options(options: ParserOptions) -> Self {
        Self {
            options,
            tokens: Vec::new(),
            current: 0,
            include_depth: 0,
        }
    }

    /// Parse a CFG++ string into a value
    pub fn parse(&mut self, input: &str) -> CfgppResult<CfgppValue> {
        // Tokenize input
        let mut lexer = Lexer::new(input);
        self.tokens = lexer.tokenize()?;
        self.current = 0;

        // Parse the token stream
        self.parse_value()
    }

    /// Parse a CFG++ file into a value
    pub fn parse_file<P: AsRef<Path>>(&mut self, path: P) -> CfgppResult<CfgppValue> {
        let content = std::fs::read_to_string(path.as_ref())
            .map_err(|e| CfgppError::io_error(format!("Failed to read file: {}", e)))?;
        
        self.parse(&content)
    }

    /// Parse multiple files and merge them into a single object
    pub fn parse_files<P: AsRef<Path>>(&mut self, paths: &[P]) -> CfgppResult<CfgppValue> {
        let mut result = CfgppValue::object();
        
        for path in paths {
            let file_content = self.parse_file(path)?;
            if let CfgppValue::Object(obj) = file_content {
                if let CfgppValue::Object(ref mut result_obj) = result {
                    result_obj.extend(obj);
                }
            }
        }
        
        Ok(result)
    }

    /// Validate syntax without building the value tree
    pub fn validate_syntax(&mut self, input: &str) -> CfgppResult<()> {
        let old_syntax_only = self.options.syntax_only;
        self.options.syntax_only = true;
        
        let result = self.parse(input);
        self.options.syntax_only = old_syntax_only;
        
        result.map(|_| ())
    }

    fn parse_value(&mut self) -> CfgppResult<CfgppValue> {
        match self.current_token()?.token_type {
            TokenType::String => self.parse_string(),
            TokenType::Integer => self.parse_integer(),
            TokenType::Double => self.parse_double(),
            TokenType::Boolean => self.parse_boolean(),
            TokenType::Null => self.parse_null(),
            TokenType::LeftBrace => self.parse_object(),
            TokenType::LeftBracket => self.parse_array(),
            TokenType::Identifier => self.parse_identifier_or_object(),
            TokenType::Include | TokenType::Import => self.parse_include(),
            TokenType::EnvVar => self.parse_env_var(),
            _ => Err(CfgppError::syntax_error(
                format!("Unexpected token: {}", self.current_token()?.value),
                self.current_token()?.line,
                self.current_token()?.column,
            )),
        }
    }

    fn parse_string(&mut self) -> CfgppResult<CfgppValue> {
        let token = self.advance()?;
        Ok(CfgppValue::string(token.value.clone()))
    }

    fn parse_integer(&mut self) -> CfgppResult<CfgppValue> {
        let token = self.advance()?;
        let value = token.value.parse::<i64>()
            .map_err(|_| CfgppError::syntax_error(
                format!("Invalid integer: {}", token.value),
                token.line,
                token.column,
            ))?;
        Ok(CfgppValue::integer(value))
    }

    fn parse_double(&mut self) -> CfgppResult<CfgppValue> {
        let token = self.advance()?;
        let value = token.value.parse::<f64>()
            .map_err(|_| CfgppError::syntax_error(
                format!("Invalid double: {}", token.value),
                token.line,
                token.column,
            ))?;
        Ok(CfgppValue::double(value))
    }

    fn parse_boolean(&mut self) -> CfgppResult<CfgppValue> {
        let token = self.advance()?;
        let value = match token.value.as_str() {
            "true" => true,
            "false" => false,
            _ => return Err(CfgppError::syntax_error(
                format!("Invalid boolean: {}", token.value),
                token.line,
                token.column,
            )),
        };
        Ok(CfgppValue::boolean(value))
    }

    fn parse_null(&mut self) -> CfgppResult<CfgppValue> {
        self.advance()?;
        Ok(CfgppValue::null())
    }

    fn parse_object(&mut self) -> CfgppResult<CfgppValue> {
        self.expect(TokenType::LeftBrace)?;
        let mut object = HashMap::new();

        while !self.check(TokenType::RightBrace) && !self.is_at_end() {
            // Parse key
            let key_token = self.expect_identifier()?;
            let key = key_token.value.clone();

            // Expect equals
            self.expect(TokenType::Equals)?;

            // Parse value
            let value = self.parse_value()?;

            if !self.options.syntax_only {
                object.insert(key, value);
            }

            // Optional semicolon
            if self.check(TokenType::Semicolon) {
                self.advance()?;
            }
        }

        self.expect(TokenType::RightBrace)?;

        if self.options.syntax_only {
            Ok(CfgppValue::null())
        } else {
            Ok(CfgppValue::object_with_values(object))
        }
    }

    fn parse_array(&mut self) -> CfgppResult<CfgppValue> {
        self.expect(TokenType::LeftBracket)?;
        let mut array = Vec::new();

        while !self.check(TokenType::RightBracket) && !self.is_at_end() {
            let value = self.parse_value()?;
            
            if !self.options.syntax_only {
                array.push(value);
            }

            // Optional comma
            if self.check(TokenType::Comma) {
                self.advance()?;
            }
        }

        self.expect(TokenType::RightBracket)?;

        if self.options.syntax_only {
            Ok(CfgppValue::null())
        } else {
            Ok(CfgppValue::array_with_values(array))
        }
    }

    fn parse_identifier_or_object(&mut self) -> CfgppResult<CfgppValue> {
        let identifier_value = {
            let identifier_token = self.advance()?;
            identifier_token.value.clone()
        };
        
        // Check if this is an object definition (identifier followed by {)
        if self.check(TokenType::LeftBrace) {
            // Parse as named object
            let mut object = HashMap::new();
            self.expect(TokenType::LeftBrace)?;

            while !self.check(TokenType::RightBrace) && !self.is_at_end() {
                let key_token = self.expect_identifier()?;
                let key = key_token.value.clone();

                self.expect(TokenType::Equals)?;
                let value = self.parse_value()?;

                if !self.options.syntax_only {
                    object.insert(key, value);
                }

                if self.check(TokenType::Semicolon) {
                    self.advance()?;
                }
            }

            self.expect(TokenType::RightBrace)?;

            if self.options.syntax_only {
                Ok(CfgppValue::null())
            } else {
                Ok(CfgppValue::object_with_values(object))
            }
        } else {
            // Treat as enum value
            Ok(CfgppValue::enum_value(identifier_value))
        }
    }

    fn parse_include(&mut self) -> CfgppResult<CfgppValue> {
        let (include_line, include_column, process_includes) = {
            let include_token = self.advance()?;
            (include_token.line, include_token.column, self.options.process_includes)
        };
        
        if !process_includes {
            return Err(CfgppError::syntax_error(
                "Include directives are disabled",
                include_line,
                include_column,
            ));
        }

        if self.include_depth >= self.options.max_include_depth {
            return Err(CfgppError::include_error(
                "unknown",
                format!("Maximum include depth ({}) exceeded", self.options.max_include_depth),
            ));
        }

        let (include_path, include_paths) = {
            let path_token = self.expect(TokenType::String)?;
            (path_token.value.clone(), self.options.include_paths.clone())
        };

        // Find the file in include paths
        let mut full_path = None;
        for search_path in &include_paths {
            let candidate = Path::new(search_path).join(&include_path);
            if candidate.exists() {
                full_path = Some(candidate);
                break;
            }
        }

        let file_path = full_path.ok_or_else(|| {
            CfgppError::include_error(include_path, "File not found in include paths")
        })?;

        // Parse included file
        self.include_depth += 1;
        let result = self.parse_file(&file_path);
        self.include_depth -= 1;

        result
    }

    fn parse_env_var(&mut self) -> CfgppResult<CfgppValue> {
        let (env_value, expand_env_vars) = {
            let env_token = self.advance()?;
            (env_token.value.clone(), self.options.expand_env_vars)
        };
        
        if !expand_env_vars {
            return Ok(CfgppValue::string(env_value));
        }

        // Parse environment variable syntax: ${VAR} or ${VAR:-default}
        let env_content = &env_value[2..env_value.len()-1]; // Remove ${ and }
        
        let (var_name, default_value) = if let Some(colon_pos) = env_content.find(":-") {
            (&env_content[..colon_pos], Some(&env_content[colon_pos + 2..]))
        } else {
            (env_content, None)
        };

        match std::env::var(var_name) {
            Ok(value) => Ok(CfgppValue::string(value)),
            Err(_) => {
                if let Some(default) = default_value {
                    Ok(CfgppValue::string(default.to_string()))
                } else {
                    Err(CfgppError::env_var_error(var_name, "Environment variable not found"))
                }
            }
        }
    }

    // Utility methods
    fn current_token(&self) -> CfgppResult<&Token> {
        self.tokens.get(self.current)
            .ok_or_else(|| CfgppError::parse_error("Unexpected end of input"))
    }

    fn advance(&mut self) -> CfgppResult<&Token> {
        if !self.is_at_end() {
            self.current += 1;
        }
        self.previous()
    }

    fn previous(&self) -> CfgppResult<&Token> {
        self.tokens.get(self.current - 1)
            .ok_or_else(|| CfgppError::parse_error("No previous token"))
    }

    fn check(&self, token_type: TokenType) -> bool {
        if self.is_at_end() {
            false
        } else {
            self.current_token().map(|t| t.token_type == token_type).unwrap_or(false)
        }
    }

    fn is_at_end(&self) -> bool {
        self.current >= self.tokens.len() || 
        self.current_token().map(|t| t.token_type == TokenType::Eof).unwrap_or(true)
    }

    fn expect(&mut self, expected: TokenType) -> CfgppResult<&Token> {
        if self.check(expected) {
            self.advance()
        } else {
            let current = self.current_token()?;
            Err(CfgppError::syntax_error(
                format!("Expected {:?}, found {:?}", expected, current.token_type),
                current.line,
                current.column,
            ))
        }
    }

    fn expect_identifier(&mut self) -> CfgppResult<&Token> {
        self.expect(TokenType::Identifier)
    }
}

impl Default for Parser {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_parsing() {
        let input = r#"
        database {
            host = "localhost";
            port = 5432;
            ssl = true;
        }
        "#;

        let mut parser = Parser::new();
        let result = parser.parse(input).unwrap();

        assert!(result.is_object());
        let db = result.get("database").unwrap();
        assert_eq!(db.get("host").unwrap().as_string(), Some("localhost"));
        assert_eq!(db.get("port").unwrap().as_integer(), Some(5432));
        assert_eq!(db.get("ssl").unwrap().as_boolean(), Some(true));
    }

    #[test]
    fn test_array_parsing() {
        let input = r#"
        servers = ["web1", "web2", "web3"];
        ports = [80, 443, 8080];
        "#;

        let mut parser = Parser::new();
        let result = parser.parse(input).unwrap();

        let servers = result.get("servers").unwrap().as_array().unwrap();
        assert_eq!(servers.len(), 3);
        assert_eq!(servers[0].as_string(), Some("web1"));
    }

    #[test]
    fn test_nested_objects() {
        let input = r#"
        app {
            database {
                host = "localhost";
                credentials {
                    username = "admin";
                    password = "secret";
                }
            }
        }
        "#;

        let mut parser = Parser::new();
        let result = parser.parse(input).unwrap();

        let username = result.get_path("app.database.credentials.username");
        assert_eq!(username.unwrap().as_string(), Some("admin"));
    }

    #[test]
    fn test_env_var_expansion() {
        std::env::set_var("TEST_VAR", "test_value");
        
        let input = r#"
        config {
            value = ${TEST_VAR};
            default_value = ${MISSING_VAR:-default};
        }
        "#;

        let mut parser = Parser::new();
        let result = parser.parse(input).unwrap();

        assert_eq!(result.get_path("config.value").unwrap().as_string(), Some("test_value"));
        assert_eq!(result.get_path("config.default_value").unwrap().as_string(), Some("default"));
    }

    #[test]
    fn test_syntax_validation() {
        let input = r#"
        invalid {
            missing_value = ;
        }
        "#;

        let mut parser = Parser::new();
        let result = parser.validate_syntax(input);
        
        assert!(result.is_err());
    }
}
