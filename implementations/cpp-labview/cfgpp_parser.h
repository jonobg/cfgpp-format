/**
 * CFG++ High-Performance Parser Library
 * Optimized C++ parser with C API for LabVIEW integration
 * 
 * Features:
 * - Zero-copy string parsing where possible
 * - Memory pool allocation for tokens
 * - SIMD-optimized lexing for Windows
 * - Thread-safe operations
 * - LabVIEW-compatible C interface
 */

#ifndef CFGPP_PARSER_H
#define CFGPP_PARSER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>

// API Export macro for Windows DLL
#ifdef _WIN32
    #ifdef CFGPP_EXPORTS
        #define CFGPP_API __declspec(dllexport)
    #else
        #define CFGPP_API __declspec(dllimport)
    #endif
    #define CFGPP_CALL __stdcall
#else
    #define CFGPP_API
    #define CFGPP_CALL
#endif

// Error codes for LabVIEW integration
typedef enum {
    CFGPP_SUCCESS = 0,
    CFGPP_ERROR_INVALID_SYNTAX = 1,
    CFGPP_ERROR_FILE_NOT_FOUND = 2,
    CFGPP_ERROR_MEMORY_ERROR = 3,
    CFGPP_ERROR_INVALID_PARAMETER = 4,
    CFGPP_ERROR_CIRCULAR_INCLUDE = 5,
    CFGPP_ERROR_BUFFER_TOO_SMALL = 6
} CfgppResult;

// Value types for CFG++ data
typedef enum {
    CFGPP_TYPE_NULL = 0,
    CFGPP_TYPE_BOOLEAN = 1,
    CFGPP_TYPE_INTEGER = 2,
    CFGPP_TYPE_DOUBLE = 3,
    CFGPP_TYPE_STRING = 4,
    CFGPP_TYPE_ARRAY = 5,
    CFGPP_TYPE_OBJECT = 6,
    CFGPP_TYPE_ENUM = 7
} CfgppValueType;

// Opaque handle for parser context
typedef struct CfgppParser* CfgppParserHandle;
typedef struct CfgppValue* CfgppValueHandle;
typedef struct CfgppSchema* CfgppSchemaHandle;

// Parser creation and destruction
CFGPP_API CfgppResult CFGPP_CALL cfgpp_parser_create(CfgppParserHandle* parser);
CFGPP_API CfgppResult CFGPP_CALL cfgpp_parser_destroy(CfgppParserHandle parser);

