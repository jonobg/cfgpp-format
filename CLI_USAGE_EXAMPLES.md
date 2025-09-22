# CFGPP CLI Usage Examples

## 🚀 **Command Line Interface Examples**

### Basic Parsing Commands

```bash
# Parse configuration file to JSON
python -m cfgpp.tools.cli.cli config.cfgpp

# Parse with verbose output
python -m cfgpp.tools.cli.cli config.cfgpp --verbose

# Parse and format as YAML (requires PyYAML)
python -m cfgpp.tools.cli.cli config.cfgpp --format yaml

# Parse and format as compact JSON
python -m cfgpp.tools.cli.cli config.cfgpp --format compact

# Parse from stdin
echo "App { name = 'test' }" | python -m cfgpp.tools.cli.cli --stdin

# Parse from stdin with custom format
cat config.cfgpp | python -m cfgpp.tools.cli.cli --stdin --format yaml
```

### Validation Commands

```bash
# Validate configuration syntax only
python -m cfgpp.tools.cli.cli config.cfgpp --validate

# Validate with detailed output
python -m cfgpp.tools.cli.cli config.cfgpp --validate --verbose

# Validate multiple files
python -m cfgpp.tools.cli.cli --validate configs/*.cfgpp
```

### Schema Operations

```bash
# Validate configuration against schema
python -m cfgpp.tools.cli.cli config.cfgpp schema validate --schema app.schema

# Generate schema from configuration
python -m cfgpp.tools.cli.cli config.cfgpp schema generate --output generated.schema

# Check schema compatibility
python -m cfgpp.tools.cli.cli config.cfgpp schema check --schema app.schema
```

### Formatting Commands

```bash
# Format configuration file in place
python -m cfgpp.tools.cli.cli config.cfgpp format --in-place

# Format with custom style
python -m cfgpp.tools.cli.cli config.cfgpp format --style compact

# Format and save to new file
python -m cfgpp.tools.cli.cli config.cfgpp format --output formatted.cfgpp

# Format with schema-aware formatting
python -m cfgpp.tools.cli.cli config.cfgpp format --schema app.schema
```

## 📁 **Project Workflow Examples**

### 1. Development Workflow

```bash
#!/bin/bash
# dev-workflow.sh - Development workflow script

# Validate all configuration files
echo "🔍 Validating configurations..."
find configs/ -name "*.cfgpp" -exec python -m cfgpp.tools.cli.cli {} --validate \;

# Format all configuration files
echo "🎨 Formatting configurations..."
find configs/ -name "*.cfgpp" -exec python -m cfgpp.tools.cli.cli {} format --in-place \;

# Generate documentation from configurations
echo "📚 Generating documentation..."
for config in configs/*.cfgpp; do
    python -m cfgpp.tools.cli.cli "$config" --format yaml > "docs/$(basename "$config" .cfgpp).yaml"
done

echo "✅ Development workflow complete!"
```

### 2. CI/CD Pipeline Integration

```yaml
# .github/workflows/validate-configs.yml
name: Validate Configurations

on:
  push:
    paths:
      - 'configs/**/*.cfgpp'
      - 'schemas/**/*.schema'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install CFGPP
        run: |
          cd implementations/python
          pip install -e .
      
      - name: Validate Configuration Syntax
        run: |
          find configs/ -name "*.cfgpp" -exec python -m cfgpp.tools.cli.cli {} --validate \;
      
      - name: Validate Against Schemas
        run: |
          for config in configs/**/*.cfgpp; do
            service=$(basename $(dirname "$config"))
            if [ -f "schemas/${service}.schema" ]; then
              python -m cfgpp.tools.cli.cli "$config" schema validate --schema "schemas/${service}.schema"
            fi
          done
      
      - name: Check Formatting
        run: |
          # Check if any files need formatting
          for config in configs/**/*.cfgpp; do
            original=$(cat "$config")
            formatted=$(python -m cfgpp.tools.cli.cli "$config" format)
            if [ "$original" != "$formatted" ]; then
              echo "❌ $config needs formatting"
              exit 1
            fi
          done
          echo "✅ All files properly formatted"
```

### 3. Configuration Migration Script

