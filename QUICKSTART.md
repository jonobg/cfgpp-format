# CFG++ — Quickstart

Minimal instructions to install, run examples, and test.

## Setup
```bash
# From repo root
cd implementations/python
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -e .
```

## CLI Examples
```bash
# Parse example to JSON
python -m cfgpp specification/examples/advanced/complex-config.cfgpp

# As YAML (requires PyYAML)
python -m cfgpp specification/examples/advanced/complex-config.cfgpp --format yaml

# Read from stdin
echo 'AppConfig { name = "test" }' | python -m cfgpp -
```

## Library Usage
```python
from cfgpp import parse_string, parse_file

# Parse from string
parsed = parse_string('App { name = "hello" }')
print(parsed)

# Parse from file
parsed = parse_file('config.cfgpp')
print(parsed)

# Legacy aliases also work
from cfgpp import loads, load
```

## Tests
```bash
cd implementations/python
python -m pytest tests/ -v
# Expected: 98 tests passing
```

## Notes
- Features supported: typed objects, namespaced identifiers (`Type::instance`), arrays, comments (`//` and `/* */`), constructor syntax with `()` and block syntax with `{}`.