// High-performance parsing functions
CFGPP_API CfgppResult CFGPP_CALL cfgpp_parse_string(
    CfgppParserHandle parser,
    const char* config_text,
    size_t text_length,
    CfgppValueHandle* result
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_parse_file(
    CfgppParserHandle parser,
    const char* file_path,
    CfgppValueHandle* result
);

// Value access functions (zero-copy where possible)
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_type(
    CfgppValueHandle value, 
    CfgppValueType* type
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_boolean(
    CfgppValueHandle value, 
    int* result
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_integer(
    CfgppValueHandle value, 
    int64_t* result
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_double(
    CfgppValueHandle value, 
    double* result
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_string(
    CfgppValueHandle value,
    char* buffer,
    size_t buffer_size,
    size_t* actual_length
);

// Object/Array navigation
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_object_size(
    CfgppValueHandle value,
    size_t* size
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_object_key_at(
    CfgppValueHandle value,
    size_t index,
    char* key_buffer,
    size_t key_buffer_size,
    size_t* actual_key_length
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_object_value_at(
    CfgppValueHandle value,
    size_t index,
    CfgppValueHandle* child_value
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_object_value_by_key(
    CfgppValueHandle value,
    const char* key,
    CfgppValueHandle* child_value
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_array_size(
    CfgppValueHandle value,
    size_t* size
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_get_array_element(
    CfgppValueHandle value,
    size_t index,
    CfgppValueHandle* element
);

// Writing/Serialization functions
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_create_object(CfgppValueHandle* value);
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_create_array(CfgppValueHandle* value);
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_create_string(const char* str, CfgppValueHandle* value);
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_create_integer(int64_t val, CfgppValueHandle* value);
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_create_double(double val, CfgppValueHandle* value);
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_create_boolean(int val, CfgppValueHandle* value);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_object_set(
    CfgppValueHandle object,
    const char* key,
    CfgppValueHandle value
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_array_push(
    CfgppValueHandle array,
    CfgppValueHandle value
);

// Serialization to CFG++ format
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_serialize(
    CfgppValueHandle value,
    char* buffer,
    size_t buffer_size,
    size_t* actual_size
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_serialize_to_file(
    CfgppValueHandle value,
    const char* file_path
);

// LabVIEW Integration - Direct variant/cluster serialization
// LabVIEW data type definitions for cross-compatibility
typedef enum {
    LABVIEW_TYPE_VOID = 0,
    LABVIEW_TYPE_I8 = 1,
    LABVIEW_TYPE_I16 = 2,
    LABVIEW_TYPE_I32 = 3,
    LABVIEW_TYPE_I64 = 5,
    LABVIEW_TYPE_U8 = 6,
    LABVIEW_TYPE_U16 = 7,
    LABVIEW_TYPE_U32 = 8,
    LABVIEW_TYPE_U64 = 10,
    LABVIEW_TYPE_SGL = 9,     // Single precision float
    LABVIEW_TYPE_DBL = 10,    // Double precision float
    LABVIEW_TYPE_BOOLEAN = 33,
    LABVIEW_TYPE_STRING = 48,
    LABVIEW_TYPE_ARRAY = 64,
    LABVIEW_TYPE_CLUSTER = 80,
    LABVIEW_TYPE_VARIANT = 15
} LabViewDataType;

// LabVIEW data header structure (matches LabVIEW internal format)
typedef struct {
    LabViewDataType type_code;
    uint32_t flags;
    uint32_t data_size;
    uint32_t dimensions;  // For arrays: number of dimensions
} LabViewDataHeader;

// Direct LabVIEW data conversion functions
CFGPP_API CfgppResult CFGPP_CALL cfgpp_from_labview_variant(
    const void* variant_data,
    size_t data_size,
    CfgppValueHandle* result
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_from_labview_cluster(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    CfgppValueHandle* result
);

// High-level LabVIEW convenience functions
CFGPP_API CfgppResult CFGPP_CALL cfgpp_variant_to_file(
    const void* variant_data,
    size_t data_size,
    const char* file_path
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_cluster_to_file(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    const char* file_path
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_variant_to_string(
    const void* variant_data,
    size_t data_size,
    char* output_buffer,
    size_t buffer_size,
    size_t* actual_size
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_cluster_to_string(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    char* output_buffer,
    size_t buffer_size,
    size_t* actual_size
);

// Memory management
CFGPP_API CfgppResult CFGPP_CALL cfgpp_value_destroy(CfgppValueHandle value);

// Error information
CFGPP_API CfgppResult CFGPP_CALL cfgpp_get_last_error_message(
    CfgppParserHandle parser,
    char* buffer,
    size_t buffer_size,
    size_t* actual_length
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_get_last_error_location(
    CfgppParserHandle parser,
    int* line,
    int* column
);

// Performance and configuration
CFGPP_API CfgppResult CFGPP_CALL cfgpp_parser_set_include_paths(
    CfgppParserHandle parser,
    const char** paths,
    size_t path_count
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_parser_enable_validation(
    CfgppParserHandle parser,
    int enable
);

// Schema support functions
CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_create(CfgppSchemaHandle* schema);
CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_destroy(CfgppSchemaHandle schema);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_parse_file(
    CfgppSchemaHandle schema,
    const char* schema_file_path
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_schema_parse_string(
    CfgppSchemaHandle schema,
    const char* schema_text,
    size_t text_length
);

// Schema validation functions
CFGPP_API CfgppResult CFGPP_CALL cfgpp_validate_value(
    CfgppSchemaHandle schema,
    CfgppValueHandle value,
    char* error_buffer,
    size_t buffer_size,
    size_t* error_length
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_validate_file(
    CfgppSchemaHandle schema,
    const char* config_file_path,
    char* error_buffer,
    size_t buffer_size,
    size_t* error_length
);

// Schema-aware LabVIEW integration
CFGPP_API CfgppResult CFGPP_CALL cfgpp_variant_to_file_validated(
    const void* variant_data,
    size_t data_size,
    const char* file_path,
    CfgppSchemaHandle schema
);

CFGPP_API CfgppResult CFGPP_CALL cfgpp_cluster_to_file_validated(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    const char* file_path,
    CfgppSchemaHandle schema
);

// Generate schema from LabVIEW data structure
CFGPP_API CfgppResult CFGPP_CALL cfgpp_generate_schema_from_cluster(
    const void* cluster_data,
    size_t data_size,
    const char** field_names,
    size_t field_count,
    char* schema_buffer,
    size_t buffer_size,
    size_t* actual_size
);

#ifdef __cplusplus
}
#endif

#endif // CFGPP_PARSER_H
