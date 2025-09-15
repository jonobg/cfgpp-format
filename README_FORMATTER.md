# CFG++ Format - Code Formatter

The cfgpp-format package now includes a comprehensive code formatter that provides consistent styling for your configuration files.

## Quick Start

```bash
# Format files in place
cfgpp format config.cfgpp --in-place

# Check if files are formatted
cfgpp format-check *.cfgpp

# Format with specific style
cfgpp format config.cfgpp --style compact --in-place

# Show what would change
cfgpp format config.cfgpp --diff
```

## Formatting Styles

### Default Style
- 4-space indentation
- Braces on same line
- Auto array formatting
- Moderate spacing

### Compact Style
- 2-space indentation  
- Minimal blank lines
- Compact arrays
- Reduced spacing

### Expanded Style
- 4-space indentation
- Braces on new lines
- Multi-line arrays
- Extra blank lines for readability

## Configuration

Create a `.cfgpp-format` file to customize formatting:

```json
{
  "indent_size": 4,
  "use_tabs": false,
  "space_before_equals": true,
  "space_after_equals": true,
  "brace_style": "same_line",
  "array_style": "auto",
  "max_line_length": 100,
  "sort_object_keys": false
}
```

### Configuration Options

- **`indent_size`**: Number of spaces per indentation level
- **`use_tabs`**: Use tabs instead of spaces
- **`space_before_equals`**: Add space before `=` in assignments
- **`space_after_equals`**: Add space after `=` in assignments
- **`brace_style`**: `"same_line"`, `"new_line"`, or `"new_line_indent"`
- **`array_style`**: `"compact"`, `"one_per_line"`, or `"auto"`
- **`max_line_length`**: Maximum line length before wrapping
- **`blank_lines_before_object`**: Blank lines before top-level objects
- **`blank_lines_after_object`**: Blank lines after top-level objects
- **`sort_object_keys`**: Alphabetically sort object properties
- **`sort_enum_values`**: Alphabetically sort enum values

## CLI Commands

### `cfgpp format`
Format configuration files with various options.

```bash
cfgpp format config.cfgpp [options]
```

Options:
- `--in-place, -i`: Format files in place
- `--output, -o DIR`: Output directory for formatted files
- `--style STYLE`: Use predefined style (default, compact, expanded)
- `--check`: Check if files are formatted (exit 1 if not)
- `--diff`: Show diff of changes
- `--config, -c FILE`: Use specific configuration file
- `--indent SIZE`: Override indentation size
- `--tabs`: Use tabs instead of spaces
- `--max-line-length LENGTH`: Override max line length
- `--sort-keys`: Sort object keys alphabetically
- `--quiet, -q`: Suppress non-error output
- `--verbose, -v`: Show detailed information

### `cfgpp format-check`
Check formatting without modifying files.

```bash
cfgpp format-check config.cfgpp [options]
```

### `cfgpp format-init`
Create a formatting configuration file.

```bash
cfgpp format-init [options]
```

Options:
- `--style STYLE`: Base style for configuration
- `--output, -o FILE`: Output configuration file
- `--force, -f`: Overwrite existing file

## Examples

### Basic Formatting
```bash
# Format a single file
cfgpp format config.cfgpp --in-place

# Format multiple files
cfgpp format *.cfgpp --in-place

# Check formatting status
cfgpp format-check config.cfgpp
```

### Advanced Usage
```bash
# Use compact style with custom indentation
cfgpp format config.cfgpp --style compact --indent 2 --in-place

# Show differences without modifying files
cfgpp format config.cfgpp --diff

# Format with custom configuration
cfgpp format config.cfgpp --config .my-format-config --in-place

# Sort keys and format
cfgpp format config.cfgpp --sort-keys --in-place
```

### CI/CD Integration
```bash
# Check formatting in CI pipeline
cfgpp format-check src/**/*.cfgpp || exit 1

# Format all files in project
find . -name "*.cfgpp" -exec cfgpp format {} --in-place \;
```

## Editor Integration

### VS Code
Add to your `settings.json`:
```json
{
  "files.associations": {
    "*.cfgpp": "cfgpp"
  },
  "[cfgpp]": {
    "editor.defaultFormatter": "cfgpp-format",
    "editor.formatOnSave": true
  }
}
```

### Pre-commit Hook
Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: cfgpp-format
        name: Format CFGPP files
        entry: cfgpp format-check
        language: system
        files: \.cfgpp$
```

## Features

- **AST-based formatting**: Preserves semantic meaning
- **Schema-aware**: Respects schema definitions when available
- **Configurable**: Extensive customization options
- **Fast**: Efficient processing of large configuration files
- **Error recovery**: Graceful handling of syntax errors
- **Multiple output formats**: In-place, directory, or stdout

The formatter ensures your cfgpp configuration files maintain consistent style across your team and projects.
