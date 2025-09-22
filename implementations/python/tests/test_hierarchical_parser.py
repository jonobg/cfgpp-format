"""Test hierarchical parser extension"""

import pytest
from cfgpp.ai.extensions.hierarchical import (
    HierarchicalNode,
    HierarchicalExtension,
    AIReasoningInterface,
)
from cfgpp.ai.feature_flags import FeatureFlags


def test_hierarchical_node_creation():
    """Test basic hierarchical node functionality"""
    # Test root node
    root = HierarchicalNode("root", "object")
    assert root.name == "root"
    assert root.node_type == "object"
    assert root.value is None
    assert root.parent is None
    assert root.full_path == "root"
    assert len(root.children) == 0

    # Test child node
    child = HierarchicalNode("config", "object")
    root.add_child(child)

    assert child.parent == root
    assert child.full_path == "root.config"
    assert len(root.children) == 1
    assert root.children["config"] == child


def test_hierarchical_node_path_calculation():
    """Test full path calculation for nested nodes"""
    root = HierarchicalNode("root", "object")
    config = HierarchicalNode("AppConfig", "object")
    database = HierarchicalNode("database", "object")
    host = HierarchicalNode("host", "property", "localhost")

    root.add_child(config)
    config.add_child(database)
    database.add_child(host)

    assert root.full_path == "root"
    assert config.full_path == "root.AppConfig"
    assert database.full_path == "root.AppConfig.database"
    assert host.full_path == "root.AppConfig.database.host"


def test_hierarchical_node_tree_operations():
    """Test tree traversal and search operations"""
    root = HierarchicalNode("root", "object")

    # Create test tree
    app_config = HierarchicalNode("AppConfig", "object")
    name_prop = HierarchicalNode("name", "property", "test-app")
    port_prop = HierarchicalNode("port", "property", 8080)

    db_config = HierarchicalNode("DatabaseConfig", "object")
    host_param = HierarchicalNode("host", "parameter", "localhost")

    root.add_child(app_config)
    root.add_child(db_config)
    app_config.add_child(name_prop)
    app_config.add_child(port_prop)
    db_config.add_child(host_param)

    # Test get_node by path
    found_name = root.get_node("root.AppConfig.name")
    assert found_name is not None
    assert found_name.value == "test-app"

    found_host = root.get_node("root.DatabaseConfig.host")
    assert found_host is not None
    assert found_host.value == "localhost"

    # Test non-existent path
    not_found = root.get_node("root.NonExistent.path")
    assert not_found is None

    # Test list_children
    root_children = root.list_children()
    assert len(root_children) == 2
    child_names = [child.name for child in root_children]
    assert "AppConfig" in child_names
    assert "DatabaseConfig" in child_names

    # Test find_nodes_by_type
    properties = root.find_nodes_by_type("property")
    assert len(properties) == 2

    parameters = root.find_nodes_by_type("parameter")
    assert len(parameters) == 1
    assert parameters[0].name == "host"


def test_hierarchical_node_to_dict():
    """Test conversion to dictionary for AI communication"""
    root = HierarchicalNode("config", "object")
    prop = HierarchicalNode("name", "property", "test")
    root.add_child(prop)

    root_dict = root.to_dict()
    assert root_dict["name"] == "config"
    assert root_dict["type"] == "object"
    assert root_dict["path"] == "config"
    assert "children" in root_dict
    assert "name" in root_dict["children"]

    prop_dict = root_dict["children"]["name"]
    assert prop_dict["name"] == "name"
    assert prop_dict["type"] == "property"
    assert prop_dict["value"] == "test"
    assert prop_dict["path"] == "config.name"


def test_hierarchical_extension_disabled():
    """Test hierarchical extension when feature is disabled"""
    extension = HierarchicalExtension()
    assert not extension.enabled

    # Should pass through original result unchanged
    original_result = {"body": {"test": "data"}}
    processed = extension.process(original_result)

    assert processed == original_result
    assert "_hierarchical_view" not in processed


def test_hierarchical_extension_enabled():
    """Test hierarchical extension when feature is enabled"""
    original_value = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        extension = HierarchicalExtension()
        assert extension.enabled

        # Mock AST result similar to actual parser output
        ast_result = {
            "body": {
                "AppConfig": {
                    "name": "AppConfig",
                    "body": {
                        "name": {"value": {"type": "string", "value": "test-app"}},
                        "port": {"value": {"type": "integer", "value": 8080}},
                    },
                }
            }
        }

        processed = extension.process(ast_result)

        # Should have hierarchical view added
        assert "_hierarchical_view" in processed
        assert "_ai_capabilities" in processed

        tree = processed["_hierarchical_view"]
        assert tree.name == "root"
        assert len(tree.children) == 1
        assert "AppConfig" in tree.children

        app_config = tree.children["AppConfig"]
        assert len(app_config.children) == 2
        assert "name" in app_config.children
        assert "port" in app_config.children

        # Test properties were processed correctly
        name_node = app_config.children["name"]
        assert name_node.node_type == "property"
        assert name_node.value == "test-app"

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_value


