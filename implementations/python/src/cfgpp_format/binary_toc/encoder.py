"""
Binary CFGPP Encoder - Convert standard CFGPP to Binary TOC format.
"""

import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .types import (
    MagicHeader, SectionEntry, TableOfContents, 
    CFGPPFormat, SectionType, CFGPPBinaryError
)


class CFGPPBinaryEncoder:
    """Encode standard CFGPP files into Binary TOC format"""
    
    def __init__(self, version: int = 1):
        self.version = version
        self.sections: List[Tuple[SectionType, str]] = []
        
    def add_section_from_content(self, content: str, section_type: Optional[SectionType] = None) -> SectionType:
        """
        Add a section from CFGPP content, auto-detecting section type if not provided
        """
        if section_type is None:
            section_type = self._detect_section_type(content)
            
        self.sections.append((section_type, content))
        return section_type
    
    def add_section(self, section_type: SectionType, content: str):
        """Add a section with explicit type"""
        self.sections.append((section_type, content))
    
    def _detect_section_type(self, content: str) -> SectionType:
        """
        Auto-detect section type from CFGPP content based on naming patterns
        """
        content_lower = content.lower()
        
        # Look for common patterns in the content
        if any(keyword in content_lower for keyword in ['database', 'db', 'connection', 'pool']):
            return SectionType.DATABASE
        elif any(keyword in content_lower for keyword in ['security', 'auth', 'jwt', 'ssl', 'tls']):
            return SectionType.SECURITY
        elif any(keyword in content_lower for keyword in ['log', 'logging', 'logger']):
            return SectionType.LOGGING
        elif any(keyword in content_lower for keyword in ['metric', 'monitor', 'stats']):
            return SectionType.METRICS
        elif any(keyword in content_lower for keyword in ['network', 'host', 'port', 'url']):
            return SectionType.NETWORK
        elif any(keyword in content_lower for keyword in ['storage', 'disk', 'file', 'path']):
            return SectionType.STORAGE
        elif any(keyword in content_lower for keyword in ['cache', 'redis', 'memcache']):
            return SectionType.CACHE
        elif any(keyword in content_lower for keyword in ['queue', 'message', 'kafka', 'rabbitmq']):
            return SectionType.QUEUE
        elif any(keyword in content_lower for keyword in ['env', 'environment', 'var']):
            return SectionType.ENVIRONMENT
        else:
            return SectionType.APPLICATION  # Default fallback
    
    def encode_file(self, input_path: str, output_path: str, environment: str = "PROD") -> TableOfContents:
        """
        Encode a standard CFGPP file into Binary TOC format
        """
        # Read and parse the input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into logical sections
        sections = self._split_into_sections(content)
        
        # If no sections found, treat entire content as one APPLICATION section
        if not sections:
            sections = [content]
        
        # Add sections to encoder
        for section_content in sections:
            self.add_section_from_content(section_content)
        
        # Generate the binary TOC file
        return self.generate_file(output_path, environment)
    
    def _split_into_sections(self, content: str) -> List[str]:
        """
        Split CFGPP content into logical sections based on top-level constructs
        """
        sections = []
        current_section = []
        
        lines = content.split('\n')
        in_construct = False
        brace_depth = 0
        paren_depth = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and comments at top level
            if not stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('@'):
                if not in_construct:
                    continue
                else:
                    current_section.append(line)
                    continue
            
            # Detect start of new construct
            # Pattern 1: Constructor syntax (DatabaseConfig::production)
            # Pattern 2: Object syntax (AppConfig {)
            # Pattern 3: Function syntax (function_name()
            is_new_construct = (
                '::' in line or 
                ('{' in line and not in_construct) or
                (line.endswith('(') and not in_construct)
            )
            
            if is_new_construct:
                # If we have accumulated content, save it as a section
                if current_section and not in_construct:
                    sections.append('\n'.join(current_section))
                    current_section = []
                
                in_construct = True
                brace_depth = 0
                paren_depth = 0
            
            if in_construct:
                current_section.append(line)
                
                # Track brace and parentheses depth to know when construct ends
                brace_depth += line.count('{') - line.count('}')
                paren_depth += line.count('(') - line.count(')')
                
                # Construct ends when both braces and parentheses are balanced
                if brace_depth <= 0 and paren_depth <= 0 and ('{' in line or '}' in line or '(' in line or ')' in line):
                    # Construct ended
                    sections.append('\n'.join(current_section))
                    current_section = []
                    in_construct = False
            else:
                # Handle single-line constructs or assignments
                if stripped and not stripped.startswith('//'):
                    sections.append(line)
        
        # Add any remaining content
        if current_section:
            sections.append('\n'.join(current_section))
        
        return [s.strip() for s in sections if s.strip()]
    
    def generate_file(self, filepath: str, environment: str = "PROD") -> TableOfContents:
        """
        Generate complete Binary TOC file
        """
        if not self.sections:
            raise CFGPPBinaryError("No sections to encode")
        
        # Calculate section offsets and sizes
        toc_entries = self._calculate_section_layout(environment)
        
        # Generate TOC structure
        toc = self._generate_toc(toc_entries)
        
        # Write complete file
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write TOC header
            f.write(toc.generate_toc_text())
            
            # Write sections with landmarks
            for section_type, content in self.sections:
                f.write(f"---{section_type.value}-START---\n")
                f.write(content)
                if not content.endswith('\n'):
                    f.write('\n')
                f.write(f"---{section_type.value}-END---\n\n")
        
        return toc
    
    def _calculate_section_layout(self, environment: str) -> List[SectionEntry]:
        """
        Calculate offsets and sizes for all sections
        """
        entries = []
        
        # Generate TOC first to estimate its size
        temp_toc = self._generate_toc([])
        toc_text = temp_toc.generate_toc_text()
        
        # Start content after TOC
        current_offset = len(toc_text.encode('utf-8'))
        
        for section_type, content in self.sections:
            # Calculate section size including landmarks
            start_marker = f"---{section_type.value}-START---\n"
            end_marker = f"---{section_type.value}-END---\n\n"
            
            section_size = (
                len(start_marker.encode('utf-8')) +
                len(content.encode('utf-8')) +
                (0 if content.endswith('\n') else 1) +  # Add newline if needed
                len(end_marker.encode('utf-8'))
            )
            
            entries.append(SectionEntry(
                section_type=section_type,
                offset=current_offset,
                size=section_size,
                environment=environment
            ))
            
            current_offset += section_size
        
        return entries
    
    def _generate_toc(self, entries: List[SectionEntry]) -> TableOfContents:
        """
        Generate TOC structure
        """
        magic_header = MagicHeader(
            format_type=CFGPPFormat.BINARY_TOC,
            encoding='T',  # Text encoding
            toc_type='T',  # TOC type
            version=self.version
        )
        
        toc = TableOfContents(
            magic_header=magic_header,
            section_count=len(entries),
            sections=entries
        )
        
        # Calculate actual TOC size
        toc_text = toc.generate_toc_text()
        toc.toc_size = len(toc_text.encode('utf-8'))
        
        return toc
    
    def clear_sections(self):
        """Clear all sections for reuse"""
        self.sections.clear()