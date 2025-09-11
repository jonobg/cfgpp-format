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
```python
from cfgpp.parser import loads
parsed = loads('App(string name="x")')
print(parsed)
```

## Tests
```powershell
pytest -q tests
```

## Notes
- Features supported: env vars `${VAR:-default}`, includes, expressions, comments, compact syntax.
