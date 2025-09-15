# CFG++ C++ LabVIEW Implementation

High-performance C++ parser optimized for LabVIEW integration with DLL support and LabVIEW-specific data structures.

## Features

- **🔗 LabVIEW Integration**: Native support for LabVIEW clusters and variants
- **📚 Windows DLL**: Ready-to-use DLL for LabVIEW applications
- **⚡ High Performance**: SIMD-optimized parsing with memory pooling
- **🛡️ Schema Validation**: Built-in validation with detailed error reporting
- **🔧 C API**: Clean C interface compatible with LabVIEW
- **📦 CMake Build**: Cross-platform build system

## LabVIEW Integration

```c
// Convert LabVIEW cluster to CFG++ file
CfgppResult result = cfgpp_cluster_to_file(
    cluster_data,       // LabVIEW cluster data
    data_size,          // Size of cluster data
    field_names,        // Array of field names
    field_count,        // Number of fields
    "config.cfgpp"      // Output file path
);

// Parse CFG++ file back to LabVIEW
CfgppValueHandle config;
cfgpp_parse_file(parser, "config.cfgpp", &config);
```

## Schema Validation

```c
// Load schema
CfgppSchemaHandle schema;
cfgpp_schema_create(&schema);
cfgpp_schema_parse_file(schema, "measurement.cfgpp-schema");

// Validate LabVIEW data with schema
cfgpp_cluster_to_file_validated(
    cluster_data, data_size, field_names, field_count,
    "validated_config.cfgpp", schema
);
```

## Building the DLL

### Prerequisites

