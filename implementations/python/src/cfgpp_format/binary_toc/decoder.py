"""
Binary CFGPP Decoder - Convert Binary TOC format back to standard CFGPP.
"""

from typing import Dict, List, Optional, TextIO
from pathlib import Path

from .types import (
    MagicHeader, SectionEntry, TableOfContents, 
    CFGPPFormat, SectionType, CFGPPBinaryError, 
    CorruptionDetectedError, UnsupportedVersionError
)


class CFGPPBinaryDecoder:
    """Decode Binary TOC format back to standard CFGPP"""
    
    def __init__(self):
        self.toc: Optional[TableOfContents] = None
        self.section_registry: Dict[SectionType, int] = {}
        
    def decode_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Decode a Binary TOC file back to standard CFGPP format
        
        Args:
            input_path: Path to Binary TOC file
            output_path: Optional output path (if None, returns content as string)
            
        Returns:
            Decoded CFGPP content as string
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            # Parse the file
            content = self._parse_file(f)
            
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        return content
    
    def _parse_file(self, file_handle: TextIO) -> str:
        """Parse Binary TOC file and return standard CFGPP content"""
        # Read magic header
        magic = file_handle.read(4)
        file_handle.seek(0)  # Reset for full parsing
        
        header = MagicHeader.from_string(magic)
        
        if header.format_type == CFGPPFormat.BINARY_TOC:
            return self._parse_binary_toc(file_handle, header)
        else:
            raise UnsupportedVersionError(f"Unsupported format: {header.format_type}")
    
    def _parse_binary_toc(self, file_handle: TextIO, header: MagicHeader) -> str:
        """Parse CBT format with TOC"""
        # Parse TOC
        self.toc = self._parse_toc_header(file_handle, header.version)
        
        # Build section registry for O(1) lookup
        self.section_registry = self.toc.get_section_registry()
        
        # Extract all sections and combine into standard CFGPP
        return self._extract_all_sections(file_handle)
    
    def _parse_toc_header(self, file_handle: TextIO, version: int) -> TableOfContents:
        """Parse TOC header section"""
        content = file_handle.read()
        lines = content.split('\n')
        
        # Find TOC boundaries
        toc_start = None
        toc_end = None
        
        for i, line in enumerate(lines):
            if line.strip() == f"---TOC-V{version}-START---":
                toc_start = i + 1
            elif line.strip() == f"---TOC-V{version}-END---":
                toc_end = i
                break
                
        if toc_start is None or toc_end is None:
            raise CorruptionDetectedError("Invalid TOC format - missing boundaries")
            
        # Parse header info
        magic_header = MagicHeader.from_string(lines[0].strip())
        toc_size = int(lines[1].split(':')[1])
        section_count = int(lines[2].split(':')[1])
        created_timestamp = lines[3].split(':', 1)[1]
        
        # Parse section entries
        sections = []
        for i in range(toc_start, toc_end):
            line = lines[i].strip()
            if line:  # Skip empty lines
                try:
                    sections.append(SectionEntry.from_toc_line(line, version))
                except Exception as e:
                    raise CorruptionDetectedError(f"Invalid TOC entry: {line}") from e
                
        return TableOfContents(
            magic_header=magic_header,
            toc_size=toc_size,
            section_count=section_count,
            created_timestamp=created_timestamp,
            sections=sections
        )
    
    def get_section(self, section_type: SectionType, file_handle: TextIO) -> str:
        """
        O(1) section access - extract specific section content
        """
        if section_type not in self.section_registry:
            raise KeyError(f"Section {section_type.value} not found in TOC")
            
        # Get all content and split into lines for seeking
        file_handle.seek(0)
        content = file_handle.read()
        lines = content.split('\n')
        
        # Find section boundaries
        start_marker = f"---{section_type.value}-START---"
        end_marker = f"---{section_type.value}-END---"
        
        start_line = None
        end_line = None
        
        for i, line in enumerate(lines):
            if line.strip() == start_marker:
                start_line = i + 1
            elif line.strip() == end_marker and start_line is not None:
                end_line = i
                break
        
        if start_line is None or end_line is None:
            raise CorruptionDetectedError(f"Section {section_type.value} boundaries not found")
        
        # Extract section content
        section_lines = lines[start_line:end_line]
        return '\n'.join(section_lines)
    
    def _extract_all_sections(self, file_handle: TextIO) -> str:
        """Extract all sections and combine into standard CFGPP format"""
        sections_content = []
        
        # Add file header comment
        sections_content.append("// Decoded from Binary TOC CFGPP format")
        sections_content.append(f"// Original format: {self.toc.magic_header.to_string()}")
        sections_content.append(f"// Created: {self.toc.created_timestamp}")
        sections_content.append("")
        
        # Extract each section in order
        for section_entry in self.toc.sections:
            try:
                section_content = self.get_section(section_entry.section_type, file_handle)
                
                # Add section comment
                sections_content.append(f"// Section: {section_entry.section_type.name}")
                sections_content.append(f"// Environment: {section_entry.environment}")
                sections_content.append("")
                
                # Add the actual content
                sections_content.append(section_content.strip())
                sections_content.append("")
                
            except Exception as e:
                # Add error comment but continue processing
                sections_content.append(f"// ERROR: Failed to decode section {section_entry.section_type.value}: {e}")
                sections_content.append("")
        
        return '\n'.join(sections_content)
    
    def list_sections(self) -> List[SectionType]:
        """List all available sections in the TOC"""
        if not self.toc:
            return []
        return [section.section_type for section in self.toc.sections]
    
    def get_section_info(self, section_type: SectionType) -> Optional[SectionEntry]:
        """Get metadata about a specific section"""
        if not self.toc:
            return None
            
        for section in self.toc.sections:
            if section.section_type == section_type:
                return section
        return None
    
    def validate_integrity(self, file_handle: TextIO) -> List[str]:
        """
        Validate file integrity and return list of issues found
        """
        issues = []
        
        if not self.toc:
            issues.append("No TOC loaded")
            return issues
        
        # Check each section exists and has correct boundaries
        for section_entry in self.toc.sections:
            try:
                content = self.get_section(section_entry.section_type, file_handle)
                
                # Validate section size (approximate, since encoding may vary)
                actual_size = len(content.encode('utf-8'))
                expected_size = section_entry.size
                
                # Allow some variance for landmarks and encoding differences
                size_variance = abs(actual_size - expected_size) / expected_size
                if size_variance > 0.1:  # 10% variance threshold
                    issues.append(
                        f"Section {section_entry.section_type.value} size mismatch: "
                        f"expected ~{expected_size}, got {actual_size}"
                    )
                    
            except Exception as e:
                issues.append(f"Section {section_entry.section_type.value} corrupted: {e}")
        
        return issues