```bash
#!/bin/bash
# migrate-configs.sh - Migrate configurations to new format

BACKUP_DIR="config_backup_$(date +%Y%m%d_%H%M%S)"

echo "🔄 Starting configuration migration..."

# Create backup
echo "💾 Creating backup in $BACKUP_DIR..."
cp -r configs/ "$BACKUP_DIR/"

# Migrate each configuration
for config in configs/**/*.cfgpp; do
    echo "🔄 Migrating $config..."
    
    # Parse current configuration
    python -m cfgpp.tools.cli.cli "$config" --format json > temp_config.json
    
    # Apply migration transformations (example)
    python3 << EOF
import json
import sys

with open('temp_config.json', 'r') as f:
    data = json.load(f)

# Migration logic here (example: rename ServerConfig to ServiceConfig)
if 'body' in data and 'ServerConfig' in data['body']:
    data['body']['ServiceConfig'] = data['body'].pop('ServerConfig')
    print(f"✅ Migrated ServerConfig to ServiceConfig in $config")

with open('temp_config.json', 'w') as f:
    json.dump(data, f, indent=2)
EOF
    
    # Convert back to CFGPP and format
    # (This would require a JSON to CFGPP converter)
    # python json_to_cfgpp.py temp_config.json > "$config"
    # python -m cfgpp.tools.cli.cli "$config" format --in-place
done

# Cleanup
rm -f temp_config.json

echo "✅ Migration complete! Backup available in $BACKUP_DIR"
```

## 🛠 **Advanced CLI Usage**

### 1. Configuration Analysis Script

```python
#!/usr/bin/env python3
"""Advanced configuration analysis using CLI tools."""

import subprocess
import json
import sys
from pathlib import Path

def analyze_config(config_file: str):
    """Analyze configuration file using CLI tools."""
    
    print(f"📊 Analyzing {config_file}...")
    
    # Parse configuration
    result = subprocess.run([
        sys.executable, "-m", "cfgpp.tools.cli.cli",
        config_file, "--format", "json"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to parse {config_file}: {result.stderr}")
        return
    
    config_data = json.loads(result.stdout)
    
    # Analyze structure
    def analyze_structure(data, path=""):
        """Recursively analyze configuration structure."""
        stats = {
            'objects': 0,
            'properties': 0,
            'arrays': 0,
            'depth': 0
        }
        
        if isinstance(data, dict):
            if 'body' in data and isinstance(data['body'], dict):
                stats['objects'] += 1
                for key, value in data['body'].items():
                    sub_stats = analyze_structure(value, f"{path}.{key}")
                    stats['objects'] += sub_stats['objects']
                    stats['properties'] += sub_stats['properties']
                    stats['arrays'] += sub_stats['arrays']
                    stats['depth'] = max(stats['depth'], sub_stats['depth'] + 1)
            elif 'value' in data:
                stats['properties'] += 1
                if data.get('is_array', False):
                    stats['arrays'] += 1
        
        return stats
    
    if 'body' in config_data:
        stats = analyze_structure(config_data)
        
        print(f"  📈 Structure Statistics:")
        print(f"    Objects: {stats['objects']}")
        print(f"    Properties: {stats['properties']}")
        print(f"    Arrays: {stats['arrays']}")
        print(f"    Max Depth: {stats['depth']}")
        
        # Check for potential issues
        issues = []
        if stats['depth'] > 10:
            issues.append("Very deep nesting detected (>10 levels)")
        if stats['objects'] > 50:
            issues.append("Large number of objects (>50)")
        
        if issues:
            print(f"  ⚠️  Potential Issues:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  ✅ No structural issues detected")

def main():
    """Main analysis function."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_configs.py <config_files...>")
        sys.exit(1)
    
    config_files = sys.argv[1:]
    
    print(f"🔍 Analyzing {len(config_files)} configuration files...")
    
    for config_file in config_files:
        if Path(config_file).exists():
            analyze_config(config_file)
        else:
            print(f"❌ File not found: {config_file}")
    
    print("📊 Analysis complete!")

if __name__ == "__main__":
    main()
```

### 2. Configuration Deployment Script

```bash
#!/bin/bash
# deploy-configs.sh - Deploy configurations to different environments

ENVIRONMENT="${1:-development}"
CONFIG_DIR="configs"
DEPLOYMENT_TARGET="${2:-/etc/myapp}"

echo "🚀 Deploying configurations for environment: $ENVIRONMENT"

# Validate configurations before deployment
echo "🔍 Validating configurations..."
validation_failed=false

for config in "$CONFIG_DIR"/**/*.cfgpp; do
    if ! python -m cfgpp.tools.cli.cli "$config" --validate --quiet; then
        echo "❌ Validation failed for $config"
        validation_failed=true
    fi
done

if [ "$validation_failed" = true ]; then
    echo "❌ Deployment aborted due to validation failures"
    exit 1
fi

echo "✅ All configurations validated successfully"

# Process environment-specific configurations
echo "🔄 Processing environment-specific configurations..."

for config in "$CONFIG_DIR"/**/*.cfgpp; do
    # Extract service name from path
    service=$(basename "$(dirname "$config")")
    config_name=$(basename "$config" .cfgpp)
    
    # Check if environment-specific config exists
    env_config="$CONFIG_DIR/$service/${ENVIRONMENT}.cfgpp"
    
    if [ -f "$env_config" ]; then
        echo "📝 Using environment-specific config: $env_config"
        source_config="$env_config"
    else
        echo "📝 Using base config: $config"
        source_config="$config"
    fi
    
    # Convert to JSON for deployment
    output_file="$DEPLOYMENT_TARGET/$service-$config_name.json"
    
    echo "📤 Deploying $source_config -> $output_file"
    
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$output_file")"
    
    # Convert and deploy
    if python -m cfgpp.tools.cli.cli "$source_config" --format json > "$output_file"; then
        echo "✅ Successfully deployed $output_file"
    else
        echo "❌ Failed to deploy $source_config"
        exit 1
    fi
done

echo "🎉 Deployment to $ENVIRONMENT complete!"

# Optional: Restart services
if [ "$3" = "--restart-services" ]; then
    echo "🔄 Restarting services..."
    # Add service restart logic here
    systemctl reload myapp || echo "⚠️ Failed to reload myapp service"
fi
```

