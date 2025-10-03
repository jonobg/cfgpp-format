# Build script for CFG++ VS Code Extension
# Creates separate VSIX files for VS Code Marketplace and Open VSX Registry

Write-Host "🎯 Building CFG++ VS Code Extensions for Both Marketplaces" -ForegroundColor Green

# Check if vsce is installed
if (-not (Get-Command vsce -ErrorAction SilentlyContinue)) {
    Write-Host "❌ vsce not found. Installing..." -ForegroundColor Red
    npm install -g vsce
}

# Check if ovsx is installed
if (-not (Get-Command ovsx -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ovsx not found. Installing..." -ForegroundColor Red
    npm install -g ovsx
}

# Compile TypeScript
Write-Host "🔧 Compiling TypeScript..." -ForegroundColor Yellow
npm run compile

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ TypeScript compilation failed!" -ForegroundColor Red
    exit 1
}

# Build for VS Code Marketplace (publisher: cfgpp-format)
Write-Host "📦 Building VSIX for VS Code Marketplace (publisher: cfgpp-format)..." -ForegroundColor Yellow
vsce package --out "cfgpp-language-support-vscode-1.2.1.vsix"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ VS Code Marketplace VSIX build failed!" -ForegroundColor Red
    exit 1
}

# Backup current package.json and switch to Open VSX version
Write-Host "🔄 Switching to Open VSX configuration..." -ForegroundColor Yellow
Copy-Item "package.json" "package-vscode.json.bak"
Copy-Item "package-openvsx.json" "package.json"

# Build for Open VSX Registry (publisher: cfgpp)
Write-Host "📦 Building VSIX for Open VSX Registry (publisher: cfgpp)..." -ForegroundColor Yellow
vsce package --out "cfgpp-language-support-openvsx-1.2.1.vsix"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Open VSX VSIX build failed!" -ForegroundColor Red
    # Restore original package.json
    Copy-Item "package-vscode.json.bak" "package.json"
    Remove-Item "package-vscode.json.bak"
    exit 1
}

# Restore original package.json
Write-Host "🔄 Restoring VS Code Marketplace configuration..." -ForegroundColor Yellow
Copy-Item "package-vscode.json.bak" "package.json"
Remove-Item "package-vscode.json.bak"

Write-Host "✅ Both VSIX files built successfully!" -ForegroundColor Green
Write-Host "📁 Files created:" -ForegroundColor Cyan
Write-Host "   • cfgpp-language-support-vscode-1.2.1.vsix (for VS Code Marketplace)" -ForegroundColor White
Write-Host "   • cfgpp-language-support-openvsx-1.2.1.vsix (for Open VSX Registry)" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Green
Write-Host "1. Publish to VS Code Marketplace:" -ForegroundColor Yellow
Write-Host "   vsce publish --packagePath cfgpp-language-support-vscode-1.2.1.vsix" -ForegroundColor White
Write-Host ""
Write-Host "2. Publish to Open VSX Registry:" -ForegroundColor Yellow
Write-Host "   ovsx publish cfgpp-language-support-openvsx-1.2.1.vsix" -ForegroundColor White
Write-Host ""
Write-Host "🌲 Swedish Forest Note: Another VS Code extension? Probably useful for CFG++ files." -ForegroundColor DarkGreen
