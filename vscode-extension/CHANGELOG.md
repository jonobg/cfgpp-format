# CFG++ Language Support - Changelog

## [1.2.0] - 2025-09-22

### API Revolution & Project Reorganization Update
This release aligns the extension with the major API improvements and project reorganization.

#### Fixed
- **Language server path** updated for new modular project structure
- **Extension compatibility** with reorganized Python implementation
- **File references** updated to match new `implementations/python/src/cfgpp/tools/` structure

#### Backend Improvements
- **Clear API naming**: Backend now uses `parse_string()` and `parse_file()` instead of confusing `loads()`/`load()`
- **Professional modular structure**: Core, schema, tools, and AI components properly organized
- **Enhanced examples**: Comprehensive documentation with real-world usage patterns
- **Zero breaking changes**: All legacy APIs maintained for backward compatibility

## [1.1.0] - 2025-09-21

### Major Update - Documentation Crisis Resolution
This release aligns the extension with the major documentation overhaul of the CFG++ Format project.

#### Added
- **Extension README** with comprehensive feature documentation
- **Links to authoritative syntax reference** for users
- **Verified syntax examples** in extension documentation
- **Updated description** reflecting verified syntax support

#### Changed
- **Version bumped to 1.1.0** to reflect major documentation alignment
- **Package description updated** to highlight verified syntax support
- **Documentation references** now point to authoritative syntax guide

#### Verified
- All syntax patterns in extension align with tested parser implementation
- Extension grammar supports all verified working syntax features:
  - Environment variables: `${VAR:-"default"}`
  - Include directives: `@include "file.cfgpp"`
  - Constructor syntax: `ObjectName(params) { body }`
  - Namespaced identifiers: `Module::Type`
  - Enum definitions: `enum::Name { values = [...] }`

### Context
This update resolves the alignment between extension capabilities and actual parser implementation. Previously, the project suffered from contradictory documentation that made it appear broken. The extension now reflects the reality that CFG++ is a substantial, working configuration format with comprehensive features.

## [1.0.4] - Previous

### Features
- Basic language support for CFG++ files
- Syntax highlighting and validation
- Language Server Protocol integration

---

*This changelog documents the extension's evolution alongside the main CFG++ Format project documentation overhaul.*
