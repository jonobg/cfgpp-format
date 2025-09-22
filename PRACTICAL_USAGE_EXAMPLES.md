# CFGPP Practical Usage Examples

## 🚀 **Real-World Application Examples**

### 1. Microservice Configuration

```python
from cfgpp import parse_file, parse_string
from cfgpp.core.formatter import format_string
from cfgpp.schema import load_schema, validate_config

def load_microservice_config(service_name: str, environment: str):
    """Load and validate microservice configuration."""
    
    # Load base configuration
    base_config = parse_file(f"configs/{service_name}/base.cfgpp")
    
    # Load environment-specific overrides
    try:
        env_config = parse_file(f"configs/{service_name}/{environment}.cfgpp")
        # Merge configurations (simplified)
        merged_body = {**base_config['body'], **env_config['body']}
        config = {'body': merged_body}
    except FileNotFoundError:
        print(f"No environment config for {environment}, using base only")
        config = base_config
    
    # Validate against schema
    schema = load_schema(f"schemas/{service_name}.schema")
    validation = validate_config(config, schema)
    
    if not validation.is_valid:
        print("❌ Configuration validation failed:")
        for error in validation.get_errors():
            print(f"  - {error.message}")
        raise ValueError("Invalid configuration")
    
    print(f"✅ {service_name} configuration loaded for {environment}")
    return config

# Usage
try:
    config = load_microservice_config("user-service", "production")
    service_body = config['body']['ServiceConfig']['body']
    port = service_body['port']['value']['value']
    print(f"Service will run on port {port}")
except Exception as e:
    print(f"Failed to load configuration: {e}")
```

### 2. Configuration Template Generator

```python
from cfgpp import parse_string, parse_file
from cfgpp.core.formatter import format_string, FormatterConfig, BraceStyle

class ConfigTemplateGenerator:
    """Generate configuration templates for new services."""
    
    def __init__(self):
        self.formatter_config = FormatterConfig(
            indent_size=4,
            brace_style=BraceStyle.NEW_LINE,
            preserve_comments=True
        )
    
    def generate_service_config(self, service_name: str, port: int, database_type: str):
        """Generate a new service configuration."""
        
        template = f'''
        // Generated configuration for {service_name}
        ServiceConfig::standard(
            string name = "{service_name}",
            int port = {port},
            bool debug = false
        )
        
        // Database configuration
        DatabaseConfig::{database_type}(
            string host = "${{DATABASE_HOST:-localhost}}",
            int port = ${{DATABASE_PORT:-5432}},
            string database = "{service_name}_db",
            bool ssl_enabled = true
        )
        
        // Observability
        LoggingConfig {{
            level = "info",
            format = "json",
            outputs = ["stdout", "file:/var/log/{service_name}.log"]
        }}
        
        MetricsConfig {{
            enabled = true,
            port = {port + 1000},
            path = "/metrics"
        }}
        '''
        
        # Format the template
        formatted = format_string(template.strip(), self.formatter_config)
        return formatted
    
    def save_template(self, service_name: str, port: int, database_type: str):
        """Save generated template to file."""
        config_content = self.generate_service_config(service_name, port, database_type)
        
        filename = f"configs/{service_name}/base.cfgpp"
        with open(filename, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Generated configuration template: {filename}")
        return filename

# Usage
generator = ConfigTemplateGenerator()

# Generate different service configurations
services = [
    ("user-service", 8080, "PostgreSQL"),
    ("order-service", 8081, "MySQL"),
    ("notification-service", 8082, "Redis")
]

for service_name, port, db_type in services:
    generator.save_template(service_name, port, db_type)
```

### 3. Configuration Validation Pipeline

