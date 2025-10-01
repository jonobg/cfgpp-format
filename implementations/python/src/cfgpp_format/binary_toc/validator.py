"""
Binary CFGPP Validator - Test round-trip encoding/decoding and performance.
"""

import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .encoder import CFGPPBinaryEncoder
from .decoder import CFGPPBinaryDecoder
from .types import SectionType, CFGPPBinaryError


class CFGPPBinaryValidator:
    """Validate Binary TOC encoding/decoding with performance benchmarks"""
    
    def __init__(self):
        self.encoder = CFGPPBinaryEncoder()
        self.decoder = CFGPPBinaryDecoder()
        
    def validate_round_trip(self, input_file: str, temp_dir: str = "temp") -> Dict[str, any]:
        """
        Test complete round-trip: CFGPP → Binary TOC → CFGPP
        
        Returns validation results with performance metrics
        """
        results = {
            'success': False,
            'errors': [],
            'performance': {},
            'file_sizes': {},
            'sections_detected': []
        }
        
        try:
            # Create temp directory
            temp_path = Path(temp_dir)
            temp_path.mkdir(exist_ok=True)
            
            binary_file = temp_path / "test.cbt1"
            decoded_file = temp_path / "decoded.cfgpp"
            
            # Step 1: Encode to Binary TOC
            start_time = time.time()
            toc = self.encoder.encode_file(input_file, str(binary_file))
            encode_time = time.time() - start_time
            
            results['performance']['encode_time_ms'] = encode_time * 1000
            results['sections_detected'] = [s.section_type.name for s in toc.sections]
            
            # Step 2: Decode back to CFGPP
            start_time = time.time()
            decoded_content = self.decoder.decode_file(str(binary_file), str(decoded_file))
            decode_time = time.time() - start_time
            
            results['performance']['decode_time_ms'] = decode_time * 1000
            
            # Step 3: File size comparison
            original_size = Path(input_file).stat().st_size
            binary_size = binary_file.stat().st_size
            decoded_size = decoded_file.stat().st_size
            
            results['file_sizes'] = {
                'original_bytes': original_size,
                'binary_toc_bytes': binary_size,
                'decoded_bytes': decoded_size,
                'overhead_percent': ((binary_size - original_size) / original_size) * 100
            }
            
            # Step 4: Content validation
            with open(input_file, 'r') as f:
                original_content = f.read().strip()
            
            # Remove decoder comments for comparison
            decoded_lines = decoded_content.split('\n')
            content_lines = [line for line in decoded_lines 
                           if not line.strip().startswith('// ')]
            clean_decoded = '\n'.join(content_lines).strip()
            
            # Normalize whitespace for comparison
            original_normalized = self._normalize_content(original_content)
            decoded_normalized = self._normalize_content(clean_decoded)
            
            if original_normalized == decoded_normalized:
                results['success'] = True
            else:
                results['errors'].append("Content mismatch after round-trip")
                results['content_diff'] = self._show_diff(original_normalized, decoded_normalized)
            
        except Exception as e:
            results['errors'].append(f"Validation failed: {str(e)}")
            
        return results
    
    def benchmark_section_access(self, binary_file: str, iterations: int = 1000) -> Dict[str, any]:
        """
        Benchmark O(1) section access performance
        """
        results = {
            'success': False,
            'section_access_times': {},
            'average_access_time_ms': 0,
            'sections_tested': []
        }
        
        try:
            # Load the binary file
            with open(binary_file, 'r') as f:
                self.decoder._parse_file(f)
            
            available_sections = self.decoder.list_sections()
            results['sections_tested'] = [s.name for s in available_sections]
            
            if not available_sections:
                results['errors'] = ['No sections found in binary file']
                return results
            
            # Test each section access time
            total_time = 0
            
            for section_type in available_sections:
                section_times = []
                
                with open(binary_file, 'r') as f:
                    for _ in range(iterations):
                        start_time = time.time()
                        content = self.decoder.get_section(section_type, f)
                        access_time = time.time() - start_time
                        section_times.append(access_time * 1000)  # Convert to ms
                
                avg_time = sum(section_times) / len(section_times)
                results['section_access_times'][section_type.name] = {
                    'average_ms': avg_time,
                    'min_ms': min(section_times),
                    'max_ms': max(section_times)
                }
                total_time += avg_time
            
            results['average_access_time_ms'] = total_time / len(available_sections)
            results['success'] = True
            
        except Exception as e:
            results['errors'] = [f"Benchmark failed: {str(e)}"]
            
        return results
    
    def validate_corruption_detection(self, binary_file: str) -> Dict[str, any]:
        """
        Test corruption detection capabilities
        """
        results = {
            'success': False,
            'integrity_issues': [],
            'corruption_tests': {}
        }
        
        try:
            # Test 1: Normal integrity check
            with open(binary_file, 'r') as f:
                self.decoder._parse_file(f)
                issues = self.decoder.validate_integrity(f)
            
            results['integrity_issues'] = issues
            
            # Test 2: Simulate corruption by modifying file
            temp_file = Path(binary_file).with_suffix('.corrupted')
            
            with open(binary_file, 'r') as original:
                content = original.read()
            
            # Corrupt a section marker
            corrupted_content = content.replace('---DB-START---', '---DB-CORRUPT---', 1)
            
            with open(temp_file, 'w') as corrupted:
                corrupted.write(corrupted_content)
            
            # Test corruption detection
            try:
                with open(temp_file, 'r') as f:
                    self.decoder._parse_file(f)
                    self.decoder.get_section(SectionType.DATABASE, f)
                results['corruption_tests']['marker_corruption'] = 'NOT_DETECTED'
            except CFGPPBinaryError:
                results['corruption_tests']['marker_corruption'] = 'DETECTED'
            
            # Clean up
            temp_file.unlink(missing_ok=True)
            
            results['success'] = True
            
        except Exception as e:
            results['errors'] = [f"Corruption test failed: {str(e)}"]
            
        return results
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for comparison"""
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remove comments and empty lines
            stripped = line.strip()
            if stripped and not stripped.startswith('//') and not stripped.startswith('@'):
                normalized_lines.append(stripped)
        
        return '\n'.join(normalized_lines)
    
    def _show_diff(self, original: str, decoded: str) -> Dict[str, any]:
        """Show differences between original and decoded content"""
        orig_lines = original.split('\n')
        dec_lines = decoded.split('\n')
        
        return {
            'original_lines': len(orig_lines),
            'decoded_lines': len(dec_lines),
            'first_difference': self._find_first_diff(orig_lines, dec_lines)
        }
    
    def _find_first_diff(self, orig_lines: List[str], dec_lines: List[str]) -> Optional[Dict[str, any]]:
        """Find first difference between line lists"""
        max_lines = max(len(orig_lines), len(dec_lines))
        
        for i in range(max_lines):
            orig_line = orig_lines[i] if i < len(orig_lines) else "<MISSING>"
            dec_line = dec_lines[i] if i < len(dec_lines) else "<MISSING>"
            
            if orig_line != dec_line:
                return {
                    'line_number': i + 1,
                    'original': orig_line,
                    'decoded': dec_line
                }
        
        return None