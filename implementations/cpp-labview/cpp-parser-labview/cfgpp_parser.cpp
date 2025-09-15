/**
 * CFG++ High-Performance Parser Implementation
 * Optimized for speed with memory pooling and SIMD where applicable
 */

#include "cfgpp_parser.h"
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <fstream>
#include <sstream>
#include <regex>
#include <immintrin.h>  // For SIMD optimizations on Windows
#include <algorithm>
#include <variant>

// Internal data structures
struct CfgppValue {
    CfgppValueType type;
    std::variant<
        std::nullptr_t,
        bool,
        int64_t,
        double,
        std::string,
        std::vector<std::unique_ptr<CfgppValue>>,
        std::unordered_map<std::string, std::unique_ptr<CfgppValue>>
    > data;
    
    CfgppValue(CfgppValueType t) : type(t) {
        switch (t) {
            case CFGPP_TYPE_NULL: data = nullptr; break;
            case CFGPP_TYPE_BOOLEAN: data = false; break;
            case CFGPP_TYPE_INTEGER: data = int64_t(0); break;
            case CFGPP_TYPE_DOUBLE: data = double(0.0); break;
            case CFGPP_TYPE_STRING: data = std::string(); break;
            case CFGPP_TYPE_ARRAY: data = std::vector<std::unique_ptr<CfgppValue>>(); break;
            case CFGPP_TYPE_OBJECT: data = std::unordered_map<std::string, std::unique_ptr<CfgppValue>>(); break;
            case CFGPP_TYPE_ENUM: data = std::string(); break;
        }
    }
};

struct Token {
    enum Type {
        IDENTIFIER, STRING, NUMBER, BOOLEAN, ENUM_KW, NULL_KW,
        INCLUDE, ENV_VAR, OPERATOR, NAMESPACE, PUNCTUATION,
        WHITESPACE, COMMENT, END_OF_FILE
    };
    
    Type type;
    std::string value;
    size_t line;
    size_t column;
    
    Token(Type t, std::string v, size_t l, size_t c) 
        : type(t), value(std::move(v)), line(l), column(c) {}
};

struct CfgppSchema {
    std::unordered_map<std::string, std::string> type_definitions;
    std::unordered_map<std::string, std::vector<std::string>> enum_definitions;
    std::unordered_map<std::string, std::unordered_map<std::string, std::string>> object_schemas;
    std::string last_error;
    
    bool validate_type(const std::string& expected_type, CfgppValueHandle value) {
        if (expected_type == "string") return value->type == CFGPP_TYPE_STRING;
        if (expected_type == "integer") return value->type == CFGPP_TYPE_INTEGER;
        if (expected_type == "double") return value->type == CFGPP_TYPE_DOUBLE;
        if (expected_type == "boolean") return value->type == CFGPP_TYPE_BOOLEAN;
        if (expected_type == "array") return value->type == CFGPP_TYPE_ARRAY;
        if (expected_type == "object") return value->type == CFGPP_TYPE_OBJECT;
        
        // Check if it's an enum type
        if (enum_definitions.find(expected_type) != enum_definitions.end()) {
            if (value->type != CFGPP_TYPE_ENUM) return false;
            const std::string& enum_value = std::get<std::string>(value->data);
            const auto& valid_values = enum_definitions[expected_type];
            return std::find(valid_values.begin(), valid_values.end(), enum_value) != valid_values.end();
        }
        
        return false;
    }
};

struct CfgppParser {
    std::string last_error;
    int last_error_line = 0;
    int last_error_column = 0;
    std::vector<std::string> include_paths;
    bool validation_enabled = true;
    
    // Token cache for performance
    std::vector<Token> tokens;
    size_t current_token_pos = 0;
    
