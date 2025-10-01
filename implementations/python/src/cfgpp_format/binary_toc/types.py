"""
Core data types for Binary CFGPP TOC system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime


class CFGPPFormat(Enum):
    """CFGPP Format Types"""
    STANDARD = "CFG"      # Standard CFGPP (no TOC)
    BINARY_TOC = "CBT"    # Binary with Table of Contents
    SEQUENCE_INDEX = "CQI" # Sequence with distributed Index
    AI_HASH = "CAH"       # AI-optimized with Hash lookup
    BINARY_BTREE = "CBB"  # Binary with Btree structure


class SectionType(Enum):
    """Universal Section Type Registry (2-char codes)"""
    DATABASE = "DB"
    SECURITY = "SC" 
    LOGGING = "LG"
    METRICS = "MT"
    NETWORK = "NT"
    STORAGE = "ST"
    APPLICATION = "AP"
    USER_INTERFACE = "UI"
    ARTIFICIAL_INTELLIGENCE = "AI"
    INPUT_OUTPUT = "IO"
    SYSTEM = "SY"
    ENVIRONMENT = "EN"
    CACHE = "CF"
    QUEUE = "QU"
    WORKFLOW = "WF"
    AUDIT = "AU"
    BACKUP = "BK"
    CONTINUOUS_DEPLOYMENT = "CD"
    
    @classmethod
    def from_name(cls, name: str) -> 'SectionType':
        """Get section type from human-readable name"""
        name_mapping = {
            'database': cls.DATABASE,
            'security': cls.SECURITY,
            'logging': cls.LOGGING,
            'metrics': cls.METRICS,
            'network': cls.NETWORK,
            'storage': cls.STORAGE,
            'application': cls.APPLICATION,
            'ui': cls.USER_INTERFACE,
            'ai': cls.ARTIFICIAL_INTELLIGENCE,
            'io': cls.INPUT_OUTPUT,
            'system': cls.SYSTEM,
            'environment': cls.ENVIRONMENT,
            'cache': cls.CACHE,
            'queue': cls.QUEUE,
            'workflow': cls.WORKFLOW,
            'audit': cls.AUDIT,
            'backup': cls.BACKUP,
            'cd': cls.CONTINUOUS_DEPLOYMENT,
        }
        return name_mapping.get(name.lower(), cls.APPLICATION)


@dataclass
class MagicHeader:
    """4-Character Magic Header for format identification"""
    format_type: CFGPPFormat
    encoding: str = 'T'   # 'B'=Binary, 'T'=Text, 'C'=Compressed
    toc_type: str = 'T'   # 'T'=TOC, 'I'=Index, 'F'=Flat
    version: int = 1      # 1-9
    
    def to_string(self) -> str:
        """Convert to 4-character magic string"""
        return f"{self.format_type.value[0]}{self.encoding}{self.toc_type}{self.version}"
    
    @classmethod
    def from_string(cls, magic: str) -> 'MagicHeader':
        """Parse magic string into header"""
        if len(magic) < 4:
            raise ValueError(f"Invalid magic header: {magic}")
            
        # Determine format type from first character
        format_char = magic[0]
        format_mapping = {
            'C': CFGPPFormat.BINARY_TOC,  # CBT, CAH, etc.
            'B': CFGPPFormat.BINARY_BTREE,
            'Q': CFGPPFormat.SEQUENCE_INDEX,
        }
        
        format_type = format_mapping.get(format_char, CFGPPFormat.STANDARD)
        
        return cls(
            format_type=format_type,
            encoding=magic[1] if len(magic) > 1 else 'T',
            toc_type=magic[2] if len(magic) > 2 else 'T',
            version=int(magic[3]) if len(magic) > 3 else 1
        )


@dataclass
class SectionEntry:
    """TOC Section Entry with version-aware serialization"""
    section_type: SectionType
    offset: int
    size: int
    environment: str = "PROD"
    compression: Optional[str] = None
    hash_value: Optional[str] = None
    dependencies: Optional[List[SectionType]] = None
    
    def to_toc_line(self, version: int = 1) -> str:
        """Generate TOC line based on version"""
        if version == 1:
            return f"{self.section_type.value},{self.offset},{self.size},{self.environment}"
        elif version == 2:
            comp = self.compression or "NONE"
            hash_val = self.hash_value or "NONE"
            return f"{self.section_type.value},{self.offset},{self.size},{self.environment},{comp},{hash_val}"
        elif version == 3:
            comp = self.compression or "NONE"
            hash_val = self.hash_value or "NONE"
            deps = ":".join([d.value for d in self.dependencies]) if self.dependencies else "NONE"
            return f"{self.section_type.value},{self.offset},{self.size},{self.environment},{comp},{hash_val},{deps}"
        else:
            raise ValueError(f"Unsupported TOC version: {version}")
    
    @classmethod
    def from_toc_line(cls, line: str, version: int = 1) -> 'SectionEntry':
        """Parse TOC line based on version"""
        parts = line.strip().split(',')
        
        if len(parts) < 4:
            raise ValueError(f"Invalid TOC line: {line}")
        
        entry = cls(
            section_type=SectionType(parts[0]),
            offset=int(parts[1]),
            size=int(parts[2]),
            environment=parts[3]
        )
        
        if version >= 2 and len(parts) > 4:
            entry.compression = parts[4] if parts[4] != "NONE" else None
            if len(parts) > 5:
                entry.hash_value = parts[5] if parts[5] != "NONE" else None
            
        if version >= 3 and len(parts) > 6:
            deps_str = parts[6]
            if deps_str != "NONE":
                entry.dependencies = [SectionType(d) for d in deps_str.split(':')]
                
        return entry


@dataclass
class TableOfContents:
    """Complete TOC Structure"""
    magic_header: MagicHeader
    toc_size: int = 0
    section_count: int = 0
    created_timestamp: str = ""
    sections: List[SectionEntry] = field(default_factory=list)
    
    def __post_init__(self):
        """Auto-populate fields if not provided"""
        if not self.created_timestamp:
            self.created_timestamp = datetime.now().isoformat() + 'Z'
        if not self.section_count:
            self.section_count = len(self.sections)
    
    def generate_toc_text(self) -> str:
        """Generate complete TOC text block"""
        lines = [
            self.magic_header.to_string(),
            f"TOC-SIZE:{self.toc_size}",
            f"SECTIONS:{self.section_count}",
            f"CREATED:{self.created_timestamp}",
            f"---TOC-V{self.magic_header.version}-START---"
        ]
        
        for section in self.sections:
            lines.append(section.to_toc_line(self.magic_header.version))
            
        lines.extend([
            f"---TOC-V{self.magic_header.version}-END---",
            f"---CONTENT-V{self.magic_header.version}-START---"
        ])
        
        return '\n'.join(lines) + '\n'
    
    def get_section_registry(self) -> Dict[SectionType, int]:
        """Build section lookup registry for O(1) access"""
        return {section.section_type: section.offset for section in self.sections}


class CFGPPBinaryError(Exception):
    """Base exception for Binary CFGPP operations"""
    pass


class CorruptionDetectedError(CFGPPBinaryError):
    """Raised when file corruption is detected"""
    pass


class UnsupportedVersionError(CFGPPBinaryError):
    """Raised when unsupported version is encountered"""
    pass