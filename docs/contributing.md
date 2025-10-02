# Contributing to CFGPP

Thank you for your interest in contributing to the CFGPP configuration parser! This document provides guidelines and information for contributors.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Feature Requests](#feature-requests)
8. [Bug Reports](#bug-reports)

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Git version control

### Quick Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cfgpp-format.git
   cd cfgpp-format
   ```
3. Install in development mode:
   ```bash
   pip install -e .
   ```
4. Install development dependencies:
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

## Development Setup

### Virtual Environment

We recommend using a virtual environment for development:

```bash
python -m venv cfgpp-dev
source cfgpp-dev/bin/activate  # On Windows: cfgpp-dev\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt  # When available
```

### IDE Configuration

The project works well with:
- **VS Code**: Use the Python extension with the following settings:
  ```json
  {
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
  }
  ```
- **PyCharm**: Configure Python interpreter to point to your virtual environment

## Project Structure

```
cfgpp-format/
├── src/
│   └── cfgpp/
│       ├── __init__.py          # Package exports
│       ├── parser.py            # Main parser implementation
│       └── lexer.py             # Lexical analyzer
├── tests/
│   ├── test_parser.py           # Parser tests
│   └── test_namespaced_identifiers.py  # Namespace tests
├── examples/
│   └── complex_config.cfgpp     # Example configuration
├── docs/                        # Documentation
├── setup.py                     # Package configuration
└── README.md                    # Project overview
```

### Key Components

- **`src/cfgpp/lexer.py`**: Tokenizes CFGPP text into tokens
- **`src/cfgpp/parser.py`**: Parses tokens into structured data
- **`src/cfgpp/__init__.py`**: Public API exports
- **`tests/`**: Test suite with comprehensive coverage
- **`docs/`**: Documentation in Markdown format

## Coding Standards

### Python Style

We follow PEP 8 with some specific guidelines:

- **Line length**: 88 characters (Black default)
- **Imports**: Group imports in this order:
  ```python
  # Standard library
  import re
  from typing import Dict, List
  
  # Third-party packages
  import pytest
  
  # Local imports
  from cfgpp.lexer import lex
  ```
- **Type hints**: Use type hints for all public functions and methods
- **Docstrings**: Use Google-style docstrings

### Code Formatting

Use Black for code formatting:
```bash
black src/ tests/
```

### Linting

Use flake8 for linting:
```bash
flake8 src/ tests/
```

### Type Checking

Use mypy for type checking:
```bash
mypy src/
```

### Example Code Style

```python
from typing import Dict, List, Optional, Any


class ConfigParseError(SyntaxError):
    """Custom exception for configuration parsing errors.
    
    Args:
        message: Error description
        line: Line number where error occurred
        column: Column number where error occurred
        context: Additional context information
    """
    
    def __init__(
        self, 
        message: str, 
        line: Optional[int] = None, 
        column: Optional[int] = None, 
        context: Optional[str] = None
    ) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message with line and column information."""
        # Implementation here...
        pass
```

## Testing

### Running Tests

Run the full test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src/cfgpp --cov-report=html
```

Run specific test files:
```bash
pytest tests/test_parser.py
pytest tests/test_namespaced_identifiers.py
```

### Writing Tests

Follow these guidelines when writing tests:

1. **Test file naming**: `test_*.py` or `*_test.py`
2. **Test function naming**: `test_descriptive_name`
3. **Use descriptive assertions**: 
   ```python
   # Good
   assert result['body']['Config']['body']['name']['value']['value'] == "test"
   
   # Better with helper
   def get_config_value(result, path):
       # Helper to navigate the nested structure
       pass
   
   assert get_config_value(result, "Config.name") == "test"
   ```

### Test Categories

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test component interactions
- **Edge case tests**: Test boundary conditions and error cases
- **Example tests**: Test against example configuration files

### Example Test

```python
import pytest
from cfgpp import loads
from cfgpp.parser import ConfigParseError


def test_simple_config_parsing():
    """Test parsing a simple configuration."""
    config = """
    AppConfig {
        name = "TestApp"
        port = 8080
        debug = true
    }
    """
    
    result = loads(config)
    
    # Verify structure
    assert 'body' in result
    assert 'AppConfig' in result['body']
    
    app_config = result['body']['AppConfig']['body']
    
    # Verify values
    assert app_config['name']['value']['value'] == "TestApp"
    assert app_config['port']['value']['value'] == 8080
    assert app_config['debug']['value']['value'] is True


def test_invalid_syntax_error():
    """Test that invalid syntax raises appropriate error."""
    with pytest.raises(ConfigParseError) as exc_info:
        loads("Config { invalid syntax")
    
    error = exc_info.value
    assert error.line is not None
    assert error.column is not None
    assert "Expected" in error.message
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Add tests** for your changes

4. **Run the test suite**:
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: descriptive commit message"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request** on GitHub

### Commit Message Guidelines

Use descriptive commit messages:

```
Add support for environment variable interpolation

- Implement external environment variable loading
- Add environment variable resolution
- Include tests for various interpolation scenarios
- Update documentation with examples

Closes #123
```

### Pull Request Template

When creating a pull request, include:

- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How has this been tested?
- **Documentation**: Have docs been updated?
- **Breaking changes**: Any breaking changes?

## Feature Requests

### Current Roadmap

Priority features under consideration:

1. **Comments support**: Single-line and multi-line comments
2. **Include/import system**: File inclusion and modular configs
3. **Environment variable interpolation**: External configuration loading
4. **Expression evaluation**: Basic arithmetic and string operations
5. **Schema validation**: Built-in validation support
6. **CLI tools**: Command-line utilities for formatting and validation

### Proposing New Features

Before proposing a feature:

1. **Check existing issues** to avoid duplicates
2. **Consider the scope**: Does it fit the project goals?
3. **Think about compatibility**: Will it break existing configs?
4. **Provide use cases**: Include real-world examples

Create a feature request issue with:

- **Title**: Clear, descriptive feature name
- **Description**: Detailed explanation
- **Use cases**: Real-world scenarios
- **Proposed syntax**: Example configurations
- **Implementation notes**: Technical considerations

### Example Feature Request

```markdown
## Feature: Environment Variable Interpolation

### Description
Add support for environment variable interpolation through external configuration loading.

### Use Cases
- Database URLs with credentials from environment
- API keys and secrets management
- Environment-specific configuration values

### Proposed Approach
```cfgpp
Config {
    database_url = "postgresql://localhost:5432/myapp"
    api_key = "your-api-key-here"
    debug = false
}
```

Environment-specific values would be loaded by the application configuration system.

### Implementation Considerations
- Variable resolution at parse time vs runtime
- Default value syntax
- Error handling for missing variables
- Security considerations for secret values
```

## Bug Reports

### Before Reporting

1. **Check existing issues** for similar problems
2. **Try the latest version** to see if it's already fixed
3. **Create a minimal reproduction** of the issue

### Bug Report Template

```markdown
## Bug Report

### Description
Brief description of the issue

### Steps to Reproduce
1. Create config file with content: ...
2. Run parser with: ...
3. Observe error: ...

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- Python version: 3.x.x
- CFGPP version: x.x.x
- Operating System: Windows/Linux/macOS

### Additional Context
- Error messages
- Stack traces
- Related configuration files
```

### Debugging Information

Include relevant debugging information:

- **Full error messages** with stack traces
- **Configuration files** that cause the issue
- **Python version** and environment details
- **Steps to reproduce** the problem

## Development Guidelines

### Adding New Features

1. **Start with tests**: Write failing tests first (TDD)
2. **Implement incrementally**: Small, focused changes
3. **Update documentation**: Keep docs current
4. **Consider backwards compatibility**: Avoid breaking changes

### Performance Considerations

- **Profile before optimizing**: Use tools like `cProfile`
- **Consider memory usage**: Large configuration files
- **Benchmark changes**: Measure performance impact

### Security Considerations

- **Input validation**: Sanitize all inputs
- **Error messages**: Don't leak sensitive information
- **File access**: Validate file paths and permissions

## Getting Help

- **Documentation**: Check the [docs](README.md) first
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Contact**: Reach out to maintainers for guidance

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- **Be respectful** in all interactions
- **Be constructive** in feedback and criticism
- **Be collaborative** and help others learn
- **Be patient** with new contributors

## Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Major contribution acknowledgments
- **Documentation**: Attribution for significant contributions

Thank you for contributing to CFGPP! Your help makes this project better for everyone.
