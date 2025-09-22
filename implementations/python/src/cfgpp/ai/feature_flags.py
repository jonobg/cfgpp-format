"""
Feature flags for AI-aware CFGPP capabilities
All features disabled by default to ensure zero production risk

# REASONING: Feature flags enable controlled AI feature rollout and production safety for feature workflows.
# Feature workflows require feature flags for controlled AI feature rollout and production safety in feature workflows.
# Feature flags support controlled AI feature rollout, production safety, and feature coordination while enabling
# comprehensive feature strategies and systematic AI feature workflows.
"""


class FeatureFlags:
    """
    Feature flags for AI-aware capabilities

    CRITICAL: All features MUST default to False to maintain
    backwards compatibility with existing production system

    Examples:
        >>> # Check if features are disabled by default
        >>> FeatureFlags.HIERARCHICAL_PARSING
        False
        >>> FeatureFlags.AI_REASONING_MODES
        False

        >>> # Enable features for development/testing
        >>> FeatureFlags.HIERARCHICAL_PARSING = True
        >>> FeatureFlags.is_enabled("HIERARCHICAL_PARSING")
        True

        >>> # Use in production with careful feature gating
        >>> if FeatureFlags.is_enabled("COMPRESSION"):
        ...     compressed = compressor.compress(config_text)
        ... else:
        ...     # Graceful fallback when disabled
        ...     compressed = config_text.encode('utf-8')
    """

    # Phase 1: Foundation features
    HIERARCHICAL_PARSING = False  # Hierarchical tree structure parsing
    HASH_VALIDATION = False  # Configuration integrity validation
    COMPRESSION = False  # Configuration compression

    # Phase 2: AI features (disabled until Phase 1 complete)
    AI_REASONING_MODES = False  # 5-level AI reasoning system
    AI_COMMUNICATION = False  # AI-to-AI transfer protocol

    @classmethod
    def is_enabled(cls, feature: str) -> bool:
        """Check if a feature is enabled"""
        return getattr(cls, feature, False)

    @classmethod
    def get_enabled_features(cls) -> list[str]:
        """Get list of currently enabled features"""
        enabled = []
        for attr in dir(cls):
            if not attr.startswith("_") and not callable(getattr(cls, attr)):
                if getattr(cls, attr) is True:
                    enabled.append(attr)
        return enabled