### 3. Configuration Monitoring Script

```python
#!/usr/bin/env python3
"""Monitor configuration files for changes and validate them."""

import time
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigurationHandler(FileSystemEventHandler):
    """Handle configuration file changes."""
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.cfgpp'):
            return
        
        print(f"🔄 Configuration changed: {event.src_path}")
        self.validate_config(event.src_path)
    
    def validate_config(self, file_path: str):
        """Validate a configuration file."""
        try:
            # Validate syntax
            result = subprocess.run([
                sys.executable, "-m", "cfgpp.tools.cli.cli",
                file_path, "--validate", "--quiet"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {file_path} is valid")
                
                # Auto-format if requested
                if hasattr(self, 'auto_format') and self.auto_format:
                    format_result = subprocess.run([
                        sys.executable, "-m", "cfgpp.tools.cli.cli",
                        file_path, "format", "--in-place"
                    ], capture_output=True, text=True)
                    
                    if format_result.returncode == 0:
                        print(f"🎨 Auto-formatted {file_path}")
                    else:
                        print(f"⚠️ Failed to format {file_path}")
            else:
                print(f"❌ {file_path} has validation errors:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error validating {file_path}: {e}")

def main():
    """Main monitoring function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor CFGPP configuration files")
    parser.add_argument("directory", help="Directory to monitor")
    parser.add_argument("--auto-format", action="store_true", 
                       help="Automatically format files on change")
    
    args = parser.parse_args()
    
    if not Path(args.directory).exists():
        print(f"❌ Directory not found: {args.directory}")
        sys.exit(1)
    
    # Set up file system watcher
    event_handler = ConfigurationHandler()
    event_handler.auto_format = args.auto_format
    
    observer = Observer()
    observer.schedule(event_handler, args.directory, recursive=True)
    
    print(f"👀 Monitoring {args.directory} for CFGPP configuration changes...")
    if args.auto_format:
        print("✨ Auto-formatting enabled")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\\n👋 Monitoring stopped")
    
    observer.join()

if __name__ == "__main__":
    main()
```

## 🎯 **CLI Integration Examples**

### Makefile Integration

```makefile
# Makefile for CFGPP project

.PHONY: validate-configs format-configs deploy-dev deploy-prod

PYTHON := python
CFGPP_CLI := $(PYTHON) -m cfgpp.tools.cli.cli
CONFIG_DIR := configs
SCHEMA_DIR := schemas

# Validate all configuration files
validate-configs:
	@echo "🔍 Validating configuration files..."
	@find $(CONFIG_DIR) -name "*.cfgpp" -exec $(CFGPP_CLI) {} --validate \;
	@echo "✅ All configurations validated"

# Format all configuration files
format-configs:
	@echo "🎨 Formatting configuration files..."
	@find $(CONFIG_DIR) -name "*.cfgpp" -exec $(CFGPP_CLI) {} format --in-place \;
	@echo "✅ All configurations formatted"

# Validate against schemas
validate-schemas:
	@echo "🔍 Validating configurations against schemas..."
	@for config in $(CONFIG_DIR)/**/*.cfgpp; do \
		service=$$(basename $$(dirname "$$config")); \
		if [ -f "$(SCHEMA_DIR)/$$service.schema" ]; then \
			$(CFGPP_CLI) "$$config" schema validate --schema "$(SCHEMA_DIR)/$$service.schema"; \
		fi; \
	done
	@echo "✅ Schema validation complete"

# Deploy to development
deploy-dev:
	@echo "🚀 Deploying to development..."
	@./scripts/deploy-configs.sh development /etc/myapp-dev
	@echo "✅ Development deployment complete"

# Deploy to production
deploy-prod:
	@echo "🚀 Deploying to production..."
	@make validate-configs
	@make validate-schemas
	@./scripts/deploy-configs.sh production /etc/myapp-prod --restart-services
	@echo "✅ Production deployment complete"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	@rm -f temp_*.json
	@rm -rf config_backup_*
	@echo "✅ Cleanup complete"
```

These comprehensive examples show how the CFGPP CLI can be integrated into real-world development workflows, from simple parsing to complex deployment pipelines! 🚀
