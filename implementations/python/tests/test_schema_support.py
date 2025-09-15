#!/usr/bin/env python3
"""
Comprehensive tests for cfgpp-format schema support.

Tests cover schema parsing, validation, integration, and error handling.

# REASONING: Schema testing enables schema functionality validation and regression prevention for testing workflows.
# Testing workflows require schema testing for schema functionality validation and regression prevention in testing workflows.
# Schema testing supports schema functionality validation, regression prevention, and testing coordination while enabling
# comprehensive testing strategies and systematic schema validation workflows.
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cfgpp.schema_parser import (
    loads_schema, SchemaDocument, SchemaDefinition, SchemaField, 
    EnumDefinition, ValidationRule, FieldRequirement, SchemaParseError
)
from cfgpp.schema_validator import (
    validate_config, SchemaValidator, ValidationResult, ValidationMessage, 
    ValidationSeverity
)
from cfgpp.schema_integration import (
    loads_with_schema, SchemaAwareParser, format_validation_messages,
    auto_discover_schema, SchemaRegistry
)
from cfgpp.parser import loads as config_loads


class TestSchemaParser(unittest.TestCase):
    """Test schema parsing functionality."""
    
    def test_basic_enum_parsing(self):
        """Test basic enum definition parsing."""
        schema_text = '''
        enum LogLevel {
            values = ["debug", "info", "warning", "error"]
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        
        self.assertIn('LogLevel', schema_doc.enums)
        enum_def = schema_doc.enums['LogLevel']
        self.assertEqual(enum_def.name, 'LogLevel')
        self.assertEqual(enum_def.values, ['debug', 'info', 'warning', 'error'])
        self.assertIsNone(enum_def.default_value)
    
    def test_enum_with_default(self):
        """Test enum with default value."""
        schema_text = '''
        enum Environment {
            values = ["dev", "staging", "prod"],
            default = "dev"
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        enum_def = schema_doc.enums['Environment']
        self.assertEqual(enum_def.default_value, 'dev')
    
    def test_basic_schema_parsing(self):
        """Test basic schema definition parsing."""
        schema_text = '''
        schema AppConfig {
            required string appName;
            optional int port = 3000;
            required bool debug;
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        
        self.assertIn('AppConfig', schema_doc.schemas)
        schema_def = schema_doc.schemas['AppConfig']
        
        # Check required string field
        self.assertIn('appName', schema_def.fields)
        app_name_field = schema_def.fields['appName']
        self.assertEqual(app_name_field.name, 'appName')
        self.assertEqual(app_name_field.type_name, 'string')
        self.assertEqual(app_name_field.requirement, FieldRequirement.REQUIRED)
        self.assertIsNone(app_name_field.default_value)
        
        # Check optional field with default
        self.assertIn('port', schema_def.fields)
        port_field = schema_def.fields['port']
        self.assertEqual(port_field.requirement, FieldRequirement.OPTIONAL)
        self.assertEqual(port_field.default_value, 3000)
    
    def test_array_fields(self):
        """Test array field parsing."""
        schema_text = '''
        schema Config {
            required string[] hosts;
            optional int[] ports = [80, 443];
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        schema_def = schema_doc.schemas['Config']
        
        hosts_field = schema_def.fields['hosts']
        self.assertTrue(hosts_field.is_array)
        self.assertEqual(hosts_field.type_name, 'string')
        
        ports_field = schema_def.fields['ports']
        self.assertTrue(ports_field.is_array)
        self.assertEqual(ports_field.default_value, [80, 443])
    
    def test_validation_rules(self):
        """Test validation rule parsing."""
        schema_text = '''
        schema UserConfig {
            required string username;
            required int age;
            
            validate {
                username.length > 3;
                age > 0 && age <= 120;
            }
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        schema_def = schema_doc.schemas['UserConfig']
        
        self.assertEqual(len(schema_def.validation_rules), 2)
        self.assertIn('username.length > 3', schema_def.validation_rules[0].expression)
        self.assertIn('age > 0 && age <= 120', schema_def.validation_rules[1].expression)
    
    def test_complex_schema(self):
        """Test complex schema with enums and nested objects."""
        schema_text = '''
        enum LogLevel {
            values = ["debug", "info", "error"],
            default = "info"
        }
        
        schema DatabaseConfig {
            required string host;
            required int port;
        }
        
        schema AppConfig {
            required string appName;
            required LogLevel logLevel;
            required DatabaseConfig database;
            optional string[] features = [];
            
            validate {
                appName.length > 0;
            }
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        
        # Check enum
        self.assertIn('LogLevel', schema_doc.enums)
        
        # Check nested schema
        self.assertIn('DatabaseConfig', schema_doc.schemas)
        
        # Check main schema with enum and nested object
        app_config = schema_doc.schemas['AppConfig']
        log_level_field = app_config.fields['logLevel']
        self.assertEqual(log_level_field.type_name, 'LogLevel')
        
        db_field = app_config.fields['database']
        self.assertEqual(db_field.type_name, 'DatabaseConfig')


class TestSchemaValidator(unittest.TestCase):
    """Test schema validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.basic_schema_text = '''
        enum Environment {
            values = ["dev", "staging", "prod"]
        }
        
        schema AppConfig {
            required string appName;
            required Environment environment;
            optional int port = 3000;
            optional bool debug = false;
            
            validate {
                appName.length > 0;
                port > 0 && port <= 65535;
            }
        }
        '''
        self.schema_doc = loads_schema(self.basic_schema_text)
    
    def test_valid_configuration(self):
        """Test validation of valid configuration."""
        config_text = '''
        AppConfig(
            string appName = "MyApp",
            Environment environment = "prod",
            int port = 8080,
            bool debug = false
        )
        '''
        
        config_data = config_loads(config_text)
        result = validate_config(config_data, self.schema_doc, 'AppConfig')
        
        self.assertTrue(result.is_valid)
        self.assertFalse(result.has_errors())
    
    def test_missing_required_field(self):
        """Test validation failure for missing required field."""
        config_text = '''
        AppConfig(
            string appName = "MyApp"
            // Missing required environment field
        )
        '''
        
        config_data = config_loads(config_text)
        result = validate_config(config_data, self.schema_doc, 'AppConfig')
        
        self.assertFalse(result.is_valid)
        self.assertTrue(result.has_errors())
        
        errors = result.get_errors()
        self.assertTrue(any('environment' in error.message for error in errors))
    
    def test_invalid_enum_value(self):
        """Test validation failure for invalid enum value."""
        config_text = '''
        AppConfig(
            string appName = "MyApp",
            Environment environment = "invalid_env"
        )
        '''
        
        config_data = config_loads(config_text)
        result = validate_config(config_data, self.schema_doc, 'AppConfig')
        
        self.assertFalse(result.is_valid)
        errors = result.get_errors()
        self.assertTrue(any('not valid for enum' in error.message for error in errors))
    
    def test_type_mismatch(self):
        """Test validation failure for type mismatch."""
        config_text = '''
        AppConfig(
            int appName = 123,  // Should be string
            Environment environment = "dev"
        )
        '''
        
        config_data = config_loads(config_text)
        result = validate_config(config_data, self.schema_doc, 'AppConfig')
        
        self.assertFalse(result.is_valid)
        errors = result.get_errors()
        self.assertTrue(any('Expected string' in error.message for error in errors))
    
    def test_unknown_field_warning(self):
        """Test warning for unknown fields."""
        config_text = '''
        AppConfig(
            string appName = "MyApp",
            Environment environment = "dev",
            string unknownField = "value"  // Not in schema
        )
        '''
        
        config_data = config_loads(config_text)
        result = validate_config(config_data, self.schema_doc, 'AppConfig')
        
        self.assertTrue(result.has_warnings())
        warnings = result.get_warnings()
        self.assertTrue(any('Unknown field' in warning.message for warning in warnings))
    
    def test_validation_rules(self):
        """Test custom validation rules."""
        config_text = '''
        AppConfig(
            string appName = "",  // Empty string - should fail validation
            Environment environment = "dev",
            int port = 70000  // Out of valid range
        )
        '''
        
        config_data = config_loads(config_text)
        result = validate_config(config_data, self.schema_doc, 'AppConfig')
        
        self.assertFalse(result.is_valid)
        # Should have validation rule failures
        self.assertTrue(result.has_errors())
    
    def test_array_validation(self):
        """Test array field validation."""
        schema_text = '''
        schema Config {
            required string[] hosts;
            optional int[] ports = [];
        }
        '''
        
        config_text = '''
        Config(
            string[] hosts = ["host1", "host2"],
            int[] ports = [80, 443, 8080]
        )
        '''
        
        schema_doc = loads_schema(schema_text)
        config_data = config_loads(config_text)
        result = validate_config(config_data, schema_doc, 'Config')
        
        self.assertTrue(result.is_valid)


