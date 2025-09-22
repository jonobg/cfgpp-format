# CFGPP — Quickstart

Minimal instructions to install, run examples, and test.

## Setup (Windows PowerShell)
```powershell
# From repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

## CLI Examples
```powershell
# Parse example to JSON
python -m cfgpp.cli examples/complex_config.cfgpp

# As YAML (requires PyYAML)
python -m cfgpp.cli examples/complex_config.cfgpp --format yaml

# Read from stdin
echo 'AppConfig(string name="test")' | python -m cfgpp.cli -
```

## Library Usage

**New Clear API (Recommended):**
```python
from cfgpp import parse_string, parse_file

# Parse from string
parsed = parse_string('App(string name="x")')
print(parsed)

# Parse from file
parsed = parse_file('config.cfgpp')
print(parsed)
```

**Legacy API (Still works):**
```python
from cfgpp import loads, load  # Less clear naming
parsed = loads('App(string name="x")')  # Use parse_string() instead
parsed = load('config.cfgpp')           # Use parse_file() instead
```

## Tests
```powershell
pytest -q tests
```

## Notes
- Features supported: env vars `${VAR:-default}`, includes, expressions, comments, compact syntax.
