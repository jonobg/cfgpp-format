"""Tests for namespaced identifiers in cfgpp."""

import pytest

# Import from the installed package
from cfgpp import loads


def test_namespaced_identifier():
    """Test parsing a simple namespaced identifier."""
    config = """
    Namespace::Type {
        name = "test"
    }
    """

    result = loads(config)
    assert "body" in result
    assert "Namespace::Type" in result["body"]
    assert "body" in result["body"]["Namespace::Type"]
    assert "name" in result["body"]["Namespace::Type"]["body"]
    assert result["body"]["Namespace::Type"]["body"]["name"]["value"]["value"] == "test"


def test_nested_namespaced_identifier():
    """Test parsing a nested namespaced identifier."""
    config = """
    Namespace::Subnamespace::Type {
        name = "test"
    }
    """

    result = loads(config)
    assert "body" in result
    assert "Namespace::Subnamespace::Type" in result["body"]
    assert "body" in result["body"]["Namespace::Subnamespace::Type"]
    assert "name" in result["body"]["Namespace::Subnamespace::Type"]["body"]
    assert (
        result["body"]["Namespace::Subnamespace::Type"]["body"]["name"]["value"][
            "value"
        ]
        == "test"
    )


def test_parameter_with_namespaced_type():
    """Test a parameter with a namespaced type."""
    config = """
    Config {
        Namespace::Type value = Namespace::Type { name = "test" }
    }
    """

    result = loads(config)
    assert "body" in result
    assert "Config" in result["body"]
    assert "body" in result["body"]["Config"]
    assert "value" in result["body"]["Config"]["body"]
    value = result["body"]["Config"]["body"]["value"]
    assert "type" in value
    assert value["type"] == "Namespace::Type"
    assert "value" in value
    assert "name" in value["value"]
    assert value["value"]["name"]["value"]["value"] == "test"


def test_invalid_namespace_syntax():
    """Test handling of invalid namespace syntax."""
    from cfgpp.parser import ConfigParseError
    from cfgpp.lexer import LexerError

    # Test with trailing ::
    with pytest.raises(ConfigParseError, match="Incomplete namespaced identifier"):
        loads("Namespace:: {}")

    # Test with leading ::
    with pytest.raises(ConfigParseError, match="Unexpected token at top level"):
        loads("::Type {}")

    # Test with multiple colons
    with pytest.raises(LexerError):
        loads("Namespace:::Type {}")


if __name__ == "__main__":
    pytest.main()
