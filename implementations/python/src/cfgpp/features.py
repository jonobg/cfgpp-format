"""
Feature flags for AI-aware CFGPP capabilities
All features disabled by default to ensure zero production risk
"""


class FeatureFlags:
    """
    Feature flags for AI-aware capabilities

    CRITICAL: All features MUST default to False to maintain
    backwards compatibility with existing production system
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
