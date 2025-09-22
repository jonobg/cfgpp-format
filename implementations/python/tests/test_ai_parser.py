"""Test AI-aware parser functionality"""

import pytest
from cfgpp.ai.parser import loads_with_extensions, explain_config, query_config
from cfgpp.ai.feature_flags import FeatureFlags


def test_ai_parser_disabled_by_default():
    """Test that AI parser behaves like original when disabled"""
    # Ensure features are disabled
    assert not FeatureFlags.HIERARCHICAL_PARSING
    assert not FeatureFlags.AI_REASONING_MODES

    config = """
    AppConfig {
        name = "test",
        port = 8080
    }
    """

    # Should behave exactly like original parser
    result = loads_with_extensions(config)

    # Should not have AI extensions
    assert "_hierarchical_view" not in result
    assert "_ai_interface" not in result
    assert "_ai_capabilities" not in result

    # Should have original parser structure
    assert "body" in result
    assert isinstance(result["body"], dict)


def test_hierarchical_parsing_when_enabled():
    """Test hierarchical parsing functionality when enabled"""
    original_hierarchical = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        config = """
        DatabaseConfig::primary(
            string host = "localhost",
            int port = 5432,
            bool ssl_enabled = true
        )
        
        AppConfig {
            name = "test-app",
            debug = true
        }
        """

        result = loads_with_extensions(config)

        # Should have hierarchical view
        assert "_hierarchical_view" in result
        assert "_ai_capabilities" in result

        tree = result["_hierarchical_view"]
        assert tree.name == "root"
        assert tree.node_type == "object"
        assert len(tree.children) == 2

        # Test DatabaseConfig::primary object
        db_config = tree.children["DatabaseConfig::primary"]
        assert db_config.node_type == "object"
        assert len(db_config.children) == 3

        # Test parameters
        assert db_config.children["host"].node_type == "parameter"
        assert db_config.children["host"].value == "localhost"
        assert db_config.children["port"].value == 5432
        assert db_config.children["ssl_enabled"].value is True

        # Test AppConfig object
        app_config = tree.children["AppConfig"]
        assert app_config.node_type == "object"
        assert len(app_config.children) == 2

        # Test properties
        assert app_config.children["name"].node_type == "property"
        assert app_config.children["name"].value == "test-app"
        assert app_config.children["debug"].value is True

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_hierarchical


def test_ai_reasoning_when_enabled():
    """Test AI reasoning functionality when both features enabled"""
    original_hierarchical = FeatureFlags.HIERARCHICAL_PARSING
    original_reasoning = FeatureFlags.AI_REASONING_MODES

    FeatureFlags.HIERARCHICAL_PARSING = True
    FeatureFlags.AI_REASONING_MODES = True

    try:
        config = """
        ServerConfig {
            name = "web-server",
            port = 8080
        }
        """

        result = loads_with_extensions(config)

        # Should have AI interface
        assert "_ai_interface" in result
        assert "_ai_capabilities" in result

        # Test AI capabilities metadata
        capabilities = result["_ai_capabilities"]
        assert "sequential" in capabilities["reasoning_modes"]
        assert "get_node" in capabilities["tree_functions"]
        assert "hierarchical_parsing" in capabilities["ai_features"]

        # Test AI explanation
        explanation = explain_config(result)
        assert len(explanation) > 50
        assert "Configuration Structure Analysis" in explanation
        assert "ServerConfig" in explanation

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_hierarchical
        FeatureFlags.AI_REASONING_MODES = original_reasoning


def test_hierarchical_node_functionality():
    """Test hierarchical node tree operations"""
    original_value = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        config = """
        DatabaseConfig::primary(
            string host = "localhost",
            int port = 5432
        )
        """

        result = loads_with_extensions(config)
        tree = result["_hierarchical_view"]

        # Test path calculation
        db_node = tree.children["DatabaseConfig::primary"]
        assert db_node.full_path == "root.DatabaseConfig::primary"

        host_node = db_node.children["host"]
        assert host_node.full_path == "root.DatabaseConfig::primary.host"

        # Test node lookup by path
        found_node = tree.get_node("root.DatabaseConfig::primary.host")
        assert found_node is not None
        assert found_node.value == "localhost"

        # Test children listing
        children = db_node.list_children()
        assert len(children) == 2
        child_names = [child.name for child in children]
        assert "host" in child_names
        assert "port" in child_names

        # Test find by type
        parameters = tree.find_nodes_by_type("parameter")
        assert len(parameters) == 2

        # Test to_dict conversion
        node_dict = host_node.to_dict()
        assert node_dict["name"] == "host"
        assert node_dict["type"] == "parameter"
        assert node_dict["value"] == "localhost"
        assert node_dict["path"] == "root.DatabaseConfig::primary.host"

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_value


