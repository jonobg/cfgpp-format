"""
Tests for the cfgpp parser.
"""

import os
from cfgpp.parser import loads, load


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


def test_parse_example_file():
    """Test parsing the example configuration file."""
    import pytest

    pytest.skip("Skipping example file test until core functionality is complete")

    example_path = os.path.join(os.path.dirname(__file__), "..", "AppConfig.cfgpp")

    # Parse the example file
    result = load(example_path)

    # Basic structure checks
    assert "body" in result

    # Check for expected top-level keys
    expected_keys = ["Logging", "Server", "Database", "Cache", "Security", "Features"]
    for key in expected_keys:
        assert key in result["body"], f"Expected key '{key}' not found in result"

    # Check Logging configuration
    logging = result["body"]["Logging"]
    assert "level" in logging
    assert logging["level"]["value"] == "INFO"

    # Check Server configuration
    server = result["body"]["Server"]
    assert "port" in server
    assert server["port"]["value"] == 8080
    assert "environment" in server
    assert server["environment"]["value"] == "development"

    # Check for UserConfig
    assert "userConf" in result["body"]
    user_config = result["body"]["userConf"]
    assert "users" in user_config["parameters"]
    assert user_config["parameters"]["users"]["is_array"] is True

    # Check that we have some nested objects in the body
    assert "body" in result
    assert isinstance(result["body"], dict)
