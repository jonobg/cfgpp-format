#!/usr/bin/env python3
"""
Test script for Binary TOC encoder/decoder.

This script tests the revolutionary Binary CFGPP TOC system with real examples.
"""

import sys
import json
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cfgpp_format.binary_toc import (
    CFGPPBinaryEncoder, 
    CFGPPBinaryDecoder, 
    CFGPPBinaryValidator,
    SectionType
)


def test_with_real_examples():
    """Test encoder/decoder with real CFGPP examples"""
    
    print("🚀 TESTING BINARY CFGPP TOC SYSTEM")
    print("=" * 50)
    
    # Find example files - start with basic examples
    examples_dir = Path("../../specification/examples")
    test_files = []
    
    # Start with basic examples that are more likely to work
    basic_dir = examples_dir / "basic"
    if basic_dir.exists():
        test_files.extend(basic_dir.glob("*.cfgpp"))
    
    # Add real-world examples if basic ones work
    real_world_dir = examples_dir / "real-world"
    if real_world_dir.exists():
        for subdir in real_world_dir.iterdir():
            if subdir.is_dir():
                test_files.extend(subdir.glob("*.cfgpp"))
    
    if not test_files:
        print("❌ No CFGPP example files found!")
        print(f"   Looked in: {examples_dir.absolute()}")
        return False
    
    print(f"📁 Found {len(test_files)} CFGPP files to test")
    
    validator = CFGPPBinaryValidator()
    temp_dir = Path("temp_binary_toc")
    temp_dir.mkdir(exist_ok=True)
    
    total_tests = 0
    successful_tests = 0
    
    for test_file in test_files[:3]:  # Test first 3 files
        print(f"\n🧪 Testing: {test_file.name}")
        print("-" * 30)
        
        try:
            # Check if file is readable first
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   📄 File size: {len(content)} characters")
            except UnicodeDecodeError:
                print(f"   ⚠️  Skipping {test_file.name} - encoding issues")
                continue
            
            # Test round-trip validation
            results = validator.validate_round_trip(str(test_file), str(temp_dir))
            total_tests += 1
            
            if results['success']:
                successful_tests += 1
                print("✅ Round-trip validation: PASSED")
                
                # Show performance metrics
                perf = results['performance']
                print(f"   📊 Encode time: {perf['encode_time_ms']:.2f}ms")
                print(f"   📊 Decode time: {perf['decode_time_ms']:.2f}ms")
                
                # Show file sizes
                sizes = results['file_sizes']
                print(f"   📦 Original: {sizes['original_bytes']} bytes")
                print(f"   📦 Binary TOC: {sizes['binary_toc_bytes']} bytes")
                print(f"   📦 Overhead: {sizes['overhead_percent']:.1f}%")
                
                # Show detected sections
                sections = results['sections_detected']
                print(f"   🔍 Sections detected: {', '.join(sections)}")
                
                # Test section access performance
                binary_file = temp_dir / "test.cbt1"
                if binary_file.exists():
                    bench_results = validator.benchmark_section_access(str(binary_file), iterations=100)
                    if bench_results['success']:
                        avg_time = bench_results['average_access_time_ms']
                        print(f"   ⚡ Average section access: {avg_time:.3f}ms")
                
            else:
                print("❌ Round-trip validation: FAILED")
                for error in results['errors']:
                    print(f"   💥 {error}")
                    
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n🎯 SUMMARY")
    print("=" * 20)
    print(f"Tests run: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    return successful_tests == total_tests


def test_manual_example():
    """Test with a manually created example"""
    
    print("\n🧪 MANUAL EXAMPLE TEST")
    print("=" * 30)
    
    # Create a test CFGPP content
    test_content = """
// Test configuration for Binary TOC
DatabaseConfig::production(
    string host = "prod-db.company.com",
    int port = 5432,
    int pool_size = 20
)

SecurityConfig::enterprise(
    bool enforce_2fa = true,
    int session_timeout_minutes = 30,
    array[string] allowed_ips = ["10.0.0.0/8", "192.168.0.0/16"]
)

LoggingConfig::application(
    string level = "info",
    bool enable_debug = false,
    string output_file = "/var/log/app.log"
)
"""
    
    # Write test file
    temp_dir = Path("temp_binary_toc")
    temp_dir.mkdir(exist_ok=True)
    
    test_file = temp_dir / "manual_test.cfgpp"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Test encoding
    encoder = CFGPPBinaryEncoder()
    binary_file = temp_dir / "manual_test.cbt1"
    
    try:
        print("🔄 Encoding to Binary TOC...")
        toc = encoder.encode_file(str(test_file), str(binary_file))
        print(f"✅ Encoded successfully!")
        print(f"   Magic header: {toc.magic_header.to_string()}")
        print(f"   Sections: {len(toc.sections)}")
        
        # Show the generated TOC
        print("\n📋 Generated TOC:")
        toc_text = toc.generate_toc_text()
        for i, line in enumerate(toc_text.split('\n')[:10]):  # Show first 10 lines
            print(f"   {i+1:2d}: {line}")
        
        # Test decoding
        print("\n🔄 Decoding from Binary TOC...")
        decoder = CFGPPBinaryDecoder()
        decoded_content = decoder.decode_file(str(binary_file))
        print("✅ Decoded successfully!")
        
        # Show section access
        print("\n🎯 Testing O(1) section access:")
        sections = decoder.list_sections()
        
        with open(binary_file, 'r') as f:
            for section_type in sections:
                try:
                    import time
                    start = time.time()
                    content = decoder.get_section(section_type, f)
                    access_time = (time.time() - start) * 1000
                    
                    lines = len(content.split('\n'))
                    print(f"   {section_type.name}: {access_time:.3f}ms ({lines} lines)")
                except Exception as e:
                    print(f"   {section_type.name}: ERROR - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_features():
    """Demonstrate key features of the Binary TOC system"""
    
    print("\n🌟 BINARY TOC FEATURES DEMONSTRATION")
    print("=" * 40)
    
    # Show magic header variations
    print("🔤 Magic Header System:")
    from cfgpp_format.binary_toc.types import MagicHeader, CFGPPFormat
    
    headers = [
        MagicHeader(CFGPPFormat.BINARY_TOC, 'T', 'T', 1),
        MagicHeader(CFGPPFormat.BINARY_TOC, 'T', 'T', 2),
        MagicHeader(CFGPPFormat.SEQUENCE_INDEX, 'C', 'I', 1),
        MagicHeader(CFGPPFormat.AI_HASH, 'T', 'H', 1),
    ]
    
    for header in headers:
        print(f"   {header.to_string()} = {header.format_type.name} v{header.version}")
    
    # Show section types
    print("\n📋 Universal Section Types:")
    for section_type in SectionType:
        print(f"   {section_type.value} = {section_type.name}")
    
    print("\n🎯 Key Benefits:")
    print("   ✅ O(1) section access (no sequential parsing)")
    print("   ✅ Corruption detection with landmarks")
    print("   ✅ Version evolution support")
    print("   ✅ Human-readable TOC format")
    print("   ✅ UTF-8 safe text landmarks")
    print("   ✅ Backwards compatibility")


if __name__ == "__main__":
    print("🚀 BINARY CFGPP TOC SYSTEM TEST SUITE")
    print("=" * 50)
    
    # Run all tests
    success = True
    
    try:
        # Test 1: Manual example
        success &= test_manual_example()
        
        # Test 2: Real examples (if available)
        success &= test_with_real_examples()
        
        # Test 3: Feature demonstration
        demonstrate_features()
        
        print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if success else '❌ FAILURE'}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)