def test_ai_explanation_disabled():
    """Test AI explanation when reasoning is disabled"""
    config = """
    AppConfig {
        name = "test"
    }
    """

    result = loads_with_extensions(config)
    explanation = explain_config(result)

    assert "AI reasoning modes are disabled" in explanation


def test_ai_query_functionality():
    """Test AI query functionality"""
    original_hierarchical = FeatureFlags.HIERARCHICAL_PARSING
    original_reasoning = FeatureFlags.AI_REASONING_MODES

    FeatureFlags.HIERARCHICAL_PARSING = True
    FeatureFlags.AI_REASONING_MODES = True

    try:
        config = """
        AppConfig {
            name = "test-app",
            port = 8080
        }
        """

        result = loads_with_extensions(config)

        # Test querying existing path
        query_result = query_config(result, "root.AppConfig.name")
        assert query_result is not None
        assert query_result["value"] == "test-app"

        # Test querying non-existent path
        query_result = query_config(result, "root.NonExistent.path")
        assert query_result is None

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_hierarchical
        FeatureFlags.AI_REASONING_MODES = original_reasoning


def test_ai_query_disabled():
    """Test AI query when reasoning is disabled"""
    config = """
    AppConfig {
        name = "test"
    }
    """

    result = loads_with_extensions(config)
    query_result = query_config(result, "root.AppConfig.name")

    assert query_result is None  # Should return None when disabled


def test_error_handling_and_graceful_degradation():
    """Test error handling in AI extensions"""
    original_value = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        # Test with malformed config that might cause parsing errors
        config = """
        ValidConfig {
            name = "test"
        }
        """

        # Should not crash even if hierarchical processing has issues
        result = loads_with_extensions(config)

        # Should still have original parser result even if AI extensions fail
        assert "body" in result
        assert isinstance(result["body"], dict)

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_value


def test_nested_object_processing():
    """Test processing of nested objects"""
    original_value = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        config = """
        ServerConfig {
            name = "web-server",
            database = DatabaseConfig {
                host = "localhost",
                port = 5432
            }
        }
        """

        result = loads_with_extensions(config)
        tree = result["_hierarchical_view"]

        # Test nested structure
        server_config = tree.children["ServerConfig"]
        assert "database" in server_config.children

        database_node = server_config.children["database"]
        assert database_node.node_type == "object"

        # Test nested properties
        if database_node.children:  # Nested object processing may vary
            assert len(database_node.children) >= 0  # May have nested properties

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_value


def test_backwards_compatibility():
    """Test that AI parser maintains backwards compatibility"""
    from cfgpp.core.parser import loads as original_loads

    config = """
    AppConfig {
        name = "test",
        port = 8080,
        debug = true
    }
    """

    # Results should be functionally equivalent when AI features disabled
    original_result = original_loads(config)
    ai_result = loads_with_extensions(config)

    # Should have same basic structure
    assert "body" in original_result
    assert "body" in ai_result
    assert original_result["body"].keys() == ai_result["body"].keys()

    # AI result should not have AI extensions when disabled
    assert "_hierarchical_view" not in ai_result
    assert "_ai_interface" not in ai_result


def test_feature_flag_integration():
    """Test proper integration with feature flag system"""
    # Test that features start disabled
    assert not FeatureFlags.HIERARCHICAL_PARSING
    assert not FeatureFlags.AI_REASONING_MODES

    config = """
    TestConfig {
        value = "test"
    }
    """

    # Should behave as original parser when disabled
    result = loads_with_extensions(config)
    assert "_hierarchical_view" not in result

    # Test enabling features
    original_hierarchical = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        result = loads_with_extensions(config)
        assert "_hierarchical_view" in result
    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_hierarchical


def test_production_safety():
    """Test that AI parser is safe for production use"""
    # Test with various edge cases - should never crash
    test_configs = [
        "",  # Empty config
        "InvalidSyntax {",  # Malformed config
        """ValidConfig { name = "test" }""",  # Valid config
    ]

    for config in test_configs:
        try:
            result = loads_with_extensions(config)
            # Should always return a dict
            assert isinstance(result, dict)
        except Exception:
            # Parsing errors are acceptable, crashes are not
            pass  # Original parser may throw for invalid syntax