def test_hierarchical_extension_error_handling():
    """Test error handling in hierarchical extension"""
    original_value = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        extension = HierarchicalExtension()

        # Test with malformed AST
        malformed_ast = {"invalid": "structure"}
        processed = extension.process(malformed_ast)

        # Should return original structure with or without AI capabilities
        assert "invalid" in processed
        assert processed["invalid"] == "structure"
        # May have AI capabilities added even for malformed AST

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_value


def test_ai_reasoning_interface_disabled():
    """Test AI reasoning interface when disabled"""
    interface = AIReasoningInterface()
    assert not interface.enabled

    explanation = interface.explain_config_sequential()
    assert "AI reasoning disabled" in explanation


def test_ai_reasoning_interface_enabled():
    """Test AI reasoning interface when enabled"""
    original_value = FeatureFlags.AI_REASONING_MODES
    FeatureFlags.AI_REASONING_MODES = True

    try:
        # Create test hierarchical tree
        root = HierarchicalNode("root", "object")
        config = HierarchicalNode("AppConfig", "object")
        name_prop = HierarchicalNode("name", "property", "test-app")

        root.add_child(config)
        config.add_child(name_prop)

        interface = AIReasoningInterface(root)
        assert interface.enabled

        # Test sequential explanation
        explanation = interface.explain_config_sequential()
        assert len(explanation) > 50
        assert "Configuration Structure Analysis" in explanation
        assert "Sequential Mode" in explanation
        assert "AppConfig" in explanation

        # Test path querying
        result = interface.query_by_path("root.AppConfig.name")
        assert result is not None
        assert result["value"] == "test-app"

        # Test non-existent path
        result = interface.query_by_path("root.NonExistent")
        assert result is None

    finally:
        FeatureFlags.AI_REASONING_MODES = original_value


def test_typed_object_processing():
    """Test processing of typed objects with parameters"""
    original_value = FeatureFlags.HIERARCHICAL_PARSING
    FeatureFlags.HIERARCHICAL_PARSING = True

    try:
        extension = HierarchicalExtension()

        # Mock AST for typed object (DatabaseConfig::primary)
        ast_result = {
            "body": {
                "DatabaseConfig::primary": {
                    "name": "DatabaseConfig::primary",
                    "params": {
                        "host": {
                            "type": "string",
                            "value": {"type": "string", "value": "localhost"},
                        },
                        "port": {
                            "type": "int",
                            "value": {"type": "integer", "value": 5432},
                        },
                    },
                    "body": {},
                }
            }
        }

        processed = extension.process(ast_result)
        tree = processed["_hierarchical_view"]

        db_config = tree.children["DatabaseConfig::primary"]
        assert len(db_config.children) == 2

        # Test parameters were processed correctly
        host_param = db_config.children["host"]
        assert host_param.node_type == "parameter"
        assert host_param.value == "localhost"

        port_param = db_config.children["port"]
        assert port_param.node_type == "parameter"
        assert port_param.value == 5432

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_value


def test_feature_flag_integration():
    """Test integration with feature flag system"""
    # Test hierarchical extension respects flags
    assert not FeatureFlags.HIERARCHICAL_PARSING
    extension = HierarchicalExtension()
    assert not extension.enabled

    # Test AI reasoning respects flags
    assert not FeatureFlags.AI_REASONING_MODES
    interface = AIReasoningInterface()
    assert not interface.enabled


def test_production_safety():
    """Test production safety of hierarchical components"""
    original_hierarchical = FeatureFlags.HIERARCHICAL_PARSING
    original_reasoning = FeatureFlags.AI_REASONING_MODES

    FeatureFlags.HIERARCHICAL_PARSING = True
    FeatureFlags.AI_REASONING_MODES = True

    try:
        extension = HierarchicalExtension()

        # Test with various edge cases - should not crash
        edge_cases = [
            {},  # Empty AST
            {"body": {}},  # Empty body
            {"body": None},  # None body
            {"body": {"invalid": None}},  # Invalid object data
        ]

        for ast in edge_cases:
            try:
                result = extension.process(ast)
                # Should always return a dict
                assert isinstance(result, dict)
            except Exception as e:
                # Some errors are acceptable, crashes are not
                assert isinstance(e, (KeyError, TypeError, AttributeError))

        # Test AI reasoning with edge cases
        interface = AIReasoningInterface(None)
        explanation = interface.explain_config_sequential()
        assert isinstance(explanation, str)

    finally:
        FeatureFlags.HIERARCHICAL_PARSING = original_hierarchical
        FeatureFlags.AI_REASONING_MODES = original_reasoning