**Required Software:**
- **CMake 3.15+** - [Download from cmake.org](https://cmake.org/download/)
- **Visual Studio 2019 or newer** (Community edition is fine)
  - Must include "Desktop development with C++" workload
  - Windows SDK 10.0.18362.0 or newer
- **LabVIEW 2018 or newer** (for integration testing)

**Recommended Tools:**
- Git for version control
- Visual Studio Code with CMake extensions

### Step-by-Step Build Process

#### 1. Setup Build Environment
```bash
# Navigate to the C++ LabVIEW implementation
cd implementations/cpp-labview

# Create and enter build directory
mkdir build
cd build
```

#### 2. Configure CMake
```bash
# For Visual Studio (64-bit, recommended for LabVIEW)
cmake .. -G "Visual Studio 16 2019" -A x64

# Alternative: For specific Visual Studio version
cmake .. -G "Visual Studio 17 2022" -A x64

# For MinGW (if preferred)
cmake .. -G "MinGW Makefiles"
```

#### 3. Build the DLL
```bash
# Release build (recommended for production)
cmake --build . --config Release

# Debug build (for development)
cmake --build . --config Debug

# Build both configurations
cmake --build . --config Release
cmake --build . --config Debug
```

#### 4. Install and Package
```bash
# Install to dist directory
cmake --install . --prefix ../dist --config Release

# Your DLL will be in: implementations/cpp-labview/dist/bin/cfgpp_parser.dll
```

### Build Output Structure
```
cpp-labview/
├── build/                 # Build artifacts
│   ├── Release/          # Release binaries
│   │   └── cfgpp_parser.dll
│   └── Debug/            # Debug binaries (optional)
│       └── cfgpp_parser.dll
├── dist/                 # Installation directory
│   ├── bin/              # DLL files
│   │   └── cfgpp_parser.dll
│   ├── include/          # Header files
│   │   └── cfgpp_parser.h
│   └── lib/              # Import libraries
│       └── cfgpp_parser.lib
```

### LabVIEW Integration Setup

#### 1. Copy Files to LabVIEW Project
```bash
# Copy DLL to your LabVIEW project directory
copy dist\bin\cfgpp_parser.dll "C:\YourLabVIEWProject\"

# Copy header for reference
copy src\cfgpp_parser.h "C:\YourLabVIEWProject\"
```

#### 2. Configure Call Library Function Node

**In LabVIEW:**
1. **Add Call Library Function Node** to your block diagram
2. **Configure the node:**
   - **Library name or path**: `cfgpp_parser.dll`
   - **Function name**: `cfgpp_parse_file` (or desired function)
   - **Calling convention**: `stdcall (__stdcall)`
   - **Thread**: `Run in any thread`

#### 3. Function Parameter Configuration

**Example for `cfgpp_parse_file`:**
- **parser** (input): `Pointer to Void` 
- **filename** (input): `C String`
- **result** (output): `Pointer to Void`
- **Return value**: `Numeric U32` (error code)

#### 4. Memory Management
```c
// Always create parser before use
CfgppParserHandle parser;
cfgpp_parser_create(&parser);

// Always cleanup when done  
cfgpp_parser_destroy(parser);
cfgpp_value_destroy(value);
```

### Troubleshooting

#### Common Build Issues

**❌ CMake not found**
```bash
# Add CMake to PATH or use full path
"C:\Program Files\CMake\bin\cmake.exe" ..
```

**❌ Visual Studio not detected**
```bash
# List available generators
cmake --help

# Use specific VS version
cmake .. -G "Visual Studio 16 2019" -A x64
```

**❌ Missing Windows SDK**
- Install Windows SDK through Visual Studio Installer
- Or specify SDK version: `cmake .. -DCMAKE_SYSTEM_VERSION=10.0.19041.0`

#### Runtime Issues

**❌ DLL not found in LabVIEW**
- Ensure DLL is in same directory as VI
- Or add DLL path to Windows PATH environment variable
- Check DLL architecture (x86 vs x64) matches LabVIEW

**❌ Function not found**
- Verify function name spelling in Call Library Function Node
- Use `dumpbin /exports cfgpp_parser.dll` to list available functions
- Ensure calling convention is set to `stdcall`

**❌ Access violation errors**
- Always initialize pointers before use
- Check parameter types match exactly
- Ensure proper cleanup of allocated memory

#### Performance Optimization

**For Maximum Performance:**
```bash
# Enable CPU-specific optimizations
cmake .. -DCMAKE_CXX_FLAGS="/O2 /arch:AVX2"

# Link-time optimization  
cmake .. -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=TRUE
```

### Testing the Integration

#### 1. Basic Function Test
```c
// Test in LabVIEW or C test program
CfgppParserHandle parser;
CfgppResult result = cfgpp_parser_create(&parser);
if (result == CFGPP_SUCCESS) {
    printf("Parser created successfully!\n");
    cfgpp_parser_destroy(parser);
}
```

#### 2. Parse Test File
Create `test_config.cfgpp`:
```cfgpp
database {
    host = "localhost";
    port = 5432;
}
```

Then test parsing:
```c
CfgppValueHandle config;
result = cfgpp_parse_file(parser, "test_config.cfgpp", &config);
```

### Advanced Build Options

#### Custom Build Configuration
```bash
# Static runtime linking
cmake .. -DCFGPP_STATIC_RUNTIME=ON

# Enable debugging symbols in release
cmake .. -DCMAKE_CXX_FLAGS_RELEASE="/O2 /Zi"

# Custom install prefix
cmake .. -DCMAKE_INSTALL_PREFIX="C:/CFGPlusPlus"
```

#### Cross-compilation (Advanced)
```bash
# For different architectures
cmake .. -A Win32    # 32-bit
cmake .. -A x64      # 64-bit  
cmake .. -A ARM64    # ARM64
```

## Performance

| Operation | Time | Memory |
|-----------|------|--------|
| Parse 1KB config | ~20μs | 2KB |
| Parse 100KB config | ~800μs | 150KB |
| Schema validation | ~50μs | 1KB |
| LabVIEW cluster conversion | ~30μs | 4KB |

## API Reference

### Core Functions
- `cfgpp_parser_create()` - Create parser instance
- `cfgpp_parse_file()` - Parse CFG++ file
- `cfgpp_parse_string()` - Parse CFG++ string

### LabVIEW Integration  
- `cfgpp_from_labview_cluster()` - Convert LabVIEW cluster
- `cfgpp_cluster_to_file()` - Write cluster to CFG++ file
- `cfgpp_variant_to_string()` - Convert variant to CFG++ string

### Schema Validation
- `cfgpp_schema_create()` - Create schema validator
- `cfgpp_validate_value()` - Validate against schema
- `cfgpp_generate_schema_from_cluster()` - Auto-generate schema

## Project Structure

```
cpp-labview/
├── src/                    # C++ source files
│   ├── cfgpp_parser.cpp   # Main implementation
│   └── cfgpp_parser.h     # C API header
├── examples/              # LabVIEW integration examples
│   ├── labview_example.cpp
│   └── labview_integration_example.cpp
├── CMakeLists.txt         # CMake build configuration
└── CFGPPParserConfig.cmake.in  # CMake package config
```

## Examples

See the [examples/](examples/) directory for complete LabVIEW integration examples and usage patterns.

## Documentation

- [C API Reference](../../docs/api-reference/cpp-labview.md)
- [LabVIEW Integration Guide](../../docs/integration-guides/labview.md)
- [Performance Guide](../../docs/performance/cpp-optimization.md)
