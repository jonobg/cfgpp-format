#!/usr/bin/env python3
"""
Example Files Validation Tests

This test suite ensures that ALL example files in the specification/examples/
directory parse correctly with the CFGPP parser. This implements the zero
tolerance quality standard: "No syntax errors in examples - users copy/paste these"

Based on proven methodology from CFGPP-Format case study:
- Treat examples as integration tests
- Validate example configurations parse correctly
- Ensure examples reflect actual working implementation
"""

import os
import pytest
from pathlib import Path
from typing import List, Tuple
import time

from cfgpp.core.parser import loads, ConfigParseError
from cfgpp.core.lexer import LexerError


class TestExamplesValidation:
    """Comprehensive validation of all CFGPP example files."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment and discover all example files."""
        # Find the project root (where this test file is located relative to project)
        cls.project_root = Path(__file__).parent.parent.parent.parent
        cls.examples_dir = cls.project_root / "specification" / "examples"
        
        # Discover all .cfgpp files recursively
        cls.example_files = list(cls.examples_dir.rglob("*.cfgpp"))
        
        # Ensure we found example files
        assert len(cls.example_files) > 0, f"No .cfgpp files found in {cls.examples_dir}"
        
        print(f"Found {len(cls.example_files)} example files to validate")
        for file in cls.example_files:
            print(f"  - {file.relative_to(cls.examples_dir)}")
    
    def test_all_examples_parse_successfully(self):
        """Test that all example files parse without errors."""
        failed_files = []
        parsing_times = []
        
        for example_file in self.example_files:
            try:
                # Measure parsing time for performance tracking
                start_time = time.time()
                
                # Read and parse the example file
                with open(example_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the configuration
                result = loads(content)
                
                # Record parsing time
                parsing_time = time.time() - start_time
                parsing_times.append((example_file.name, parsing_time))
                
                # Basic validation that we got a result
                assert result is not None, f"Parser returned None for {example_file}"
                assert isinstance(result, dict), f"Parser should return dict, got {type(result)} for {example_file}"
                
                print(f"✅ {example_file.relative_to(self.examples_dir)} - {parsing_time:.4f}s")
                
            except (ConfigParseError, LexerError) as e:
                failed_files.append((example_file, str(e)))
                print(f"❌ {example_file.relative_to(self.examples_dir)} - Parse Error: {e}")
                
            except Exception as e:
                failed_files.append((example_file, f"Unexpected error: {str(e)}"))
                print(f"💥 {example_file.relative_to(self.examples_dir)} - Unexpected Error: {e}")
        
        # Report performance statistics
        if parsing_times:
            avg_time = sum(time for _, time in parsing_times) / len(parsing_times)
            max_time = max(parsing_times, key=lambda x: x[1])
            min_time = min(parsing_times, key=lambda x: x[1])
            
            print(f"\n📊 Parsing Performance:")
            print(f"   Average: {avg_time:.4f}s")
            print(f"   Fastest: {min_time[0]} ({min_time[1]:.4f}s)")
            print(f"   Slowest: {max_time[0]} ({max_time[1]:.4f}s)")
        
        # Assert that no files failed to parse
        if failed_files:
            error_msg = f"\n{len(failed_files)} example files failed to parse:\n"
            for file, error in failed_files:
                error_msg += f"  - {file.relative_to(self.examples_dir)}: {error}\n"
            error_msg += "\nAll example files must parse correctly (zero tolerance quality standard)."
            pytest.fail(error_msg)
    
    def test_basic_examples_structure(self):
        """Test that basic examples have expected structure and content."""
        basic_dir = self.examples_dir / "basic"
        
        # Check that basic directory exists and has expected files
        assert basic_dir.exists(), "basic/ directory should exist"
        
        expected_basic_files = [
            "hello-world.cfgpp",
            "data-types.cfgpp", 
            "comments.cfgpp",
            "environment-variables.cfgpp"
        ]
        
        for expected_file in expected_basic_files:
            file_path = basic_dir / expected_file
            assert file_path.exists(), f"Expected basic example {expected_file} should exist"
            
            # Parse and validate basic structure
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = loads(content)
            assert isinstance(result, dict), f"Basic example {expected_file} should parse to dict"
            assert len(result) > 0, f"Basic example {expected_file} should not be empty"
    
    def test_ai_aware_examples_structure(self):
        """Test that AI-aware examples have expected structure and AI features."""
        ai_aware_dir = self.examples_dir / "ai-aware"
        
        # Check that ai-aware directory exists
        assert ai_aware_dir.exists(), "ai-aware/ directory should exist"
        
        # Find AI-aware example files
        ai_aware_files = list(ai_aware_dir.glob("*.cfgpp"))
        assert len(ai_aware_files) > 0, "Should have AI-aware example files"
        
        for ai_file in ai_aware_files:
            with open(ai_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for AI-aware features in content (as comments/metadata)
            ai_features_found = []
            
            if "@config-hash" in content:
                ai_features_found.append("hash-validation")
            if "@compression-config" in content:
                ai_features_found.append("compression")
            if "@ai-validated-by" in content:
                ai_features_found.append("ai-signatures")
            if "@mqtt-config" in content:
                ai_features_found.append("iot-integration")
            
            # AI-aware examples should demonstrate AI features
            assert len(ai_features_found) > 0, f"AI-aware example {ai_file.name} should contain AI feature annotations"
            
            # Parse the configuration (ignoring AI metadata for now)
            result = loads(content)
            assert isinstance(result, dict), f"AI-aware example {ai_file.name} should parse to dict"
    
    def test_example_file_naming_conventions(self):
        """Test that example files follow naming conventions."""
        for example_file in self.example_files:
            filename = example_file.name
            
            # Should be kebab-case
            assert filename.islower(), f"Example file {filename} should be lowercase"
            assert filename.endswith('.cfgpp'), f"Example file {filename} should end with .cfgpp"
            
            # Should not contain spaces or special characters (except hyphens)
            import re
            assert re.match(r'^[a-z0-9-]+\.cfgpp$', filename), f"Example file {filename} should use kebab-case naming"
    
    def test_example_directories_have_readmes(self):
        """Test that example directories have README.md files."""
        example_subdirs = [d for d in self.examples_dir.iterdir() if d.is_dir() and d.name != '__pycache__']
        
        for subdir in example_subdirs:
            readme_path = subdir / "README.md"
            assert readme_path.exists(), f"Directory {subdir.name}/ should have a README.md file"
            
            # README should not be empty
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read().strip()
            assert len(readme_content) > 0, f"README.md in {subdir.name}/ should not be empty"
    
    def test_performance_benchmarks(self):
        """Test parsing performance to ensure examples are efficient."""
        performance_results = []
        
        for example_file in self.example_files:
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Measure parsing time over multiple iterations
            iterations = 10
            total_time = 0
            
            for _ in range(iterations):
                start_time = time.time()
                loads(content)
                total_time += time.time() - start_time
            
            avg_time = total_time / iterations
            file_size = len(content)
            
            performance_results.append({
                'file': example_file.relative_to(self.examples_dir),
                'avg_time': avg_time,
                'size': file_size,
                'throughput': file_size / avg_time if avg_time > 0 else float('inf')
            })
        
        # Sort by parsing time (slowest first)
        performance_results.sort(key=lambda x: x['avg_time'], reverse=True)
        
        print(f"\n📈 Performance Benchmark Results:")
        print(f"{'File':<40} {'Size':<8} {'Time':<10} {'Throughput':<12}")
        print("-" * 72)
        
        for result in performance_results:
            throughput_str = f"{result['throughput']:.0f} B/s" if result['throughput'] != float('inf') else "∞"
            print(f"{str(result['file']):<40} {result['size']:<8} {result['avg_time']:.4f}s   {throughput_str:<12}")
        
        # Performance assertions
        max_acceptable_time = 0.1  # 100ms should be plenty for any example
        slow_files = [r for r in performance_results if r['avg_time'] > max_acceptable_time]
        
        if slow_files:
            slow_files_str = ", ".join(str(f['file']) for f in slow_files)
            pytest.fail(f"Example files taking too long to parse (>{max_acceptable_time}s): {slow_files_str}")
    
    def test_example_content_quality(self):
        """Test that examples have good content quality (comments, structure)."""
        for example_file in self.example_files:
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Examples should have comments explaining what they demonstrate
            assert '//' in content or '/*' in content, f"Example {example_file.name} should have explanatory comments"
            
            # Examples should not be too short (should be educational)
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            non_comment_lines = [line for line in lines if not line.startswith('//') and not line.startswith('/*')]
            
            assert len(non_comment_lines) >= 3, f"Example {example_file.name} should have substantial content (at least 3 non-comment lines)"
    
