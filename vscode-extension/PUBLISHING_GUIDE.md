# CFG++ VS Code Extension Publishing Guide

## 🎯 **Marketplace Strategy**

We publish to **both marketplaces** to maximize user reach:

- **VS Code Marketplace** (70% of users) - Publisher: `cfgpp-format`
- **Open VSX Registry** (30% of users) - Publisher: `cfgpp`

## 📦 **Built VSIX Files**

- `cfgpp-language-support-vscode-1.2.1.vsix` - For VS Code Marketplace
- `cfgpp-language-support-openvsx-1.2.1.vsix` - For Open VSX Registry

## 🚀 **Publishing Commands**

### 1. Publish to VS Code Marketplace

```bash
# First time setup (if needed)
vsce login cfgpp-format

# Publish the extension
vsce publish --packagePath cfgpp-language-support-vscode-1.2.1.vsix
```

### 2. Publish to Open VSX Registry

```bash
# First time setup (if needed)
npx ovsx create-namespace cfgpp

# Publish the extension
npx ovsx publish cfgpp-language-support-openvsx-1.2.1.vsix -p YOUR_OPENVSX_TOKEN
```

## 🔑 **Authentication Setup**

### VS Code Marketplace
1. Go to [Azure DevOps](https://dev.azure.com/)
2. Create a Personal Access Token with **Marketplace** scope
3. Run: `vsce login cfgpp-format`
4. Enter your token when prompted

### Open VSX Registry
1. Go to [Open VSX Registry](https://open-vsx.org/)
2. Sign in with GitHub
3. Generate an access token
4. Use token with `npx ovsx publish` command

## 📋 **Pre-Publishing Checklist**

- [ ] **Version updated** in both package.json files
- [ ] **CHANGELOG.md updated** with new features
- [ ] **README.md** uses Swedish Forest methodology
- [ ] **Extension tested** locally with `F5` in VS Code
- [ ] **Both VSIX files built** successfully
- [ ] **No experimental features** in stable release

## 🌲 **Swedish Forest Publishing Philosophy**

### Extension Description
```
"Language support for CFG++ configuration files. Another config format? 
Probably useful for large configurations where JSON becomes unwieldy. 
Provides syntax highlighting, validation, and auto-completion."
```

### Honest Feature Claims
- ✅ **What works**: Syntax highlighting, basic validation, auto-completion
- ❌ **Don't claim**: "Revolutionary", "game-changing", "world's best"
- ✅ **Be realistic**: "Might be useful for complex configurations"

## 📊 **Post-Publishing Verification**

### VS Code Marketplace
1. Visit: `https://marketplace.visualstudio.com/items?itemName=cfgpp-format.cfgpp-language-support`
2. Verify extension appears correctly
3. Test installation: `code --install-extension cfgpp-format.cfgpp-language-support`

### Open VSX Registry  
1. Visit: `https://open-vsx.org/extension/cfgpp/cfgpp-language-support`
2. Verify extension appears correctly
3. Test installation in compatible editors

## 🔄 **Update Process**

1. **Update version** in both `package.json` and `package-openvsx.json`
2. **Run build script**: `powershell -ExecutionPolicy Bypass -File build-extensions.ps1`
3. **Test both VSIX files** locally
4. **Publish to both marketplaces** using commands above
5. **Update documentation** with new marketplace links

## 🚨 **Critical Notes**

- **Different publishers** required due to namespace conflicts
- **Same functionality** in both versions
- **Version numbers** must stay synchronized
- **Swedish Forest tone** maintained in all descriptions
- **No experimental features** in marketplace releases

## 📈 **Success Metrics**

- **VS Code Marketplace**: Monitor downloads, ratings, reviews
- **Open VSX Registry**: Track adoption in alternative editors
- **Combined reach**: Maximize CFG++ format adoption
- **User feedback**: Honest reviews help improve the extension

---

**🌲 Swedish Forest Note**: Another VS Code extension publishing guide? Probably useful if you're maintaining extensions across multiple marketplaces and want to avoid the naming confusion we just solved.
