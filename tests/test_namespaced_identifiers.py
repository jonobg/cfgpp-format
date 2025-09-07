"""Tests for namespaced identifiers in cfgpp."""
import os
import sys
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cfgpp.parser import loads

def test_namespaced_identifier():
    """Test parsing a simple namespaced identifier."""
    config = """
    Namespace::Type {
        name = "test"
    }
    """
    
    result = loads(config)
    assert 'body' in result
    assert 'Namespace::Type' in result['body']
    assert 'body' in result['body']['Namespace::Type']
    assert 'name' in result['body']['Namespace::Type']['body']
    assert result['body']['Namespace::Type']['body']['name']['value'] == "test"

def test_nested_namespaced_identifier():
    """Test parsing a nested namespaced identifier."""
    config = """
    Namespace::Subnamespace::Type {
        name = "test"
    }
    """
    
    result = loads(config)
    assert 'body' in result
    assert 'Namespace::Subnamespace::Type' in result['body']
    assert 'body' in result['body']['Namespace::Subnamespace::Type']
    assert 'name' in result['body']['Namespace::Subnamespace::Type']['body']
    assert result['body']['Namespace::Subnamespace::Type']['body']['name']['value'] == "test"

def test_parameter_with_namespaced_type():
    """Test a parameter with a namespaced type."""
    config = """
    Config {
        Namespace::Type value = Namespace::Type { name = "test" }
    }
    """
    
    result = loads(config)
    assert 'body' in result
    assert 'Config' in result['body']
    assert 'body' in result['body']['Config']
    assert 'value' in result['body']['Config']['body']
    
    value = result['body']['Config']['body']['value']
    assert value['type'] == 'Namespace::Type'
    assert 'value' in value
    assert 'body' in value['value']
    assert 'Namespace::Type' in value['value']['body']
    assert 'body' in value['value']['body']['Namespace::Type']
    assert 'name' in value['value']['body']['Namespace::Type']['body']
    assert value['value']['body']['Namespace::Type']['body']['name']['value'] == "test"

def test_invalid_namespace_syntax():
    """Test handling of invalid namespace syntax."""
    # Test with trailing ::
    with pytest.raises(SyntaxError, match="Expected identifier after '::'"):
        loads("Namespace:: {}")
    
    # Test with leading ::
    with pytest.raises(SyntaxError, match="Expected identifier"):
        loads("::Type {}")
    
    # Test with multiple colons
    with pytest.raises(SyntaxError):
        loads("Namespace:::Type {}")

if __name__ == "__main__":
    pytest.main()
