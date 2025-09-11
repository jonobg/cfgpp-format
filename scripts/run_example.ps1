param(
    [string]$File = "examples/complex_config.cfgpp",
    [ValidateSet("json","yaml")]
    [string]$Format = "json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# From repo root
Write-Host "==> Parsing $File as $Format" -ForegroundColor Cyan
if ($Format -eq "yaml") {
    python -m cfgpp.cli $File --format yaml
} else {
    python -m cfgpp.cli $File
}
