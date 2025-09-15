//! High-performance lexer for CFG++ format

use crate::error::{CfgppError, CfgppResult};
use std::fmt;
use std::str::Chars;
use std::iter::Peekable;

/// Token types in CFG++ format
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TokenType {
    // Literals
    String,
    Integer,
    Double,
    Boolean,
    Null,
    Identifier,
    
    // Keywords
    Enum,
    Include,
    Import,
    
    // Punctuation
    LeftBrace,
    RightBrace,
    LeftBracket,
    RightBracket,
    LeftParen,
    RightParen,
    Equals,
    Semicolon,
    Comma,
    Dot,
    Colon,
    
    // Operators
    Plus,
    Minus,
    Multiply,
    Divide,
    
    // Special
    EnvVar,
    Namespace,
    Comment,
    Whitespace,
    Newline,
    Eof,
}

/// A token with its value and position
#[derive(Debug, Clone, PartialEq)]
pub struct Token {
    pub token_type: TokenType,
    pub value: String,
    pub line: usize,
    pub column: usize,
    pub position: usize,
}

impl Token {
    pub fn new(
        token_type: TokenType,
        value: String,
        line: usize,
        column: usize,
        position: usize,
    ) -> Self {
        Self {
            token_type,
            value,
            line,
            column,
            position,
        }
    }
}

impl fmt::Display for Token {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{:?}({}) at {}:{}",
            self.token_type, self.value, self.line, self.column
        )
    }
}

/// High-performance lexer with SIMD optimizations where possible
pub struct Lexer<'a> {
    input: &'a str,
    chars: Peekable<Chars<'a>>,
    position: usize,
    line: usize,
    column: usize,
    tokens: Vec<Token>,
}

impl<'a> Lexer<'a> {
    /// Create a new lexer for the given input
    pub fn new(input: &'a str) -> Self {
        Self {
            input,
            chars: input.chars().peekable(),
            position: 0,
            line: 1,
            column: 1,
            tokens: Vec::with_capacity(input.len() / 10), // Estimate token count
        }
    }

    /// Tokenize the entire input
    pub fn tokenize(&mut self) -> CfgppResult<Vec<Token>> {
        while self.peek().is_some() {
            match self.next_token() {
                Ok(Some(token)) => {
                    // Skip whitespace and comments for now
                    if !matches!(token.token_type, TokenType::Whitespace | TokenType::Comment) {
                        self.tokens.push(token);
                    }
                }
                Ok(None) => break,
                Err(e) => return Err(e),
            }
        }

        // Add EOF token
        self.tokens.push(Token::new(
            TokenType::Eof,
            String::new(),
            self.line,
            self.column,
            self.position,
        ));

        Ok(std::mem::take(&mut self.tokens))
    }

    fn next_token(&mut self) -> CfgppResult<Option<Token>> {
        self.skip_whitespace();

        let start_line = self.line;
        let start_column = self.column;
        let start_position = self.position;

        let ch = match self.advance() {
            Some(ch) => ch,
            None => return Ok(None),
        };

        let token_type = match ch {
            // Single-character tokens
            '{' => TokenType::LeftBrace,
            '}' => TokenType::RightBrace,
            '[' => TokenType::LeftBracket,
            ']' => TokenType::RightBracket,
            '(' => TokenType::LeftParen,
            ')' => TokenType::RightParen,
            '=' => TokenType::Equals,
            ';' => TokenType::Semicolon,
            ',' => TokenType::Comma,
            '.' => TokenType::Dot,
            '+' => TokenType::Plus,
            '-' => TokenType::Minus,
            '*' => TokenType::Multiply,
            '/' => {
                // Check for comments
                if self.peek() == Some(&'/') {
                    self.advance(); // consume second '/'
                    return Ok(Some(self.read_line_comment(start_line, start_column, start_position)));
                }
                TokenType::Divide
            }
            ':' => {
                // Check for namespace operator '::'
                if self.peek() == Some(&':') {
                    self.advance(); // consume second ':'
                    return Ok(Some(Token::new(
                        TokenType::Namespace,
                        "::".to_string(),
                        start_line,
                        start_column,
                        start_position,
                    )));
                }
                TokenType::Colon
            }

            // String literals
            '"' => return Ok(Some(self.read_string(start_line, start_column, start_position)?)),

            // Environment variables
            '$' => {
                if self.peek() == Some(&'{') {
                    return Ok(Some(self.read_env_var(start_line, start_column, start_position)?));
                }
                return Err(CfgppError::syntax_error(
                    "Unexpected character '$'",
                    start_line,
                    start_column,
                ));
            }

            // Include/import directives
            '@' => return Ok(Some(self.read_directive(start_line, start_column, start_position)?)),

            // Numbers
            '0'..='9' => {
                return Ok(Some(self.read_number(ch, start_line, start_column, start_position)?));
            }

            // Identifiers and keywords
            'a'..='z' | 'A'..='Z' | '_' => {
                return Ok(Some(self.read_identifier(ch, start_line, start_column, start_position)?));
            }

            _ => {
                return Err(CfgppError::syntax_error(
                    format!("Unexpected character '{}'", ch),
                    start_line,
                    start_column,
                ));
            }
        };

        Ok(Some(Token::new(
            token_type,
            ch.to_string(),
            start_line,
            start_column,
            start_position,
        )))
    }