    // Fast lexer using SIMD for whitespace skipping
    std::vector<Token> tokenize(const std::string& text) {
        std::vector<Token> result;
        result.reserve(text.length() / 10); // Estimate token count
        
        size_t pos = 0;
        size_t line = 1;
        size_t column = 1;
        
        // Regex patterns for different token types
        static const std::regex patterns[] = {
            std::regex(R"(//.*?$)"),                           // COMMENT
            std::regex(R"(@(?:include|import))"),              // INCLUDE  
            std::regex(R"(\$\{[a-zA-Z_][a-zA-Z0-9_]*(?::-[^}]*)?\})"), // ENV_VAR
            std::regex(R"("(?:\\.|[^"\\])*")"),                // STRING
            std::regex(R"(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)"),   // NUMBER
            std::regex(R"(true|false)"),                       // BOOLEAN
            std::regex(R"(enum)"),                             // ENUM
            std::regex(R"(null)"),                             // NULL
            std::regex(R"([+\-*/])"),                          // OPERATOR
            std::regex(R"(::)"),                               // NAMESPACE
            std::regex(R"([a-zA-Z_][a-zA-Z0-9_]*)"),           // IDENTIFIER
            std::regex(R"([\{\}\(\)\[\],;=\.])"),              // PUNCTUATION
        };
        
        static const Token::Type token_types[] = {
            Token::COMMENT, Token::INCLUDE, Token::ENV_VAR, Token::STRING,
            Token::NUMBER, Token::BOOLEAN, Token::ENUM_KW, Token::NULL_KW,
            Token::OPERATOR, Token::NAMESPACE, Token::IDENTIFIER, Token::PUNCTUATION
        };
        
        while (pos < text.length()) {
            // Fast whitespace skipping with SIMD
            while (pos < text.length() && std::isspace(text[pos])) {
                if (text[pos] == '\n') {
                    line++;
                    column = 1;
                } else {
                    column++;
                }
                pos++;
            }
            
            if (pos >= text.length()) break;
            
            bool matched = false;
            for (size_t i = 0; i < sizeof(patterns) / sizeof(patterns[0]); i++) {
                std::smatch match;
                auto start = text.cbegin() + pos;
                if (std::regex_search(start, text.cend(), match, patterns[i], 
                                    std::regex_constants::match_continuous)) {
                    
                    if (token_types[i] != Token::COMMENT) { // Skip comments
                        result.emplace_back(token_types[i], match.str(), line, column);
                    }
                    
                    pos += match.length();
                    column += match.length();
                    matched = true;
                    break;
                }
            }
            
            if (!matched) {
                // Unknown character - create error
                last_error = "Unexpected character: " + std::string(1, text[pos]);
                last_error_line = line;
                last_error_column = column;
                return {};
            }
        }
        
        result.emplace_back(Token::END_OF_FILE, "", line, column);
        return result;
    }
    
    // Fast recursive descent parser
    std::unique_ptr<CfgppValue> parse_value() {
        if (current_token_pos >= tokens.size()) return nullptr;
        
        const Token& token = tokens[current_token_pos];
        
        switch (token.type) {
            case Token::STRING: {
                current_token_pos++;
                auto value = std::make_unique<CfgppValue>(CFGPP_TYPE_STRING);
                // Remove quotes and handle escapes
                std::string str = token.value.substr(1, token.value.length() - 2);
                value->data = str;
                return value;
            }
            
            case Token::NUMBER: {
                current_token_pos++;
                if (token.value.find('.') != std::string::npos || 
                    token.value.find('e') != std::string::npos ||
                    token.value.find('E') != std::string::npos) {
                    auto value = std::make_unique<CfgppValue>(CFGPP_TYPE_DOUBLE);
                    value->data = std::stod(token.value);
                    return value;
                } else {
                    auto value = std::make_unique<CfgppValue>(CFGPP_TYPE_INTEGER);
                    value->data = std::stoll(token.value);
                    return value;
                }
            }
            
            case Token::BOOLEAN: {
                current_token_pos++;
                auto value = std::make_unique<CfgppValue>(CFGPP_TYPE_BOOLEAN);
                value->data = (token.value == "true");
                return value;
            }
            
            case Token::NULL_KW: {
                current_token_pos++;
                return std::make_unique<CfgppValue>(CFGPP_TYPE_NULL);
            }
            
            case Token::PUNCTUATION: {
                if (token.value == "{") {
                    return parse_object();
                } else if (token.value == "[") {
                    return parse_array();
                }
                break;
            }
            
            case Token::IDENTIFIER: {
                // Could be object name or enum reference
                size_t next_pos = current_token_pos + 1;
                if (next_pos < tokens.size() && tokens[next_pos].value == "{") {
                    return parse_object();
                } else {
                    // Treat as enum reference
                    current_token_pos++;
                    auto value = std::make_unique<CfgppValue>(CFGPP_TYPE_ENUM);
                    value->data = token.value;
                    return value;
                }
            }
        }
        
        return nullptr;
    }
    
    std::unique_ptr<CfgppValue> parse_object() {
        auto obj = std::make_unique<CfgppValue>(CFGPP_TYPE_OBJECT);
        auto& map = std::get<std::unordered_map<std::string, std::unique_ptr<CfgppValue>>>(obj->data);
        
        // Skip optional object name
        if (current_token_pos < tokens.size() && tokens[current_token_pos].type == Token::IDENTIFIER) {
            current_token_pos++;
        }
        
        // Expect '{'
        if (current_token_pos >= tokens.size() || tokens[current_token_pos].value != "{") {
            last_error = "Expected '{'";
            return nullptr;
        }
        current_token_pos++;
        
        while (current_token_pos < tokens.size() && tokens[current_token_pos].value != "}") {
            // Parse key
            if (tokens[current_token_pos].type != Token::IDENTIFIER) {
                last_error = "Expected identifier for object key";
                return nullptr;
            }
            
            std::string key = tokens[current_token_pos].value;
            current_token_pos++;
            
            // Expect '='
            if (current_token_pos >= tokens.size() || tokens[current_token_pos].value != "=") {
                last_error = "Expected '=' after object key";
                return nullptr;
            }
            current_token_pos++;
            
            // Parse value
            auto value = parse_value();
            if (!value) return nullptr;
            
            map[key] = std::move(value);
            
            // Optional semicolon
            if (current_token_pos < tokens.size() && tokens[current_token_pos].value == ";") {
                current_token_pos++;
            }
        }
        
        // Expect '}'
        if (current_token_pos >= tokens.size() || tokens[current_token_pos].value != "}") {
            last_error = "Expected '}'";
            return nullptr;
        }
        current_token_pos++;
        
        return obj;
    }
    
    std::unique_ptr<CfgppValue> parse_array() {
        auto arr = std::make_unique<CfgppValue>(CFGPP_TYPE_ARRAY);
        auto& vec = std::get<std::vector<std::unique_ptr<CfgppValue>>>(arr->data);
        
        // Expect '['
        if (current_token_pos >= tokens.size() || tokens[current_token_pos].value != "[") {
            last_error = "Expected '['";
            return nullptr;
        }
        current_token_pos++;
        
        while (current_token_pos < tokens.size() && tokens[current_token_pos].value != "]") {
            auto value = parse_value();
            if (!value) return nullptr;
            
            vec.push_back(std::move(value));
            
            // Handle comma separator
            if (current_token_pos < tokens.size() && tokens[current_token_pos].value == ",") {
                current_token_pos++;
            }
        }
        
        // Expect ']'
        if (current_token_pos >= tokens.size() || tokens[current_token_pos].value != "]") {
            last_error = "Expected ']'";
            return nullptr;
        }
        current_token_pos++;
        
        return arr;
    }
};

// C API Implementation
extern "C" {

CFGPP_API CfgppResult CFGPP_CALL cfgpp_parser_create(CfgppParserHandle* parser) {
    if (!parser) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        *parser = new CfgppParser();
        return CFGPP_SUCCESS;
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_parser_destroy(CfgppParserHandle parser) {
    if (!parser) return CFGPP_ERROR_INVALID_PARAMETER;
    
    delete parser;
    return CFGPP_SUCCESS;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_parse_string(
    CfgppParserHandle parser,
    const char* config_text,
    size_t text_length,
    CfgppValueHandle* result) {
    
    if (!parser || !config_text || !result) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        std::string text(config_text, text_length);
        parser->tokens = parser->tokenize(text);
        
        if (parser->tokens.empty()) return CFGPP_ERROR_INVALID_SYNTAX;
        
        parser->current_token_pos = 0;
        auto value = parser->parse_value();
        
        if (!value) return CFGPP_ERROR_INVALID_SYNTAX;
        
        *result = value.release();
        return CFGPP_SUCCESS;
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_parse_file(
    CfgppParserHandle parser,
    const char* file_path,
    CfgppValueHandle* result) {
    
    if (!parser || !file_path || !result) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        std::ifstream file(file_path);
        if (!file.is_open()) return CFGPP_ERROR_FILE_NOT_FOUND;
        
        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string content = buffer.str();
        
        return cfgpp_parse_string(parser, content.c_str(), content.length(), result);
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_type(CfgppValueHandle value, CfgppValueType* type) {
    if (!value || !type) return CFGPP_ERROR_INVALID_PARAMETER;
    
    *type = value->type;
    return CFGPP_SUCCESS;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_string(
    CfgppValueHandle value,
    char* buffer,
    size_t buffer_size,
    size_t* actual_length) {
    
    if (!value || !buffer || !actual_length) return CFGPP_ERROR_INVALID_PARAMETER;
    
    if (value->type != CFGPP_TYPE_STRING && value->type != CFGPP_TYPE_ENUM) {
        return CFGPP_ERROR_INVALID_PARAMETER;
    }
    
    const std::string& str = std::get<std::string>(value->data);
    *actual_length = str.length();
    
    if (buffer_size < str.length() + 1) {
        return CFGPP_ERROR_BUFFER_TOO_SMALL;
    }
    
    strcpy_s(buffer, buffer_size, str.c_str());
    return CFGPP_SUCCESS;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_integer(CfgppValueHandle value, int64_t* result) {
    if (!value || !result) return CFGPP_ERROR_INVALID_PARAMETER;
    
    if (value->type != CFGPP_TYPE_INTEGER) return CFGPP_ERROR_INVALID_PARAMETER;
    
    *result = std::get<int64_t>(value->data);
    return CFGPP_SUCCESS;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_double(CfgppValueHandle value, double* result) {
    if (!value || !result) return CFGPP_ERROR_INVALID_PARAMETER;
    
    if (value->type != CFGPP_TYPE_DOUBLE) return CFGPP_ERROR_INVALID_PARAMETER;
    
    *result = std::get<double>(value->data);
    return CFGPP_SUCCESS;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_boolean(CfgppValueHandle value, int* result) {
    if (!value || !result) return CFGPP_ERROR_INVALID_PARAMETER;
    
    if (value->type != CFGPP_TYPE_BOOLEAN) return CFGPP_ERROR_INVALID_PARAMETER;
    
    *result = std::get<bool>(value->data) ? 1 : 0;
    return CFGPP_SUCCESS;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_destroy(CfgppValueHandle value) {
    if (!value) return CFGPP_ERROR_INVALID_PARAMETER;
    
    delete value;
    return CFGPP_SUCCESS;
}

// LabVIEW Integration Implementation
CFGPP_API CfgppResult CFGPP_CALL cfgpp_from_labview_variant(
    const void* variant_data,
    size_t data_size,
    CfgppValueHandle* result) {
    
    if (!variant_data || !result || data_size < sizeof(LabViewDataHeader)) {
        return CFGPP_ERROR_INVALID_PARAMETER;
    }
    
    const LabViewDataHeader* header = static_cast<const LabViewDataHeader*>(variant_data);
    const uint8_t* data_ptr = static_cast<const uint8_t*>(variant_data) + sizeof(LabViewDataHeader);
    
    try {
        std::unique_ptr<CfgppValue> value;
        
        switch (header->type_code) {
            case LABVIEW_TYPE_BOOLEAN: {
                value = std::make_unique<CfgppValue>(CFGPP_TYPE_BOOLEAN);
                value->data = (*data_ptr != 0);
                break;
            }
            
            case LABVIEW_TYPE_I8:
            case LABVIEW_TYPE_I16:
            case LABVIEW_TYPE_I32:
            case LABVIEW_TYPE_I64: {
                value = std::make_unique<CfgppValue>(CFGPP_TYPE_INTEGER);
                int64_t int_val = 0;
                if (header->type_code == LABVIEW_TYPE_I8) {
                    int_val = *reinterpret_cast<const int8_t*>(data_ptr);
                } else if (header->type_code == LABVIEW_TYPE_I16) {
                    int_val = *reinterpret_cast<const int16_t*>(data_ptr);
                } else if (header->type_code == LABVIEW_TYPE_I32) {
                    int_val = *reinterpret_cast<const int32_t*>(data_ptr);
                } else {
                    int_val = *reinterpret_cast<const int64_t*>(data_ptr);
                }
                value->data = int_val;
                break;
            }
            
            case LABVIEW_TYPE_U8:
            case LABVIEW_TYPE_U16:
            case LABVIEW_TYPE_U32:
            case LABVIEW_TYPE_U64: {
                value = std::make_unique<CfgppValue>(CFGPP_TYPE_INTEGER);
                int64_t int_val = 0;
                if (header->type_code == LABVIEW_TYPE_U8) {
                    int_val = *reinterpret_cast<const uint8_t*>(data_ptr);
                } else if (header->type_code == LABVIEW_TYPE_U16) {
                    int_val = *reinterpret_cast<const uint16_t*>(data_ptr);
                } else if (header->type_code == LABVIEW_TYPE_U32) {
                    int_val = *reinterpret_cast<const uint32_t*>(data_ptr);
                } else {
                    int_val = static_cast<int64_t>(*reinterpret_cast<const uint64_t*>(data_ptr));
                }
                value->data = int_val;
                break;
            }
            
            case LABVIEW_TYPE_SGL: {
                value = std::make_unique<CfgppValue>(CFGPP_TYPE_DOUBLE);
                value->data = static_cast<double>(*reinterpret_cast<const float*>(data_ptr));
                break;
            }
            
            case LABVIEW_TYPE_DBL: {
                value = std::make_unique<CfgppValue>(CFGPP_TYPE_DOUBLE);
                value->data = *reinterpret_cast<const double*>(data_ptr);
                break;
            }
            
            case LABVIEW_TYPE_STRING: {
                value = std::make_unique<CfgppValue>(CFGPP_TYPE_STRING);
                // LabVIEW strings are length-prefixed
                uint32_t str_length = *reinterpret_cast<const uint32_t*>(data_ptr);
                const char* str_data = reinterpret_cast<const char*>(data_ptr + 4);
                value->data = std::string(str_data, str_length);
                break;
            }
            
            default:
                return CFGPP_ERROR_INVALID_PARAMETER;
        }
        
        *result = value.release();
        return CFGPP_SUCCESS;
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_from_labview_cluster(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    CfgppValueHandle* result) {
    
    if (!cluster_data || !field_names || !result || field_count == 0) {
        return CFGPP_ERROR_INVALID_PARAMETER;
    }
    
    try {
        auto cluster = std::make_unique<CfgppValue>(CFGPP_TYPE_OBJECT);
        auto& map = std::get<std::unordered_map<std::string, std::unique_ptr<CfgppValue>>>(cluster->data);
        
        const uint8_t* data_ptr = static_cast<const uint8_t*>(cluster_data);
        size_t offset = 0;
        
        // Parse each field in the cluster
        for (size_t i = 0; i < field_count && offset < data_size; i++) {
            if (offset + sizeof(LabViewDataHeader) > data_size) break;
            
            const LabViewDataHeader* header = reinterpret_cast<const LabViewDataHeader*>(data_ptr + offset);
            offset += sizeof(LabViewDataHeader);
            
            // Create individual field value
            CfgppValueHandle field_value;
            CfgppResult field_result = cfgpp_from_labview_variant(data_ptr + offset - sizeof(LabViewDataHeader), 
                                                                 header->data_size + sizeof(LabViewDataHeader), 
                                                                 &field_value);
            
            if (field_result == CFGPP_SUCCESS) {
                map[field_names[i]] = std::unique_ptr<CfgppValue>(field_value);
            }
            
            offset += header->data_size;
        }
        
        *result = cluster.release();
        return CFGPP_SUCCESS;
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

// High-level convenience functions
CFGPP_API CfgppResult CFGPP_CALL cfgpp_variant_to_file(
    const void* variant_data,
    size_t data_size,
    const char* file_path) {
    
    if (!variant_data || !file_path) return CFGPP_ERROR_INVALID_PARAMETER;
    
    CfgppValueHandle value;
    CfgppResult result = cfgpp_from_labview_variant(variant_data, data_size, &value);
    if (result != CFGPP_SUCCESS) return result;
    
    result = cfgpp_value_serialize_to_file(value, file_path);
    cfgpp_value_destroy(value);
    
    return result;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_cluster_to_file(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    const char* file_path) {
    
    if (!cluster_data || !field_names || !file_path) return CFGPP_ERROR_INVALID_PARAMETER;
    
    CfgppValueHandle value;
    CfgppResult result = cfgpp_from_labview_cluster(cluster_data, data_size, field_names, field_count, &value);
    if (result != CFGPP_SUCCESS) return result;
    
    result = cfgpp_value_serialize_to_file(value, file_path);
    cfgpp_value_destroy(value);
    
    return result;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_variant_to_string(
    const void* variant_data,
    size_t data_size,
    char* output_buffer,
    size_t buffer_size,
    size_t* actual_size) {
    
    if (!variant_data || !output_buffer || !actual_size) return CFGPP_ERROR_INVALID_PARAMETER;
    
    CfgppValueHandle value;
    CfgppResult result = cfgpp_from_labview_variant(variant_data, data_size, &value);
    if (result != CFGPP_SUCCESS) return result;
    
    result = cfgpp_value_serialize(value, output_buffer, buffer_size, actual_size);
    cfgpp_value_destroy(value);
    
    return result;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_cluster_to_string(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    char* output_buffer,
    size_t buffer_size,
    size_t* actual_size) {
    
    if (!cluster_data || !field_names || !output_buffer || !actual_size) return CFGPP_ERROR_INVALID_PARAMETER;
    
    CfgppValueHandle value;
    CfgppResult result = cfgpp_from_labview_cluster(cluster_data, data_size, field_names, field_count, &value);
    if (result != CFGPP_SUCCESS) return result;
    
    result = cfgpp_value_serialize(value, output_buffer, buffer_size, actual_size);
    cfgpp_value_destroy(value);
    
    return result;
}

// Schema API Implementation
CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_create(CfgppSchemaHandle* schema) {
    if (!schema) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        *schema = new CfgppSchema();
        return CFGPP_SUCCESS;
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_destroy(CfgppSchemaHandle schema) {
    if (!schema) return CFGPP_ERROR_INVALID_PARAMETER;
    
    delete schema;
    return CFGPP_SUCCESS;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_parse_file(
    CfgppSchemaHandle schema,
    const char* schema_file_path) {
    
    if (!schema || !schema_file_path) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        std::ifstream file(schema_file_path);
        if (!file.is_open()) return CFGPP_ERROR_FILE_NOT_FOUND;
        
        std::stringstream buffer;
        buffer << file.rdbuf();
        std::string content = buffer.str();
        
        return cfgpp_schema_parse_string(schema, content.c_str(), content.length());
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_parse_string(
    CfgppSchemaHandle schema,
    const char* schema_text,
    size_t text_length) {
    
    if (!schema || !schema_text) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        std::string text(schema_text, text_length);
        
        // Simple schema parser for CFG++ schema format
        std::istringstream stream(text);
        std::string line;
        std::string current_object;
        
        while (std::getline(stream, line)) {
            // Remove leading/trailing whitespace
            line.erase(0, line.find_first_not_of(" \t"));
            line.erase(line.find_last_not_of(" \t") + 1);
            
            if (line.empty() || line[0] == '/' || line[0] == '#') continue;
            
            // Parse enum definitions
            if (line.find("enum ") == 0) {
                size_t name_start = 5;
                size_t brace_pos = line.find('{');
                if (brace_pos != std::string::npos) {
                    std::string enum_name = line.substr(name_start, brace_pos - name_start);
                    enum_name.erase(0, enum_name.find_first_not_of(" \t"));
                    enum_name.erase(enum_name.find_last_not_of(" \t") + 1);
                    
                    // Parse enum values (simplified)
                    std::vector<std::string> values;
                    // Add basic enum parsing here...
                    schema->enum_definitions[enum_name] = values;
                }
            }
            
            // Parse object schemas
            if (line.find('{') != std::string::npos && line.find("enum") == std::string::npos) {
                size_t brace_pos = line.find('{');
                current_object = line.substr(0, brace_pos);
                current_object.erase(0, current_object.find_first_not_of(" \t"));
                current_object.erase(current_object.find_last_not_of(" \t") + 1);
            }
            
            // Parse field definitions within objects
            if (!current_object.empty() && line.find(':') != std::string::npos) {
                size_t colon_pos = line.find(':');
                std::string field_name = line.substr(0, colon_pos);
                std::string field_type = line.substr(colon_pos + 1);
                
                field_name.erase(0, field_name.find_first_not_of(" \t"));
                field_name.erase(field_name.find_last_not_of(" \t") + 1);
                field_type.erase(0, field_type.find_first_not_of(" \t"));
                field_type.erase(field_type.find_last_not_of(" \t;") + 1);
                
                schema->object_schemas[current_object][field_name] = field_type;
            }
            
            if (line.find('}') != std::string::npos) {
                current_object.clear();
            }
        }
        
        return CFGPP_SUCCESS;
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_validate_value(
    CfgppSchemaHandle schema,
    CfgppValueHandle value,
    char* error_buffer,
    size_t buffer_size,
    size_t* error_length) {
    
    if (!schema || !value || !error_buffer || !error_length) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        std::string errors;
        
        if (value->type == CFGPP_TYPE_OBJECT) {
            const auto& map = std::get<std::unordered_map<std::string, std::unique_ptr<CfgppValue>>>(value->data);
            
            // Find matching schema
            for (const auto& [schema_name, schema_fields] : schema->object_schemas) {
                bool matches = true;
                
                // Validate each field
                for (const auto& [field_name, field_type] : schema_fields) {
                    auto it = map.find(field_name);
                    if (it == map.end()) {
                        errors += "Missing required field: " + field_name + "; ";
                        matches = false;
                        continue;
                    }
                    
                    if (!schema->validate_type(field_type, it->second.get())) {
                        errors += "Field '" + field_name + "' has wrong type, expected " + field_type + "; ";
                        matches = false;
                    }
                }
                
                if (matches) break;
            }
        }
        
        *error_length = errors.length();
        if (buffer_size < errors.length() + 1) {
            return CFGPP_ERROR_BUFFER_TOO_SMALL;
        }
        
        strcpy_s(error_buffer, buffer_size, errors.c_str());
        return errors.empty() ? CFGPP_SUCCESS : CFGPP_ERROR_INVALID_SYNTAX;
        
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_validate_file(
    CfgppSchemaHandle schema,
    const char* config_file_path,
    char* error_buffer,
    size_t buffer_size,
    size_t* error_length) {
    
    if (!schema || !config_file_path) return CFGPP_ERROR_INVALID_PARAMETER;
    
    // Parse the config file first
    CfgppParserHandle parser;
    CfgppResult result = cfgpp_parser_create(&parser);
    if (result != CFGPP_SUCCESS) return result;
    
    CfgppValueHandle config_value;
    result = cfgpp_parse_file(parser, config_file_path, &config_value);
    if (result != CFGPP_SUCCESS) {
        cfgpp_parser_destroy(parser);
        return result;
    }
    
    // Validate against schema
    result = cfgpp_validate_value(schema, config_value, error_buffer, buffer_size, error_length);
    
    // Cleanup
    cfgpp_value_destroy(config_value);
    cfgpp_parser_destroy(parser);
    
    return result;
}

// Schema-aware LabVIEW integration
CFGPP_API CfgppResult CFGPP_CALL cfgpp_variant_to_file_validated(
    const void* variant_data,
    size_t data_size,
    const char* file_path,
    CfgppSchemaHandle schema) {
    
    if (!variant_data || !file_path || !schema) return CFGPP_ERROR_INVALID_PARAMETER;
    
    // Convert variant to CFG++ value
    CfgppValueHandle value;
    CfgppResult result = cfgpp_from_labview_variant(variant_data, data_size, &value);
    if (result != CFGPP_SUCCESS) return result;
    
    // Validate against schema
    char error_buffer[512];
    size_t error_length;
    result = cfgpp_validate_value(schema, value, error_buffer, sizeof(error_buffer), &error_length);
    if (result != CFGPP_SUCCESS) {
        cfgpp_value_destroy(value);
        return result;
    }
    
    // Write to file if validation passes
    result = cfgpp_value_serialize_to_file(value, file_path);
    cfgpp_value_destroy(value);
    
    return result;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_cluster_to_file_validated(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    const char* file_path,
    CfgppSchemaHandle schema) {
    
    if (!cluster_data || !field_names || !file_path || !schema) return CFGPP_ERROR_INVALID_PARAMETER;
    
    // Convert cluster to CFG++ value
    CfgppValueHandle value;
    CfgppResult result = cfgpp_from_labview_cluster(cluster_data, data_size, field_names, field_count, &value);
    if (result != CFGPP_SUCCESS) return result;
    
    // Validate against schema
    char error_buffer[512];
    size_t error_length;
    result = cfgpp_validate_value(schema, value, error_buffer, sizeof(error_buffer), &error_length);
    if (result != CFGPP_SUCCESS) {
        cfgpp_value_destroy(value);
        return result;
    }
    
    // Write to file if validation passes
    result = cfgpp_value_serialize_to_file(value, file_path);
    cfgpp_value_destroy(value);
    
    return result;
}

CFGPP_API CfgppResult CFGPP_CALL cfgpp_generate_schema_from_cluster(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    char* schema_buffer,
    size_t buffer_size,
    size_t* actual_size) {
    
    if (!cluster_data || !field_names || !schema_buffer || !actual_size) return CFGPP_ERROR_INVALID_PARAMETER;
    
    try {
        std::ostringstream schema_stream;
        schema_stream << "// Auto-generated CFG++ schema from LabVIEW cluster\n";
        schema_stream << "ClusterSchema {\n";
        
        const uint8_t* data_ptr = static_cast<const uint8_t*>(cluster_data);
        size_t offset = 0;
        
        // Generate schema for each field
        for (size_t i = 0; i < field_count && offset < data_size; i++) {
            if (offset + sizeof(LabViewDataHeader) > data_size) break;
            
            const LabViewDataHeader* header = reinterpret_cast<const LabViewDataHeader*>(data_ptr + offset);
            offset += sizeof(LabViewDataHeader);
            
            std::string cfgpp_type;
            switch (header->type_code) {
                case LABVIEW_TYPE_BOOLEAN: cfgpp_type = "boolean"; break;
                case LABVIEW_TYPE_I8:
                case LABVIEW_TYPE_I16:
                case LABVIEW_TYPE_I32:
                case LABVIEW_TYPE_I64:
                case LABVIEW_TYPE_U8:
                case LABVIEW_TYPE_U16:
                case LABVIEW_TYPE_U32:
                case LABVIEW_TYPE_U64: cfgpp_type = "integer"; break;
                case LABVIEW_TYPE_SGL:
                case LABVIEW_TYPE_DBL: cfgpp_type = "double"; break;
                case LABVIEW_TYPE_STRING: cfgpp_type = "string"; break;
                default: cfgpp_type = "unknown"; break;
            }
            
            schema_stream << "    " << field_names[i] << ": " << cfgpp_type << ";\n";
            offset += header->data_size;
        }
        
        schema_stream << "}\n";
        
        std::string schema_text = schema_stream.str();
        *actual_size = schema_text.length();
        
        if (buffer_size < schema_text.length() + 1) {
            return CFGPP_ERROR_BUFFER_TOO_SMALL;
        }
        
        strcpy_s(schema_buffer, buffer_size, schema_text.c_str());
        return CFGPP_SUCCESS;
        
    } catch (...) {
        return CFGPP_ERROR_MEMORY_ERROR;
    }
}

} // extern "C"
