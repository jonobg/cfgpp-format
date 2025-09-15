cmake_minimum_required(VERSION 3.16)
project(CFGPPParser VERSION 1.0.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Windows-specific optimizations
if(WIN32)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /O2 /arch:AVX2 /fp:fast")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /GL /LTCG")
    set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /LTCG")
    
    # Enable SIMD intrinsics
    add_definitions(-D_WIN32 -DCFGPP_EXPORTS)
endif()

# Source files
set(SOURCES
    cfgpp_parser.cpp
    cfgpp_parser.h
)

# Create shared library (DLL)
add_library(cfgpp_parser SHARED ${SOURCES})

# Set DLL properties
set_target_properties(cfgpp_parser PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
    OUTPUT_NAME "cfgpp_parser"
    PREFIX ""  # Remove lib prefix on Windows
)

# Include directories
target_include_directories(cfgpp_parser PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
)

# Link libraries
if(WIN32)
    # Windows-specific optimizations
    target_link_libraries(cfgpp_parser PRIVATE)
endif()

# Compiler-specific optimizations
if(MSVC)
    target_compile_options(cfgpp_parser PRIVATE
        /W4          # Warning level 4
        /WX          # Warnings as errors
        /O2          # Optimize for speed
        /Oi          # Enable intrinsic functions
        /Ot          # Favor fast code
        /arch:AVX2   # Enable AVX2 instructions
        /fp:fast     # Fast floating-point model
    )
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(cfgpp_parser PRIVATE
        -Wall -Wextra -Werror
        -O3
        -mavx2
        -ffast-math
        -funroll-loops
        -march=native
    )
endif()

# Installation
install(TARGETS cfgpp_parser
    EXPORT CFGPPParserTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(FILES cfgpp_parser.h
    DESTINATION include
)

# Export configuration
install(EXPORT CFGPPParserTargets
    FILE CFGPPParserTargets.cmake
    NAMESPACE CFGPPParser::
    DESTINATION lib/cmake/CFGPPParser
)

# Create config file
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    CFGPPParserConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/CFGPPParserConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/CFGPPParserConfig.cmake
    INSTALL_DESTINATION lib/cmake/CFGPPParser
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/CFGPPParserConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/CFGPPParserConfigVersion.cmake
    DESTINATION lib/cmake/CFGPPParser
)

# Build tests (optional)
option(BUILD_TESTS "Build test programs" ON)
if(BUILD_TESTS)
    add_subdirectory(tests)
endif()

# Build examples
option(BUILD_EXAMPLES "Build example programs" ON)
if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()