    fn read_string(&mut self, line: usize, column: usize, position: usize) -> CfgppResult<Token> {
        let mut value = String::new();
        let mut escaped = false;

        while let Some(&ch) = self.peek() {
            self.advance();

            if escaped {
                match ch {
                    'n' => value.push('\n'),
                    'r' => value.push('\r'),
                    't' => value.push('\t'),
                    '\\' => value.push('\\'),
                    '"' => value.push('"'),
                    _ => {
                        value.push('\\');
                        value.push(ch);
                    }
                }
                escaped = false;
            } else if ch == '\\' {
                escaped = true;
            } else if ch == '"' {
                return Ok(Token::new(TokenType::String, value, line, column, position));
            } else {
                value.push(ch);
            }
        }

        Err(CfgppError::syntax_error("Unterminated string", line, column))
    }

    fn read_env_var(&mut self, line: usize, column: usize, position: usize) -> CfgppResult<Token> {
        self.advance(); // consume '{'
        let mut value = String::from("${");
        let mut brace_count = 1;

        while let Some(&ch) = self.peek() {
            self.advance();
            value.push(ch);

            match ch {
                '{' => brace_count += 1,
                '}' => {
                    brace_count -= 1;
                    if brace_count == 0 {
                        return Ok(Token::new(TokenType::EnvVar, value, line, column, position));
                    }
                }
                _ => {}
            }
        }

        Err(CfgppError::syntax_error("Unterminated environment variable", line, column))
    }

    fn read_directive(&mut self, line: usize, column: usize, position: usize) -> CfgppResult<Token> {
        let mut value = String::from("@");

        while let Some(&ch) = self.peek() {
            if ch.is_alphanumeric() || ch == '_' {
                self.advance();
                value.push(ch);
            } else {
                break;
            }
        }

        let token_type = match value.as_str() {
            "@include" => TokenType::Include,
            "@import" => TokenType::Import,
            _ => return Err(CfgppError::syntax_error(format!("Unknown directive '{}'", value), line, column)),
        };

        Ok(Token::new(token_type, value, line, column, position))
    }

    fn read_number(&mut self, first: char, line: usize, column: usize, position: usize) -> CfgppResult<Token> {
        let mut value = String::new();
        value.push(first);
        let mut is_float = false;

        while let Some(&ch) = self.peek() {
            match ch {
                '0'..='9' => {
                    self.advance();
                    value.push(ch);
                }
                '.' => {
                    if is_float {
                        break; // Second dot, stop parsing
                    }
                    is_float = true;
                    self.advance();
                    value.push(ch);
                }
                'e' | 'E' => {
                    is_float = true;
                    self.advance();
                    value.push(ch);
                    
                    // Handle optional sign
                    if let Some(&sign_ch) = self.peek() {
                        if sign_ch == '+' || sign_ch == '-' {
                            self.advance();
                            value.push(sign_ch);
                        }
                    }
                }
                _ => break,
            }
        }

        let token_type = if is_float {
            TokenType::Double
        } else {
            TokenType::Integer
        };

        Ok(Token::new(token_type, value, line, column, position))
    }

    fn read_identifier(&mut self, first: char, line: usize, column: usize, position: usize) -> CfgppResult<Token> {
        let mut value = String::new();
        value.push(first);

        while let Some(&ch) = self.peek() {
            if ch.is_alphanumeric() || ch == '_' {
                self.advance();
                value.push(ch);
            } else {
                break;
            }
        }

        let token_type = match value.as_str() {
            "true" | "false" => TokenType::Boolean,
            "null" => TokenType::Null,
            "enum" => TokenType::Enum,
            _ => TokenType::Identifier,
        };

        Ok(Token::new(token_type, value, line, column, position))
    }

    fn read_line_comment(&mut self, line: usize, column: usize, position: usize) -> Token {
        let mut value = String::from("//");

        while let Some(&ch) = self.peek() {
            if ch == '\n' {
                break;
            }
            self.advance();
            value.push(ch);
        }

        Token::new(TokenType::Comment, value, line, column, position)
    }

    fn skip_whitespace(&mut self) {
        while let Some(&ch) = self.peek() {
            if ch.is_whitespace() {
                self.advance();
            } else {
                break;
            }
        }
    }

    fn peek(&mut self) -> Option<&char> {
        self.chars.peek()
    }

    fn advance(&mut self) -> Option<char> {
        if let Some(ch) = self.chars.next() {
            self.position += 1;
            if ch == '\n' {
                self.line += 1;
                self.column = 1;
            } else {
                self.column += 1;
            }
            Some(ch)
        } else {
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_tokenization() {
        let input = r#"
        database {
            host = "localhost";
            port = 5432;
            ssl = true;
        }
        "#;

        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();

        assert!(!tokens.is_empty());
        assert_eq!(tokens.last().unwrap().token_type, TokenType::Eof);
    }

    #[test]
    fn test_string_parsing() {
        let input = r#""hello world""#;
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();

        assert_eq!(tokens[0].token_type, TokenType::String);
        assert_eq!(tokens[0].value, "hello world");
    }

    #[test]
    fn test_number_parsing() {
        let input = "123 45.67 1.23e-4";
        let mut lexer = Lexer::new(input);
        let tokens = lexer.tokenize().unwrap();

        assert_eq!(tokens[0].token_type, TokenType::Integer);
        assert_eq!(tokens[0].value, "123");
        
        assert_eq!(tokens[1].token_type, TokenType::Double);
        assert_eq!(tokens[1].value, "45.67");
        
        assert_eq!(tokens[2].token_type, TokenType::Double);
        assert_eq!(tokens[2].value, "1.23e-4");
    }
}
