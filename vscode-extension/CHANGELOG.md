# CFG++ Language Support - Changelog

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
