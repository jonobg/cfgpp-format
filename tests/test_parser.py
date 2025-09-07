"""
Tests for the cfgpp parser.
"""
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cfgpp.parser import loads, load  # noqa: E402

def test_parse_simple_config():
    """Test parsing a simple configuration."""
    config = """
    AppConfig(
        string name = "test",
        int port = 8080,
        bool debug = true
    )
    """
    
    result = loads(config)
    assert 'body' in result
    assert 'AppConfig' in result['body']
    assert 'name' in result['body']['AppConfig']
    assert result['body']['AppConfig']['name'] == 'AppConfig'
    assert 'parameters' in result['body']['AppConfig']
    assert len(result['body']['AppConfig']['parameters']) == 3
    assert result['body']['AppConfig']['parameters']['name']['value'] == 'test'
    assert result['body']['AppConfig']['parameters']['port']['value'] == 8080
    assert result['body']['AppConfig']['parameters']['debug']['value'] is True

def test_parse_nested_objects():
    """Test parsing nested objects."""
    config = """
    ServerConfig {
        host = "localhost"
        port = 8080
        db = DatabaseConfig {
            name = "mydb"
            user = "admin"
        }
    }
    """

    result = loads(config)

    # The top-level object should have a 'body' with the ServerConfig
    assert 'body' in result
    assert 'ServerConfig' in result['body']
    
    server_config = result['body']['ServerConfig']
    assert 'body' in server_config
    
    # The body should have the direct properties
    assert 'host' in server_config['body']
    assert server_config['body']['host']['value'] == "localhost"
    assert 'port' in server_config['body']
    assert server_config['body']['port']['value'] == 8080

    # Check the nested database configuration
    assert 'db' in server_config['body']
    db_config = server_config['body']['db']
    assert 'value' in db_config
    assert 'body' in db_config['value']
    assert 'DatabaseConfig' in db_config['value']['body']
    
    # Check the nested properties
    db_body = db_config['value']['body']['DatabaseConfig']['body']
    assert 'name' in db_body
    assert db_body['name']['value'] == "mydb"
    
    assert 'user' in db_body
    assert db_body['user']['value'] == "admin"

def test_parse_array():
    """Test parsing an array of values."""
    config = """
    ArrayTest {
        values = [1, 2, 3, "test", true]
    }
    """
    
    result = loads(config)
    assert 'body' in result
    assert 'ArrayTest' in result['body']
    assert 'body' in result['body']['ArrayTest']
    assert 'values' in result['body']['ArrayTest']['body']
    assert result['body']['ArrayTest']['body']['values']['value'] == [1, 2, 3, "test", True]

def test_parse_example_file():
    """Test parsing the example configuration file."""
    import pytest
    pytest.skip("Skipping example file test until core functionality is complete")
    
    example_path = os.path.join(os.path.dirname(__file__), '..', 'AppConfig.cfgpp')

    # Parse the example file
    result = load(example_path)

    # Basic structure checks
    assert 'body' in result
    
    # Check for expected top-level keys
    expected_keys = ['Logging', 'Server', 'Database', 'Cache', 'Security', 'Features']
    for key in expected_keys:
        assert key in result['body'], f"Expected key '{key}' not found in result"
        
    # Check Logging configuration
    logging = result['body']['Logging']
    assert 'level' in logging
    assert logging['level']['value'] == 'INFO'
    
    # Check Server configuration
    server = result['body']['Server']
    assert 'port' in server
    assert server['port']['value'] == 8080
    assert 'environment' in server
    assert server['environment']['value'] == 'development'
    
    # Check for UserConfig
    assert 'userConf' in result['body']
    user_config = result['body']['userConf']
    assert 'users' in user_config['parameters']
    assert user_config['parameters']['users']['is_array'] is True
    
    # Check that we have some nested objects in the body
    assert 'body' in logging_config
    assert isinstance(logging_config['body'], dict)
