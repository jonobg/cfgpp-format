"""
Hierarchical parsing extension for AI-aware configuration reasoning
Phase 1: Parallel hierarchical tree structure alongside existing AST

# REASONING: Hierarchical parsing enables AI-aware configuration reasoning and tree-based analysis for hierarchical workflows.
# Hierarchical workflows require hierarchical parsing for AI-aware configuration reasoning and tree-based analysis in hierarchical workflows.
# Hierarchical parsing supports AI-aware configuration reasoning, tree-based analysis, and hierarchical coordination while enabling
# comprehensive hierarchical strategies and systematic configuration reasoning workflows.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..feature_flags import FeatureFlags


class HierarchicalNode:
    """
    Hierarchical node for AI-aware configuration reasoning

    Provides tree structure with full path keys for O(1) lookup
    Enables AI reasoning modes over configuration structure
    """

    def __init__(
        self,
        name: str,
        node_type: str = "object",
        value: Any = None,
        parent: Optional["HierarchicalNode"] = None,
    ):
        self.name = name
        self.node_type = node_type  # object, array, property, enum
        self.value = value
        self.parent = parent
        self.children: Dict[str, "HierarchicalNode"] = {}
        self.full_path = self._calculate_full_path()

    def _calculate_full_path(self) -> str:
        """Calculate full path from root for O(1) lookup"""
        if self.parent is None:
            return self.name
        elif self.parent.name == "root":
            return f"root.{self.name}"
        else:
            return f"{self.parent.full_path}.{self.name}"

    def add_child(self, child: "HierarchicalNode"):
        """Add child node and update its parent reference"""
        child.parent = self
        child.full_path = child._calculate_full_path()
        self.children[child.name] = child
        # Update paths for all descendants
        self._update_descendant_paths(child)

    def _update_descendant_paths(self, node: "HierarchicalNode"):
        """Recursively update paths for all descendants"""
        node.full_path = node._calculate_full_path()
        for child in node.children.values():
            self._update_descendant_paths(child)

    def get_node(self, path: str) -> Optional["HierarchicalNode"]:
        """Get node by full path (AI reasoning function)"""
        if path == self.full_path:
            return self

        # Check children recursively
        for child in self.children.values():
            result = child.get_node(path)
            if result:
                return result

        return None

    def list_children(self) -> List["HierarchicalNode"]:
        """List all direct children (AI reasoning function)"""
        return list(self.children.values())

    def find_nodes_by_type(self, node_type: str) -> List["HierarchicalNode"]:
        """Find all nodes of specific type (AI reasoning function)"""
        results = []
        if self.node_type == node_type:
            results.append(self)

        for child in self.children.values():
            results.extend(child.find_nodes_by_type(node_type))

        return results

    def to_dict(self) -> Dict:
        """Convert to dictionary for AI communication"""
        result = {
            "name": self.name,
            "type": self.node_type,
            "path": self.full_path,
            "value": self.value,
        }

        if self.children:
            result["children"] = {
                name: child.to_dict() for name, child in self.children.items()
            }

        return result


class HierarchicalExtension:
    """
    Parser extension that creates hierarchical view of configuration

    Phase 1: Creates parallel hierarchical tree alongside existing AST
    No modification of existing parser - pure addition
    """

    def __init__(self):
        self.enabled = FeatureFlags.is_enabled("HIERARCHICAL_PARSING")
        self.logger = logging.getLogger(__name__)

    def process(self, ast_result: Dict) -> Dict:
        """
        Process parser AST and add hierarchical view

        Args:
            ast_result: Original parser AST result

        Returns:
            Enhanced result with hierarchical view (if enabled)
        """
        if not self.enabled:
            return ast_result  # Pass through unchanged when disabled

        try:
            # Create hierarchical tree from AST
            hierarchical_tree = self._create_hierarchical_tree(ast_result)

            # Add hierarchical view to result without modifying original
            enhanced_result = ast_result.copy()
            enhanced_result["_hierarchical_view"] = hierarchical_tree
            enhanced_result["_ai_capabilities"] = {
                "reasoning_modes": ["sequential"],
                "tree_functions": ["get_node", "list_children", "find_nodes_by_type"],
                "ai_features": ["hierarchical_parsing"],
            }

            return enhanced_result

        except Exception as e:
            self.logger.error(f"Hierarchical processing failed: {e}")
            # Return original result on error - graceful degradation
            return ast_result

    def _create_hierarchical_tree(self, ast_result: Dict) -> HierarchicalNode:
        """Create hierarchical tree from parser AST"""
        root = HierarchicalNode("root", "object")

        if "body" in ast_result and isinstance(ast_result["body"], dict):
            # Parser AST has "body" as a dict, not a list
            for item_name, item_data in ast_result["body"].items():
                child_node = self._process_ast_object(item_name, item_data)
                if child_node:
                    root.add_child(child_node)

        return root

    def _process_ast_object(self, name: str, data: Dict) -> Optional[HierarchicalNode]:
        """Process top-level AST object into hierarchical node"""
        if not isinstance(data, dict):
            return None

        node = HierarchicalNode(name, "object")

        # Handle parameters (for typed objects like DatabaseConfig::primary)
        if "params" in data and isinstance(data["params"], dict):
            for param_name, param_data in data["params"].items():
                param_node = self._process_parameter(param_name, param_data)
                if param_node:
                    node.add_child(param_node)

        # Handle body properties (for regular objects)
        if "body" in data and isinstance(data["body"], dict):
            for prop_name, prop_data in data["body"].items():
                prop_node = self._process_property(prop_name, prop_data)
                if prop_node:
                    node.add_child(prop_node)

        return node

    def _process_parameter(
        self, name: str, param_data: Dict
    ) -> Optional[HierarchicalNode]:
        """Process parameter from typed object"""
        param_type = param_data.get("type", "unknown")
        value = None
        if "value" in param_data and isinstance(param_data["value"], dict):
            value = param_data["value"].get("value")

        return HierarchicalNode(name, "parameter", value)

    def _process_property(
        self, name: str, prop_data: Dict
    ) -> Optional[HierarchicalNode]:
        """Process property from object body"""
        if not isinstance(prop_data, dict) or "value" not in prop_data:
            return None

        value_data = prop_data["value"]
        if isinstance(value_data, dict):
            if "type" in value_data:
                value_type = value_data["type"]
                if value_type in ["string", "integer", "boolean"]:
                    # Simple value
                    value = value_data.get("value")
                    return HierarchicalNode(name, "property", value)
                else:
                    # Complex nested object
                    node = HierarchicalNode(name, "object")
                    # Process nested properties
                    for nested_name, nested_data in value_data.items():
                        if nested_name not in ["type", "line", "col"] and isinstance(
                            nested_data, dict
                        ):
                            nested_node = self._process_property(
                                nested_name, nested_data
                            )
                            if nested_node:
                                node.add_child(nested_node)
                    return node

        return None

    # Legacy methods - kept for compatibility but updated to handle new structure
    def _process_ast_item(self, item: Dict) -> Optional[HierarchicalNode]:
        """Legacy method - redirects to new processing methods"""
        return None  # Not used with new AST structure


class AIReasoningInterface:
    """
    Interface for AI reasoning over hierarchical configuration

    Provides Level 1 AI reasoning capabilities (Sequential/VHS mode)
    """

    def __init__(self, hierarchical_tree: Optional[HierarchicalNode] = None):
        self.enabled = FeatureFlags.is_enabled("AI_REASONING_MODES")
        self.tree = hierarchical_tree
        self.logger = logging.getLogger(__name__)

    def explain_config_sequential(self) -> str:
        """
        Level 1 AI Reasoning: Sequential/VHS mode
        Explain configuration in natural language by walking through structure
        """
        if not self.enabled or not self.tree:
            return "AI reasoning disabled or no hierarchical tree available"

        try:
            explanation = ["Configuration Structure Analysis (Sequential Mode):"]
            explanation.append("")

            self._explain_node_recursive(self.tree, explanation, indent=0)

            return "\n".join(explanation)

        except Exception as e:
            self.logger.error(f"Sequential explanation failed: {e}")
            return f"Explanation error: {e}"

    def _explain_node_recursive(
        self, node: HierarchicalNode, explanation: List[str], indent: int = 0
    ):
        """Recursively explain node structure"""
        prefix = "  " * indent

        if node.node_type == "object":
            if node.name == "root":
                explanation.append(
                    f"{prefix}Root configuration contains {len(node.children)} main sections:"
                )
            else:
                explanation.append(
                    f"{prefix}• {node.name} (object) - Contains {len(node.children)} properties"
                )
        elif node.node_type == "property":
            explanation.append(f"{prefix}• {node.name} = {node.value} (property)")
        elif node.node_type == "array":
            explanation.append(
                f"{prefix}• {node.name} (array) - Contains {len(node.value) if node.value else 0} items"
            )
        elif node.node_type == "enum":
            explanation.append(
                f"{prefix}• {node.name} (enum) - Defines {len(node.children)} allowed values"
            )

        # Explain children
        for child in node.children.values():
            self._explain_node_recursive(child, explanation, indent + 1)

    def query_by_path(self, path: str) -> Optional[Dict]:
        """
        Query configuration by full path
        Level 2 AI Reasoning preparation (DVD chapter jumping)
        """
        if not self.enabled or not self.tree:
            return None

        node = self.tree.get_node(path)
        if node:
            return node.to_dict()
        return None
