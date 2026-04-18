"""
Tests for the cfgpp parser.
"""

import os
from cfgpp.core.parser import loads, load


def test_parse_simple_config():
    """Test parsing a simple configuration."""
    config = """
    AppConfig {
        name = "test",
        port = 8080,
        debug = true
    }
    """

    result = loads(config)
    assert "body" in result
    assert "AppConfig" in result["body"]
    assert "body" in result["body"]["AppConfig"]
    assert "name" in result["body"]["AppConfig"]["body"]
    assert result["body"]["AppConfig"]["body"]["name"]["value"]["value"] == "test"
    assert "port" in result["body"]["AppConfig"]["body"]
    assert result["body"]["AppConfig"]["body"]["port"]["value"]["value"] == 8080
    assert "debug" in result["body"]["AppConfig"]["body"]
    assert result["body"]["AppConfig"]["body"]["debug"]["value"]["value"] is True


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
    assert "body" in result
    assert "ServerConfig" in result["body"]

    server_config = result["body"]["ServerConfig"]
    assert "body" in server_config

    # The body should have the direct properties
    assert "host" in server_config["body"]
    assert server_config["body"]["host"]["value"]["value"] == "localhost"
    assert "port" in server_config["body"]
    assert server_config["body"]["port"]["value"]["value"] == 8080

    # Check the nested database configuration
    assert "db" in server_config["body"]
    db_config = server_config["body"]["db"]

    # The db_config should have 'name' and 'user' in its value
    assert "value" in db_config
    assert "name" in db_config["value"]
    assert db_config["value"]["name"]["value"]["value"] == "mydb"
    assert "user" in db_config["value"]
    assert db_config["value"]["user"]["value"]["value"] == "admin"


def test_parse_array():
    """Test parsing an array of values."""
    config = """
    ArrayTest {
        values = [1, 2, 3, "test", true]
    }
    """

    result = loads(config)
    assert "body" in result
    assert "ArrayTest" in result["body"]
    assert "body" in result["body"]["ArrayTest"]
    assert "values" in result["body"]["ArrayTest"]["body"]

    # Get the array value
    values = result["body"]["ArrayTest"]["body"]["values"]["value"]

    # Check each element's value
    assert len(values) == 5
    assert values[0]["value"] == 1
    assert values[1]["value"] == 2
    assert values[2]["value"] == 3
    assert values[3]["value"] == "test"
    assert values[4]["value"] is True


def test_parse_complex_config_example():
    """Test parsing the complex-config.cfgpp example file."""
    example_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "specification",
        "examples",
        "advanced",
        "complex-config.cfgpp",
    )

    assert os.path.exists(example_path), f"Example file not found: {example_path}"

    result = load(example_path)

    assert "body" in result
    assert isinstance(result["body"], dict)
    assert "ComplexConfig" in result["body"]