```python
import os
from pathlib import Path
from typing import List, Dict, Tuple
from cfgpp import parse_file
from cfgpp.schema import load_schema, validate_config
from cfgpp.core.parser import ConfigParseError

class ConfigValidationPipeline:
    """Validate all configuration files in a project."""
    
    def __init__(self, config_dir: str, schema_dir: str):
        self.config_dir = Path(config_dir)
        self.schema_dir = Path(schema_dir)
        self.results = []
    
    def find_config_files(self) -> List[Path]:
        """Find all .cfgpp files in the configuration directory."""
        return list(self.config_dir.rglob("*.cfgpp"))
    
    def find_schema_for_config(self, config_file: Path) -> Path:
        """Find matching schema file for configuration."""
        # Convention: config/service/env.cfgpp -> schema/service.schema
        service_name = config_file.parent.name
        schema_file = self.schema_dir / f"{service_name}.schema"
        return schema_file
    
    def validate_single_config(self, config_file: Path) -> Dict:
        """Validate a single configuration file."""
        result = {
            'file': config_file,
            'status': 'unknown',
            'errors': [],
            'warnings': []
        }
        
        try:
            # Parse configuration
            config = parse_file(str(config_file))
            result['status'] = 'parsed'
            
            # Find and load schema
            schema_file = self.find_schema_for_config(config_file)
            if schema_file.exists():
                schema = load_schema(str(schema_file))
                
                # Validate against schema
                validation = validate_config(config, schema)
                
                if validation.is_valid:
                    result['status'] = 'valid'
                else:
                    result['status'] = 'invalid'
                    result['errors'] = [
                        f"Line {msg.line}: {msg.message}" 
                        for msg in validation.get_errors()
                    ]
                    result['warnings'] = [
                        f"Line {msg.line}: {msg.message}" 
                        for msg in validation.get_warnings()
                    ]
            else:
                result['status'] = 'no_schema'
                result['warnings'].append(f"No schema found: {schema_file}")
                
        except ConfigParseError as e:
            result['status'] = 'parse_error'
            result['errors'].append(f"Parse error at line {e.line}: {e.message}")
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(f"Unexpected error: {str(e)}")
        
        return result
    
    def validate_all(self) -> Dict:
        """Validate all configuration files."""
        config_files = self.find_config_files()
        
        print(f"🔍 Found {len(config_files)} configuration files")
        
        valid_count = 0
        invalid_count = 0
        error_count = 0
        
        for config_file in config_files:
            result = self.validate_single_config(config_file)
            self.results.append(result)
            
            rel_path = config_file.relative_to(self.config_dir)
            
            if result['status'] == 'valid':
                print(f"✅ {rel_path}")
                valid_count += 1
            elif result['status'] == 'invalid':
                print(f"⚠️  {rel_path} - Validation issues")
                for error in result['errors']:
                    print(f"   ❌ {error}")
                for warning in result['warnings']:
                    print(f"   ⚠️  {warning}")
                invalid_count += 1
            else:
                print(f"❌ {rel_path} - {result['status']}")
                for error in result['errors']:
                    print(f"   ❌ {error}")
                error_count += 1
        
        summary = {
            'total': len(config_files),
            'valid': valid_count,
            'invalid': invalid_count,
            'errors': error_count,
            'results': self.results
        }
        
        print(f"\n📊 Validation Summary:")
        print(f"   Total files: {summary['total']}")
        print(f"   ✅ Valid: {summary['valid']}")
        print(f"   ⚠️  Invalid: {summary['invalid']}")
        print(f"   ❌ Errors: {summary['errors']}")
        
        return summary

# Usage
pipeline = ConfigValidationPipeline("./configs", "./schemas")
summary = pipeline.validate_all()

# Exit with error code if any validation failed
if summary['invalid'] > 0 or summary['errors'] > 0:
    exit(1)
else:
    print("🎉 All configurations valid!")
```

### 4. Configuration Migration Tool

