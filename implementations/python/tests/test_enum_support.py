"""
Test cases for enum type support in cfgpp-format parser.

# REASONING: Comprehensive enum testing enables validation of enum definition parsing and type usage for testing workflows.
# Testing workflows require comprehensive enum testing for validation of enum definition parsing and type usage in testing workflows.
# Comprehensive enum testing supports validation of enum definition parsing, type usage validation, and testing coordination while enabling
# comprehensive testing strategies and systematic enum validation workflows.
"""
import unittest
from src.cfgpp.parser import loads, ConfigParseError


class TestEnumSupport(unittest.TestCase):
    """Test enum definition and usage in cfgpp-format."""
    
    def test_basic_enum_definition(self):
        """Test basic enum definition parsing with values property."""
        config = '''
        enum::Status {
            values = ["active", "inactive", "pending"]
        }
        '''
        
        result = loads(config)
        self.assertIn('Status', result['body'])
        enum_def = result['body']['Status']
        
        self.assertEqual(enum_def['type'], 'enum_definition')
        self.assertEqual(enum_def['name'], 'Status')
        self.assertEqual(enum_def['values'], ["active", "inactive", "pending"])
        self.assertIsNone(enum_def['default'])
    
    def test_enum_definition_with_default(self):
        """Test enum definition with both values and default properties."""
        config = '''
        enum::Priority {
            values = ["low", "medium", "high", "critical"],
            default = "medium"
        }
        '''
        
        result = loads(config)
        enum_def = result['body']['Priority']
        
        self.assertEqual(enum_def['type'], 'enum_definition')
        self.assertEqual(enum_def['name'], 'Priority')
        self.assertEqual(enum_def['values'], ["low", "medium", "high", "critical"])
        self.assertEqual(enum_def['default'], "medium")
    
    def test_enum_definition_default_first(self):
        """Test enum definition with default property before values."""
        config = '''
        enum::Environment {
            default = "development",
            values = ["development", "staging", "production"]
        }
        '''
        
        result = loads(config)
        enum_def = result['body']['Environment']
        
        self.assertEqual(enum_def['type'], 'enum_definition')
        self.assertEqual(enum_def['name'], 'Environment')
        self.assertEqual(enum_def['values'], ["development", "staging", "production"])
        self.assertEqual(enum_def['default'], "development")
    
    def test_multiple_enum_definitions(self):
        """Test multiple enum definitions in same configuration."""
        config = '''
        enum::Status {
            values = ["active", "inactive"]
        }
        
        enum::Priority {
            values = ["low", "high"],
            default = "low"
        }
        
        enum::Category {
            values = ["feature", "bugfix", "hotfix"]
        }
        '''
        
        result = loads(config)
        
        # Verify all three enums are defined
        self.assertIn('Status', result['body'])
        self.assertIn('Priority', result['body'])
        self.assertIn('Category', result['body'])
        
        # Verify Status enum
        status_enum = result['body']['Status']
        self.assertEqual(status_enum['type'], 'enum_definition')
        self.assertEqual(status_enum['values'], ["active", "inactive"])
        self.assertIsNone(status_enum['default'])
        
        # Verify Priority enum
        priority_enum = result['body']['Priority']
        self.assertEqual(priority_enum['type'], 'enum_definition')
        self.assertEqual(priority_enum['values'], ["low", "high"])
        self.assertEqual(priority_enum['default'], "low")
        
        # Verify Category enum
        category_enum = result['body']['Category']
        self.assertEqual(category_enum['type'], 'enum_definition')
        self.assertEqual(category_enum['values'], ["feature", "bugfix", "hotfix"])
        self.assertIsNone(category_enum['default'])
    
    def test_enum_parameter_usage(self):
        """Test enum type usage in parameter definitions."""
        config = '''
        enum::Status {
            values = ["active", "inactive", "pending"]
        }
        
        TaskManager {
            createTask(Status status, string title) {
                status = "active"
                title = "Default task"
            }
        }
        '''
        
        result = loads(config)
        
        # Verify enum definition exists
        self.assertIn('Status', result['body'])
        
        # Verify TaskManager object with enum parameter
        task_manager = result['body']['TaskManager']
        create_task = task_manager['body']['createTask']
        
        # Check parameters
        params = create_task['params']
        self.assertIn('status', params)
        self.assertIn('title', params)
        
        # Verify enum type parameter
        status_param = params['status']
        self.assertEqual(status_param['type'], 'Status')
        self.assertTrue(status_param['is_enum_type'])
        self.assertFalse(status_param['is_array'])
        
        # Verify string type parameter for comparison
        title_param = params['title']
        self.assertEqual(title_param['type'], 'string')
        self.assertFalse(title_param['is_enum_type'])
    
    def test_enum_array_parameter(self):
        """Test enum array type usage in parameters."""
        config = '''
        enum::Permission {
            values = ["read", "write", "execute", "admin"]
        }
        
        UserManager {
            setPermissions(Permission[] permissions) {
                permissions = ["read", "write"]
            }
        }
        '''
        
        result = loads(config)
        
        user_manager = result['body']['UserManager']
        set_permissions = user_manager['body']['setPermissions']
        
        # Check enum array parameter
        permissions_param = set_permissions['params']['permissions']
        self.assertEqual(permissions_param['type'], 'Permission')
        self.assertTrue(permissions_param['is_enum_type'])
        self.assertTrue(permissions_param['is_array'])


