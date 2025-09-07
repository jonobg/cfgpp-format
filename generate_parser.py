import os
import sys
from pathlib import Path

def generate_parser():
    """Generate the parser from the grammar file using ANTLR."""
    # Ensure the output directory exists
    grammar_dir = Path("src/cfgpp/grammar")
    output_dir = grammar_dir / "generated"
    output_dir.mkdir(exist_ok=True)
    
    # Path to the grammar file
    grammar_file = grammar_dir / "Cfgpp.g4"
    
    print(f"Generating parser from {grammar_file}...")
    
    # Generate the parser using antlr4-tools
    os.system(f"antlr4 -Dlanguage=Python3 -o {output_dir} -visitor -no-listener {grammar_file}")
    
    # Create __init__.py in the generated directory
    (output_dir / "__init__.py").touch()
    
    print("Parser generated successfully!")

if __name__ == "__main__":
    generate_parser()