```python
from cfgpp import parse_file, parse_string
from cfgpp.core.formatter import format_string
from pathlib import Path
import json

class ConfigMigrationTool:
    """Migrate configurations between different formats and versions."""
    
    def json_to_cfgpp(self, json_file: str) -> str:
        """Convert JSON configuration to CFGPP format."""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        return self._json_to_cfgpp_recursive(data, "Config")
    
    def _json_to_cfgpp_recursive(self, data, name: str, indent: int = 0) -> str:
        """Recursively convert JSON to CFGPP."""
        if isinstance(data, dict):
            lines = [f"{name} {{"]
            for key, value in data.items():
                if isinstance(value, dict):
                    nested = self._json_to_cfgpp_recursive(value, key, indent + 1)
                    lines.append(f"    {nested}")
                elif isinstance(value, list):
                    list_str = str(value).replace("'", '"')
                    lines.append(f"    {key} = {list_str},")
                elif isinstance(value, str):
                    lines.append(f'    {key} = "{value}",')
                else:
                    lines.append(f"    {key} = {str(value).lower()},")
            lines.append("}")
            return "\\n".join(lines)
        else:
            return str(data)
    
    def cfgpp_to_json(self, cfgpp_file: str) -> dict:
        """Convert CFGPP configuration to JSON."""
        config = parse_file(cfgpp_file)
        return self._cfgpp_to_json_recursive(config['body'])
    
    def _cfgpp_to_json_recursive(self, data) -> dict:
        """Recursively convert CFGPP AST to JSON."""
        result = {}
        
        for key, value in data.items():
            if 'body' in value and isinstance(value['body'], dict):
                # Nested object
                result[key] = self._cfgpp_to_json_recursive(value['body'])
            elif 'value' in value and 'value' in value['value']:
                # Simple value
                result[key] = value['value']['value']
        
        return result
    
    def upgrade_v1_to_v2(self, config_file: str) -> str:
        """Upgrade configuration from v1 to v2 format."""
        config = parse_file(config_file)
        
        # V2 changes: Add version field, rename 'server' to 'service'
        v2_config = '''
        // Upgraded to configuration format v2
        ConfigVersion = "2.0"
        
        '''
        
        # Process existing configuration
        for obj_name, obj_data in config['body'].items():
            if obj_name == "ServerConfig":
                # Rename ServerConfig to ServiceConfig in v2
                v2_config += f"ServiceConfig {{\n"
                if 'body' in obj_data:
                    for prop_name, prop_data in obj_data['body'].items():
                        if 'value' in prop_data and 'value' in prop_data['value']:
                            value = prop_data['value']['value']
                            if isinstance(value, str):
                                v2_config += f'    {prop_name} = "{value}",\\n'
                            else:
                                v2_config += f"    {prop_name} = {str(value).lower()},\\n"
                v2_config += "}\\n\\n"
            else:
                # Keep other objects as-is
                # ... (implement full migration logic)
                pass
        
        return format_string(v2_config)

# Usage Examples
migrator = ConfigMigrationTool()

# Convert JSON to CFGPP
json_config = migrator.json_to_cfgpp("legacy_config.json")
print(json_config)

# Convert CFGPP to JSON for API usage
json_data = migrator.cfgpp_to_json("app.cfgpp")
print(json.dumps(json_data, indent=2))

# Upgrade configuration format
upgraded = migrator.upgrade_v1_to_v2("old_config.cfgpp")
with open("new_config.cfgpp", "w") as f:
    f.write(upgraded)
print("✅ Configuration upgraded to v2")
```

### 5. AI-Powered Configuration Assistant

```python
from cfgpp import parse_string, parse_file
from cfgpp.ai import FeatureFlags, loads_with_extensions, explain_config, query_config

class ConfigurationAssistant:
    """AI-powered configuration analysis and assistance."""
    
    def __init__(self):
        # Enable AI features
        FeatureFlags.HIERARCHICAL_PARSING = True
        FeatureFlags.AI_REASONING_MODES = True
    
    def analyze_configuration(self, config_file: str):
        """Provide AI-powered analysis of configuration."""
        print(f"🤖 Analyzing {config_file} with AI assistance...")
        
        # Load with AI extensions
        config = loads_with_extensions(open(config_file).read())
        
        # Generate explanation
        explanation = explain_config(config)
        print(f"\\n📋 Configuration Summary:")
        print(explanation)
        
        # Query specific aspects
        queries = [
            "What databases are configured?",
            "What are the security settings?",
            "What ports are being used?",
            "Are there any potential issues?"
        ]
        
        print(f"\\n❓ AI Queries:")
        for question in queries:
            answer = query_config(config, question)
            if answer:
                print(f"Q: {question}")
                print(f"A: {answer}\\n")
    
    def suggest_improvements(self, config_text: str):
        """Suggest configuration improvements."""
        config = loads_with_extensions(config_text)
        
        suggestions = []
        
        # Check for common issues
        if '_hierarchical_view' in config:
            tree = config['_hierarchical_view']
            
            # Check for hardcoded values that should be environment variables
            for node in tree.get_all_nodes():
                if node.node_type == "property" and isinstance(node.value, str):
                    if "localhost" in node.value:
                        suggestions.append(
                            f"Consider using environment variable for {node.full_path}: {node.value}"
                        )
                    elif node.value.startswith("password") or "secret" in node.value.lower():
                        suggestions.append(
                            f"⚠️  Security: Consider externalizing secret at {node.full_path}"
                        )
            
            # Check for missing required configurations
            config_types = [node.name for node in tree.children.values()]
            if "LoggingConfig" not in config_types:
                suggestions.append("💡 Consider adding LoggingConfig for better observability")
            if "MetricsConfig" not in config_types:
                suggestions.append("💡 Consider adding MetricsConfig for monitoring")
        
        return suggestions
    
    def interactive_query(self, config_file: str):
        """Interactive Q&A about configuration."""
        config = loads_with_extensions(open(config_file).read())
        
        print(f"🤖 Configuration Assistant loaded {config_file}")
        print("Ask me anything about this configuration (type 'quit' to exit):\\n")
        
        while True:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
                
            try:
                answer = query_config(config, question)
                if answer:
                    print(f"🤖 {answer}\\n")
                else:
                    print("🤖 I couldn't find information about that. Try asking differently.\\n")
            except Exception as e:
                print(f"❌ Error processing question: {e}\\n")
        
        print("👋 Thanks for using the Configuration Assistant!")

# Usage
assistant = ConfigurationAssistant()

# Analyze configuration with AI
assistant.analyze_configuration("production.cfgpp")

# Get improvement suggestions
config_text = '''
AppConfig {
    name = "MyApp",
    database_host = "localhost",
    admin_password = "secret123",
    port = 8080
}
'''

suggestions = assistant.suggest_improvements(config_text)
print("💡 Suggestions:")
for suggestion in suggestions:
    print(f"  - {suggestion}")

# Interactive mode (uncomment to try)
# assistant.interactive_query("complex_config.cfgpp")
```