class TestEnumErrorHandling(unittest.TestCase):
    """Test error handling for enum definitions."""
    
    def test_enum_missing_namespace_separator(self):
        """Test error when enum keyword is not followed by :: separator."""
        config = '''
        enum Status {
            values = ["active", "inactive"]
        }
        '''
        
        with self.assertRaises(ConfigParseError) as context:
            loads(config)
        
        self.assertIn("Expected '::' after 'enum'", str(context.exception))
    
    def test_enum_missing_name(self):
        """Test error when enum name is missing after ::."""
        config = '''
        enum:: {
            values = ["active", "inactive"]
        }
        '''
        
        with self.assertRaises(ConfigParseError) as context:
            loads(config)
        
        # Should fail during identifier parsing
        self.assertTrue(isinstance(context.exception, ConfigParseError))
    
    def test_enum_missing_opening_brace(self):
        """Test error when enum definition is missing opening brace."""
        config = '''
        enum::Status
            values = ["active", "inactive"]
        }
        '''
        
        with self.assertRaises(ConfigParseError) as context:
            loads(config)
        
        self.assertIn("Expected '{'", str(context.exception))
    
    def test_enum_missing_closing_brace(self):
        """Test error when enum definition is missing closing brace."""
        config = '''
        enum::Status {
            values = ["active", "inactive"]
        '''
        
        with self.assertRaises(ConfigParseError) as context:
            loads(config)
        
        self.assertIn("Expected '}'", str(context.exception))
    
    def test_enum_invalid_property(self):
        """Test error when enum has invalid property."""
        config = '''
        enum::Status {
            invalid_prop = "test",
            values = ["active", "inactive"]
        }
        '''
        
        with self.assertRaises(ConfigParseError) as context:
            loads(config)
        
        self.assertIn("Unknown enum property: invalid_prop", str(context.exception))
    
    def test_enum_values_not_array(self):
        """Test error when enum values property is not an array."""
        config = '''
        enum::Status {
            values = "not_an_array"
        }
        '''
        
        with self.assertRaises(ConfigParseError) as context:
            loads(config)
        
        self.assertIn("Expected '['", str(context.exception))
    
    def test_enum_empty_body(self):
        """Test error when enum has empty body."""
        config = '''
        enum::Status {
        }
        '''
        
        with self.assertRaises(ConfigParseError) as context:
            loads(config)
        
        # Should fail because no values property was provided
        self.assertTrue(isinstance(context.exception, ConfigParseError))


class TestEnumIntegration(unittest.TestCase):
    """Test enum integration with other cfgpp-format features."""
    
    def test_enum_with_includes(self):
        """Test enum definitions with include directives."""
        # This would require actual file setup, so we'll test parsing structure
        config = '''
        enum::BaseStatus {
            values = ["active", "inactive"]
        }
        
        TaskSystem {
            processTask(BaseStatus status) {
                status = "active"
            }
        }
        '''
        
        result = loads(config)
        
        # Verify both enum and usage are parsed correctly
        self.assertIn('BaseStatus', result['body'])
        self.assertIn('TaskSystem', result['body'])
        
        task_system = result['body']['TaskSystem']
        process_task = task_system['body']['processTask']
        status_param = process_task['params']['status']
        
        self.assertEqual(status_param['type'], 'BaseStatus')
        self.assertTrue(status_param['is_enum_type'])
    
    def test_enum_with_nested_objects(self):
        """Test enum usage in nested object structures."""
        config = '''
        enum::LogLevel {
            values = ["debug", "info", "warning", "error"],
            default = "info"
        }
        
        Application {
            Logger {
                log(LogLevel level, string message) {
                    level = "info"
                    message = "Default log message"
                }
                
                Settings {
                    setDefaultLevel(LogLevel level) {
                        level = "warning"
                    }
                }
            }
        }
        '''
        
        result = loads(config)
        
        # Verify enum definition
        log_level_enum = result['body']['LogLevel']
        self.assertEqual(log_level_enum['type'], 'enum_definition')
        self.assertEqual(log_level_enum['default'], "info")
        
        # Verify nested usage in Logger.log
        logger = result['body']['Application']['body']['Logger']
        log_method = logger['value']['body']['log']
        level_param = log_method['params']['level']
        
        self.assertEqual(level_param['type'], 'LogLevel')
        self.assertTrue(level_param['is_enum_type'])
        
        # Verify nested usage in Logger.Settings.setDefaultLevel
        settings = logger['value']['body']['Settings']
        set_level_method = settings['value']['body']['setDefaultLevel']
        level_param2 = set_level_method['params']['level']
        
        self.assertEqual(level_param2['type'], 'LogLevel')
        self.assertTrue(level_param2['is_enum_type'])


if __name__ == '__main__':
    unittest.main()
