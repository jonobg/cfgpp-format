#!/usr/bin/env python
"""
CFGPP MCP server exposing parse tools for the cfgpp-format project.
Requires: `pip install mcp fastmcp` and project dependencies installed in the environment.

Tools:
- parse_text(text: str, format: str = "json") -> dict | str
- parse_file(path: str, format: str = "json") -> dict | str

`format` can be "json" or "yaml" (requires PyYAML for yaml output).
"""
from typing import Any
import json
import os

try:
    from fastmcp import FastMCP
except Exception:
    raise SystemExit("fastmcp not installed. Run: pip install fastmcp")

try:
    from cfgpp.parser import loads
except Exception:
    raise SystemExit(
        "cfgpp is not importable. Activate your venv and install the package with 'pip install -e .'"
    )

app = FastMCP("cfgpp-server", version="0.1.0")


def _to_output(data: Any, fmt: str) -> Any:
    fmt = (fmt or "json").lower()
    if fmt == "json":
        return data  # client can render JSON directly
    if fmt == "yaml":
        try:
            import yaml  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("PyYAML is not installed. Run: pip install pyyaml") from e
        return yaml.safe_dump(data, sort_keys=False)
    raise ValueError("format must be 'json' or 'yaml'")


@app.tool()
def parse_text(text: str, format: str = "json") -> Any:
    """Parse CFGPP text and return JSON or YAML.

    Parameters
    ----------
    text: str
        CFGPP document text.
    format: str
        'json' (default) or 'yaml'.
    """
    parsed = loads(text)
    return _to_output(parsed, format)


@app.tool()
def parse_file(path: str, format: str = "json") -> Any:
    """Parse a CFGPP file and return JSON or YAML.

    Parameters
    ----------
    path: str
        Path to a .cfgpp file.
    format: str
        'json' (default) or 'yaml'.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    parsed = loads(text)
    return _to_output(parsed, format)


if __name__ == "__main__":
    app.run()