## 🔧 **Development Workflow Integration**

### Git Pre-commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook to validate CFGPP configurations."""

import sys
import subprocess
from pathlib import Path
from cfgpp import parse_file
from cfgpp.core.parser import ConfigParseError

def validate_changed_configs():
    """Validate all changed .cfgpp files."""
    # Get changed files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    
    changed_files = [
        f for f in result.stdout.strip().split('\\n') 
        if f.endswith('.cfgpp')
    ]
    
    if not changed_files:
        print("✅ No CFGPP files to validate")
        return True
    
    print(f"🔍 Validating {len(changed_files)} CFGPP files...")
    
    errors = []
    for file_path in changed_files:
        try:
            parse_file(file_path)
            print(f"  ✅ {file_path}")
        except ConfigParseError as e:
            error_msg = f"  ❌ {file_path}: Parse error at line {e.line}: {e.message}"
            print(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"  ❌ {file_path}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
    
    if errors:
        print(f"\\n❌ {len(errors)} configuration files have errors:")
        for error in errors:
            print(error)
        print("\\nPlease fix these issues before committing.")
        return False
    
    print(f"\\n✅ All {len(changed_files)} CFGPP files are valid!")
    return True

if __name__ == "__main__":
    if not validate_changed_configs():
        sys.exit(1)
```

## 🚀 **Performance Optimization Examples**

### Efficient Configuration Loading

```python
import time
from typing import Dict, Any
from cfgpp import parse_file, parse_string
from functools import lru_cache

class OptimizedConfigLoader:
    """Optimized configuration loading with caching."""
    
    def __init__(self):
        self._cache = {}
        self._file_timestamps = {}
    
    @lru_cache(maxsize=100)
    def load_cached(self, file_path: str) -> Dict[str, Any]:
        """Load configuration with LRU caching."""
        return parse_file(file_path)
    
    def load_with_change_detection(self, file_path: str) -> Dict[str, Any]:
        """Load configuration only if file has changed."""
        from pathlib import Path
        import os
        
        path = Path(file_path)
        current_mtime = os.path.getmtime(path)
        
        # Check if we have cached version and if file hasn't changed
        if (file_path in self._cache and 
            file_path in self._file_timestamps and
            self._file_timestamps[file_path] == current_mtime):
            return self._cache[file_path]
        
        # File changed or not cached, reload
        config = parse_file(file_path)
        self._cache[file_path] = config
        self._file_timestamps[file_path] = current_mtime
        
        return config
    
    def benchmark_loading(self, file_path: str, iterations: int = 100):
        """Benchmark different loading strategies."""
        
        # Benchmark uncached loading
        start_time = time.time()
        for _ in range(iterations):
            parse_file(file_path)
        uncached_time = time.time() - start_time
        
        # Benchmark cached loading
        start_time = time.time()
        for _ in range(iterations):
            self.load_cached(file_path)
        cached_time = time.time() - start_time
        
        # Benchmark change detection
        start_time = time.time()
        for _ in range(iterations):
            self.load_with_change_detection(file_path)
        change_detection_time = time.time() - start_time
        
        print(f"📊 Performance Benchmark ({iterations} iterations):")
        print(f"  Uncached:         {uncached_time:.3f}s ({uncached_time/iterations*1000:.2f}ms per load)")
        print(f"  LRU Cached:       {cached_time:.3f}s ({cached_time/iterations*1000:.2f}ms per load)")
        print(f"  Change Detection: {change_detection_time:.3f}s ({change_detection_time/iterations*1000:.2f}ms per load)")
        print(f"  Speedup (cached): {uncached_time/cached_time:.1f}x faster")

# Usage
loader = OptimizedConfigLoader()
config = loader.load_with_change_detection("large_config.cfgpp")
loader.benchmark_loading("large_config.cfgpp")
```

These examples demonstrate the power and flexibility of the CFGPP system with its new clear API, showing real-world applications from simple configuration loading to AI-powered analysis and development workflow integration! 🚀
