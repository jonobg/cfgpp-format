#!/usr/bin/env python3
"""
Debug script for Binary TOC encoder/decoder.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cfgpp_format.binary_toc import CFGPPBinaryEncoder, CFGPPBinaryDecoder


def debug_simple_example():
    """Debug with the hello-world example"""
    
    print("🔍 DEBUGGING BINARY TOC WITH HELLO-WORLD")
    print("=" * 50)
    
    # Test with hello-world.cfgpp
    test_file = Path("../../specification/examples/basic/hello-world.cfgpp")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    # Read original content
    with open(test_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    print("📄 ORIGINAL CONTENT:")
    print("-" * 20)
    for i, line in enumerate(original_content.split('\n'), 1):
        print(f"{i:2d}: {line}")
    
    # Create temp directory
    temp_dir = Path("temp_debug")
    temp_dir.mkdir(exist_ok=True)
    
    # Encode
    print("\n🔄 ENCODING...")
    encoder = CFGPPBinaryEncoder()
    binary_file = temp_dir / "hello-world.cbt1"
    
    try:
        toc = encoder.encode_file(str(test_file), str(binary_file))
        print(f"✅ Encoded successfully!")
        print(f"   Sections: {len(toc.sections)}")
        
        for section in toc.sections:
            print(f"   - {section.section_type.name}: {section.size} bytes")
        
        # Show the binary file content
        print("\n📄 BINARY TOC FILE:")
        print("-" * 20)
        with open(binary_file, 'r', encoding='utf-8') as f:
            binary_content = f.read()
        
        for i, line in enumerate(binary_content.split('\n'), 1):
            print(f"{i:2d}: {line}")
        
        # Decode
        print("\n🔄 DECODING...")
        decoder = CFGPPBinaryDecoder()
        decoded_content = decoder.decode_file(str(binary_file))
        
        print("\n📄 DECODED CONTENT:")
        print("-" * 20)
        for i, line in enumerate(decoded_content.split('\n'), 1):
            print(f"{i:2d}: {line}")
        
        # Compare
        print("\n🔍 COMPARISON:")
        print("-" * 20)
        
        # Normalize for comparison
        orig_lines = [line.strip() for line in original_content.split('\n') 
                     if line.strip() and not line.strip().startswith('//')]
        
        decoded_lines = [line.strip() for line in decoded_content.split('\n') 
                        if line.strip() and not line.strip().startswith('//')]
        
        print(f"Original lines (no comments): {len(orig_lines)}")
        print(f"Decoded lines (no comments): {len(decoded_lines)}")
        
        if orig_lines == decoded_lines:
            print("✅ Content matches!")
        else:
            print("❌ Content mismatch!")
            print("\nOriginal (normalized):")
            for i, line in enumerate(orig_lines, 1):
                print(f"  {i:2d}: {line}")
            print("\nDecoded (normalized):")
            for i, line in enumerate(decoded_lines, 1):
                print(f"  {i:2d}: {line}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_simple_example()