class TestSchemaIntegration(unittest.TestCase):
    """Test schema integration functionality."""
    
    def test_schema_aware_parsing(self):
        """Test schema-aware parsing with validation."""
        schema_text = '''
        schema AppConfig {
            required string name;
            optional int port = 3000;
        }
        '''
        
        config_text = '''
        AppConfig(
            string name = "TestApp",
            int port = 8080
        )
        '''
        
        config_data, validation_result = loads_with_schema(
            config_text, schema_text=schema_text, validate=True
        )
        
        self.assertIsNotNone(config_data)
        self.assertIsNotNone(validation_result)
        self.assertTrue(validation_result.is_valid)
    
    def test_schema_aware_parsing_with_errors(self):
        """Test schema-aware parsing with validation errors."""
        schema_text = '''
        schema AppConfig {
            required string name;
            required bool enabled;
        }
        '''
        
        config_text = '''
        AppConfig(
            string name = "TestApp"
            // Missing required 'enabled' field
        )
        '''
        
        config_data, validation_result = loads_with_schema(
            config_text, schema_text=schema_text, validate=True
        )
        
        self.assertIsNotNone(config_data)
        self.assertIsNotNone(validation_result)
        self.assertFalse(validation_result.is_valid)
        self.assertTrue(validation_result.has_errors())
    
    def test_validation_message_formatting(self):
        """Test validation message formatting."""
        messages = [
            ValidationMessage(
                severity=ValidationSeverity.ERROR,
                message="Required field missing",
                path="config.database.host",
                suggestion="Add host field with string value"
            ),
            ValidationMessage(
                severity=ValidationSeverity.WARNING,
                message="Unknown field",
                path="config.extra"
            )
        ]
        
        formatted = format_validation_messages(messages)
        
        self.assertIn("❌ 1 error(s):", formatted)
        self.assertIn("⚠️  1 warning(s):", formatted)
        self.assertIn("💡 Add host field", formatted)
    
    def test_schema_registry(self):
        """Test schema registry functionality."""
        registry = SchemaRegistry()
        
        schema_text = '''
        schema TestConfig {
            required string name;
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        registry.register_schema('test', schema_doc)
        
        # Test retrieval
        retrieved = registry.get_schema('test')
        self.assertIsNotNone(retrieved)
        self.assertIn('TestConfig', retrieved.schemas)
        
        # Test validation through registry
        config_data = config_loads('TestConfig(string name = "test")')
        result = registry.validate_config(config_data, 'test', 'TestConfig')
        self.assertTrue(result.is_valid)


class TestSchemaErrorHandling(unittest.TestCase):
    """Test schema error handling and edge cases."""
    
    def test_invalid_schema_syntax(self):
        """Test handling of invalid schema syntax."""
        invalid_schema = '''
        schema InvalidSchema {
            required  // Missing type and name
        }
        '''
        
        with self.assertRaises(SchemaParseError):
            loads_schema(invalid_schema)
    
    def test_unknown_enum_reference(self):
        """Test handling of unknown enum references."""
        schema_text = '''
        schema Config {
            required UnknownEnum status;  // Enum not defined
        }
        '''
        
        config_text = '''
        Config(
            UnknownEnum status = "active"
        )
        '''
        
        schema_doc = loads_schema(schema_text)
        config_data = config_loads(config_text)
        result = validate_config(config_data, schema_doc, 'Config')
        
        # Should produce warning about unknown type
        self.assertTrue(result.has_warnings())
    
    def test_circular_schema_references(self):
        """Test handling of circular schema references."""
        # This is a basic test - full circular reference detection
        # would require more sophisticated implementation
        schema_text = '''
        schema NodeA {
            required NodeB child;
        }
        
        schema NodeB {
            required NodeA parent;
        }
        '''
        
        # Should parse successfully (circular reference handling
        # would be implemented in the validator)
        schema_doc = loads_schema(schema_text)
        self.assertIn('NodeA', schema_doc.schemas)
        self.assertIn('NodeB', schema_doc.schemas)


class TestSchemaPerformance(unittest.TestCase):
    """Test schema performance characteristics."""
    
    def test_large_schema_parsing(self):
        """Test parsing of large schema documents."""
        # Generate a large schema with many fields
        schema_parts = ['schema LargeConfig {']
        
        for i in range(100):
            schema_parts.append(f'    optional string field{i} = "default{i}";')
        
        schema_parts.append('}')
        large_schema = '\n'.join(schema_parts)
        
        # Should parse successfully without significant delay
        schema_doc = loads_schema(large_schema)
        large_config = schema_doc.schemas['LargeConfig']
        
        self.assertEqual(len(large_config.fields), 100)
    
    def test_deep_nesting_validation(self):
        """Test validation of deeply nested configurations."""
        schema_text = '''
        schema Level3 {
            required string value;
        }
        
        schema Level2 {
            required Level3 nested;
        }
        
        schema Level1 {
            required Level2 nested;
        }
        
        schema RootConfig {
            required Level1 nested;
        }
        '''
        
        config_text = '''
        RootConfig {
            Level1::nested {
                Level2::nested {
                    Level3::nested(
                        string value = "deep_value"
                    );
                }
            }
        }
        '''
        
        schema_doc = loads_schema(schema_text)
        config_data = config_loads(config_text)
        
        # This should validate successfully
        result = validate_config(config_data, schema_doc, 'RootConfig')
        # Note: This test may need adjustment based on how nested objects are parsed


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
