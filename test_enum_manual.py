#!/usr/bin/env python3
"""
Manual test script for enum support in cfgpp-format parser.
This script can be run directly without pytest dependencies.

# REASONING: Manual testing enables enum validation without external dependencies for testing workflows.
# Testing workflows require manual testing for enum validation without external dependencies in testing workflows.  
# Manual testing supports enum validation, dependency-free testing, and testing coordination while enabling
# comprehensive testing strategies and systematic enum verification workflows.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cfgpp.parser import loads, ConfigParseError


def test_basic_enum_definition():
    """Test basic enum definition parsing."""
    print("Testing basic enum definition...")
    
    config = '''
    enum::Status {
        values = ["active", "inactive", "pending"]
    }
    '''
    
    try:
        result = loads(config)
        assert 'Status' in result['body']
        enum_def = result['body']['Status']
        
        assert enum_def['type'] == 'enum_definition'
        assert enum_def['name'] == 'Status'
        assert enum_def['values'] == ["active", "inactive", "pending"]
        assert enum_def['default'] is None
        
        print("✓ Basic enum definition test passed")
        return True
    except Exception as e:
        print(f"✗ Basic enum definition test failed: {e}")
        return False


def test_enum_with_default():
    """Test enum definition with default value."""
    print("Testing enum with default value...")
    
    config = '''
    enum::Priority {
        values = ["low", "medium", "high"],
        default = "medium"
    }
    '''
    
    try:
        result = loads(config)
        enum_def = result['body']['Priority']
        
        assert enum_def['type'] == 'enum_definition'
        assert enum_def['name'] == 'Priority'
        assert enum_def['values'] == ["low", "medium", "high"]
        assert enum_def['default'] == "medium"
        
        print("✓ Enum with default test passed")
        return True
    except Exception as e:
        print(f"✗ Enum with default test failed: {e}")
        return False


def test_enum_parameter_usage():
    """Test enum type usage in parameters."""
    print("Testing enum parameter usage...")
    
    config = '''
    enum::Status {
        values = ["active", "inactive"]
    }
    
    TaskManager {
        createTask(Status status, string title) {
            status = "active"
            title = "Default task"
        }
    }
    '''
    
    try:
        result = loads(config)
        
        # Verify enum definition
        assert 'Status' in result['body']
        
        # Verify parameter usage
        task_manager = result['body']['TaskManager']
        create_task = task_manager['body']['createTask']
        params = create_task['params']
        
        assert 'status' in params
        status_param = params['status']
        assert status_param['type'] == 'Status'
        assert status_param['is_enum_type'] == True
        
        print("✓ Enum parameter usage test passed")
        return True
    except Exception as e:
        print(f"✗ Enum parameter usage test failed: {e}")
        return False


def test_multiple_enums():
    """Test multiple enum definitions."""
    print("Testing multiple enum definitions...")
    
    config = '''
    enum::Status {
        values = ["active", "inactive"]
    }
    
    enum::Priority {
        values = ["low", "high"],
        default = "low"
    }
    '''
    
    try:
        result = loads(config)
        
        assert 'Status' in result['body']
        assert 'Priority' in result['body']
        
        status_enum = result['body']['Status']
        priority_enum = result['body']['Priority']
        
        assert status_enum['type'] == 'enum_definition'
        assert priority_enum['type'] == 'enum_definition'
        assert priority_enum['default'] == "low"
        
        print("✓ Multiple enums test passed")
        return True
    except Exception as e:
        print(f"✗ Multiple enums test failed: {e}")
        return False


def test_enum_error_handling():
    """Test error handling for invalid enum syntax."""
    print("Testing enum error handling...")
    
    # Test missing :: separator
    invalid_config = '''
    enum Status {
        values = ["active", "inactive"]
    }
    '''
    
    try:
        loads(invalid_config)
        print("✗ Error handling test failed: Should have thrown error for missing ::")
        return False
    except ConfigParseError as e:
        if "Expected '::' after 'enum'" in str(e):
            print("✓ Error handling test passed")
            return True
        else:
            print(f"✗ Error handling test failed: Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"✗ Error handling test failed: Unexpected error: {e}")
        return False


def run_all_tests():
    """Run all enum tests and report results."""
    print("=" * 50)
    print("CFGPP-FORMAT ENUM SUPPORT TESTS")
    print("=" * 50)
    
    tests = [
        test_basic_enum_definition,
        test_enum_with_default,
        test_enum_parameter_usage,
        test_multiple_enums,
        test_enum_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enum tests PASSED! Enum support is working correctly.")
        return True
    else:
        print(f"❌ {total - passed} tests FAILED. Please check the implementation.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
