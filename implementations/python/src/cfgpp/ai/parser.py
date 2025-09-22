"""
AI-aware parser interface for CFGPP
Extends existing parser with hierarchical and AI reasoning capabilities

# REASONING: AI-aware parser enables enhanced configuration understanding and reasoning capabilities for AI workflows.
# AI workflows require AI-aware parser for enhanced configuration understanding and reasoning capabilities in AI workflows.
# AI-aware parser supports enhanced configuration understanding, reasoning capabilities, and AI coordination while enabling
# comprehensive AI strategies and systematic configuration reasoning workflows.
"""

import logging
from typing import Dict, Set, Optional
from pathlib import Path

from ..core.parser import loads as original_loads, load as original_load
from .feature_flags import FeatureFlags
from .extensions.hierarchical import HierarchicalExtension, AIReasoningInterface


def loads_with_extensions(
    text: str, base_path: str = None, included_files: Set[Path] = None
) -> Dict:
    """
    Enhanced loads function with AI-aware extensions

    CRITICAL: Maintains 100% backwards compatibility
    - Uses original parser as foundation
    - All AI features disabled by default
    - Graceful degradation on any AI errors
    
    Returns original parser result PLUS optional AI enhancements:
    - '_hierarchical_view': Tree structure for AI reasoning
    - '_ai_interface': AI reasoning capabilities  
    - '_ai_capabilities': Metadata about available features
    
    Examples:
        >>> # Basic usage (acts like normal parser when AI disabled)
        >>> config = loads_with_extensions('App { name = "test" }')
        >>> config['body']['App']['body']['name']['value']['value']
        'test'
        
        >>> # Enable AI features
        >>> FeatureFlags.HIERARCHICAL_PARSING = True
        >>> config = loads_with_extensions('''
        ... DatabaseConfig::primary(
        ...     string host = "localhost",
        ...     int port = 5432
        ... )
        ... ''')
        >>> 
        >>> # Access hierarchical view
        >>> tree = config['_hierarchical_view']
        >>> tree.children['DatabaseConfig::primary'].children['host'].value
        'localhost'
        
        >>> # AI reasoning (when enabled)
        >>> FeatureFlags.AI_REASONING_MODES = True
        >>> explanation = explain_config(config)
        >>> print(explanation)  # Natural language explanation
    """
    # Always use original parser as foundation - NEVER modify this
    result = original_loads(text, base_path, included_files)

    # Only apply extensions if hierarchical parsing is enabled
    if not FeatureFlags.is_enabled("HIERARCHICAL_PARSING"):
        return result  # Return original result unchanged

    logger = logging.getLogger(__name__)

    try:
        # Apply hierarchical extension
        hierarchical_ext = HierarchicalExtension()
        enhanced_result = hierarchical_ext.process(result)

        # Add AI reasoning interface if both features are enabled
        if (
            FeatureFlags.is_enabled("AI_REASONING_MODES")
            and "_hierarchical_view" in enhanced_result
        ):
            ai_interface = AIReasoningInterface(enhanced_result["_hierarchical_view"])
            enhanced_result["_ai_interface"] = ai_interface

        return enhanced_result

    except Exception as e:
        logger.error(f"AI extensions failed: {e}")
        # Return original result on any extension error - graceful degradation
        return result


def load_with_extensions(file_path: str) -> Dict:
    """
    Enhanced load function with AI-aware extensions

    Maintains 100% backwards compatibility with original load function
    """
    # Always use original load as foundation
    result = original_load(file_path)

    # Only apply extensions if hierarchical parsing is enabled
    if not FeatureFlags.is_enabled("HIERARCHICAL_PARSING"):
        return result

    logger = logging.getLogger(__name__)

    try:
        # Apply hierarchical extension
        hierarchical_ext = HierarchicalExtension()
        enhanced_result = hierarchical_ext.process(result)

        # Add AI reasoning interface if enabled
        if (
            FeatureFlags.is_enabled("AI_REASONING_MODES")
            and "_hierarchical_view" in enhanced_result
        ):
            ai_interface = AIReasoningInterface(enhanced_result["_hierarchical_view"])
            enhanced_result["_ai_interface"] = ai_interface

        return enhanced_result

    except Exception as e:
        logger.error(f"AI extensions failed: {e}")
        # Return original result on any extension error
        return result


def explain_config(config_result: Dict) -> str:
    """
    Level 1 AI Reasoning: Explain configuration in natural language

    Args:
        config_result: Parser result (potentially with AI extensions)

    Returns:
        Natural language explanation of configuration structure
    """
    if not FeatureFlags.is_enabled("AI_REASONING_MODES"):
        return "AI reasoning modes are disabled"

    if "_ai_interface" in config_result:
        ai_interface = config_result["_ai_interface"]
        return ai_interface.explain_config_sequential()

    # Fallback explanation for standard parser results
    if "body" in config_result:
        item_count = len(config_result["body"])
        return f"Configuration contains {item_count} top-level items. Enable HIERARCHICAL_PARSING for detailed AI analysis."

    return "Unable to explain configuration structure"


def query_config(config_result: Dict, path: str) -> Optional[Dict]:
    """
    Level 2 AI Reasoning: Query configuration by path

    Args:
        config_result: Parser result with hierarchical view
        path: Full path to query (e.g., "root.DatabaseConfig.host")

    Returns:
        Node information if found, None otherwise
    """
    if not FeatureFlags.is_enabled("AI_REASONING_MODES"):
        return None

    if "_ai_interface" in config_result:
        ai_interface = config_result["_ai_interface"]
        return ai_interface.query_by_path(path)

    return None


# Backwards compatibility aliases
# These allow existing code to work unchanged while gaining AI capabilities when enabled
loads = loads_with_extensions
load = load_with_extensions
