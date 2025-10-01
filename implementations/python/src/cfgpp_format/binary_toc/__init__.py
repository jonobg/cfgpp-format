"""
Binary TOC (Table of Contents) implementation for CFGPP.

This module provides encoding/decoding capabilities for the revolutionary
Binary CFGPP format with filesystem-style Table of Contents for O(1) section access.
"""

from .encoder import CFGPPBinaryEncoder
from .decoder import CFGPPBinaryDecoder
from .types import MagicHeader, SectionType, SectionEntry, TableOfContents
from .validator import CFGPPBinaryValidator

__all__ = [
    'CFGPPBinaryEncoder',
    'CFGPPBinaryDecoder', 
    'CFGPPBinaryValidator',
    'MagicHeader',
    'SectionType',
    'SectionEntry',
    'TableOfContents'
]