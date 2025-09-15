#!/usr/bin/env python3
"""
Integration module for schema-aware parsing in cfgpp-format.

This module provides the main interface for schema-integrated parsing,
combining the configuration parser with schema validation for enhanced
developer experience.

# REASONING: Schema integration enables seamless schema-aware parsing for integration workflows.
# Integration workflows require schema integration for seamless schema-aware parsing in integration workflows.
# Schema integration supports seamless schema-aware parsing, developer experience, and integration coordination while enabling
# comprehensive integration strategies and systematic schema-driven parsing workflows.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import os
from pathlib import Path

from .parser import loads as config_loads, ConfigParseError
from .schema_parser import loads_schema, load_schema, SchemaDocument, SchemaParseError
from .schema_validator import validate_config, ValidationResult, ValidationMessage, ValidationSeverity


class SchemaAwareParser:
    """
    Schema-aware configuration parser that combines parsing and validation.
    
    # REASONING: Schema-aware parsing enables integrated validation and enhanced error reporting for parsing workflows.
    # Parsing workflows require schema-aware parsing for integrated validation and enhanced error reporting in parsing workflows.
    # Schema-aware parsing supports integrated validation, enhanced error reporting, and parsing coordination while enabling
    # comprehensive parsing strategies and systematic schema-integrated parsing workflows.
    """
    
    def __init__(self, schema_doc: Optional[SchemaDocument] = None, schema_path: Optional[str] = None):
        """
        Initialize the schema-aware parser.
        
        Args:
            schema_doc: Pre-loaded schema document
            schema_path: Path to schema file to load
        """
        if schema_doc is not None:
            self.schema_doc = schema_doc
        elif schema_path is not None:
            self.schema_doc = load_schema(schema_path)
        else:
            self.schema_doc = None
    
    def parse(self, config_text: str, schema_name: Optional[str] = None, 
              validate: bool = True) -> Tuple[Dict[str, Any], Optional[ValidationResult]]:
        """
        Parse configuration with optional schema validation.
        
        Args:
            config_text: The configuration text to parse
            schema_name: Optional schema name for validation
            validate: Whether to perform schema validation
            
        Returns:
            Tuple of (parsed_config, validation_result)
            
        Raises:
            ConfigParseError: If configuration parsing fails
            SchemaParseError: If schema is invalid
        """
        # Parse the configuration
        config_data = config_loads(config_text)
        
        # Perform schema validation if requested and schema is available
        validation_result = None
        if validate and self.schema_doc is not None:
            validation_result = validate_config(config_data, self.schema_doc, schema_name)
        
        return config_data, validation_result
    
    def parse_with_enhanced_errors(self, config_text: str, schema_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse configuration with enhanced error messages from schema validation.
        
        Args:
            config_text: The configuration text to parse
            schema_name: Optional schema name for validation
            
        Returns:
            Dict: The parsed configuration data
            
        Raises:
            ConfigParseError: If parsing fails, potentially with enhanced error messages
        """
        try:
            config_data, validation_result = self.parse(config_text, schema_name, validate=True)
            
            # If validation failed, enhance the error message
            if validation_result and validation_result.has_errors():
                error_messages = []
                for msg in validation_result.get_errors():
                    error_line = f"  {msg.path}: {msg.message}"
                    if msg.suggestion:
                        error_line += f" (Suggestion: {msg.suggestion})"
                    error_messages.append(error_line)
                
                enhanced_message = "Configuration validation failed:\n" + "\n".join(error_messages)
                raise ConfigParseError(enhanced_message, 0, 0)
            
            return config_data
            
        except ConfigParseError:
            # Re-raise parsing errors as-is
            raise


def loads_with_schema(config_text: str, schema_text: Optional[str] = None, 
                     schema_path: Optional[str] = None, schema_name: Optional[str] = None,
                     validate: bool = True) -> Tuple[Dict[str, Any], Optional[ValidationResult]]:
    """
    Parse configuration text with optional schema validation.
    
    Args:
        config_text: The configuration text to parse
        schema_text: Optional schema text to validate against
        schema_path: Optional path to schema file
        schema_name: Optional specific schema name for validation
        validate: Whether to perform validation
        
    Returns:
        Tuple of (parsed_config, validation_result)
        
    Raises:
        ConfigParseError: If configuration parsing fails
        SchemaParseError: If schema parsing fails
    """
    # Load schema if provided
    schema_doc = None
    if schema_text is not None:
        schema_doc = loads_schema(schema_text)
    elif schema_path is not None:
        schema_doc = load_schema(schema_path)
    
    # Create parser and parse
    parser = SchemaAwareParser(schema_doc=schema_doc)
    return parser.parse(config_text, schema_name, validate)


def auto_discover_schema(config_path: str) -> Optional[str]:
    """
    Auto-discover schema file for a configuration file.
    
    Looks for schema files in the following order:
    1. {config_name}.cfgpp-schema (same directory)
    2. schema/{config_name}.cfgpp-schema
    3. {config_name}-schema.cfgpp-schema
    4. schema.cfgpp-schema (generic schema in same directory)
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        str or None: Path to discovered schema file, or None if not found
    """
    config_path = Path(config_path)
    config_dir = config_path.parent
    config_stem = config_path.stem
    
    # Candidate schema paths
    candidates = [
        config_dir / f"{config_stem}.cfgpp-schema",
        config_dir / "schema" / f"{config_stem}.cfgpp-schema",
        config_dir / f"{config_stem}-schema.cfgpp-schema",
        config_dir / "schema.cfgpp-schema"
    ]
    
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)
    
    return None


def load_with_auto_schema(config_path: str, schema_name: Optional[str] = None,
                         validate: bool = True) -> Tuple[Dict[str, Any], Optional[ValidationResult]]:
    """
    Load configuration file with automatic schema discovery.
    
    Args:
        config_path: Path to the configuration file
        schema_name: Optional specific schema name for validation
        validate: Whether to perform validation
        
    Returns:
        Tuple of (parsed_config, validation_result)
        
    Raises:
        ConfigParseError: If configuration parsing fails
        SchemaParseError: If schema parsing fails
        FileNotFoundError: If configuration file doesn't exist
    """
    # Read configuration file
    with open(config_path, 'r', encoding='utf-8') as f:
        config_text = f.read()
    
    # Try to auto-discover schema
    schema_path = auto_discover_schema(config_path)
    
    # Parse with discovered schema
    return loads_with_schema(
        config_text=config_text,
        schema_path=schema_path,
        schema_name=schema_name,
        validate=validate
    )


def format_validation_messages(messages: List[ValidationMessage], show_suggestions: bool = True) -> str:
    """
    Format validation messages for human-readable output.
    
    Args:
        messages: List of validation messages
        show_suggestions: Whether to include suggestions in output
        
    Returns:
        str: Formatted message string
    """
    if not messages:
        return "✅ All validation checks passed!"
    
    formatted_lines = []
    errors = [msg for msg in messages if msg.severity == ValidationSeverity.ERROR]
    warnings = [msg for msg in messages if msg.severity == ValidationSeverity.WARNING]
    infos = [msg for msg in messages if msg.severity == ValidationSeverity.INFO]
    
    if errors:
        formatted_lines.append(f"❌ {len(errors)} error(s):")
        for msg in errors:
            line = f"   • {msg.path}: {msg.message}"
            if show_suggestions and msg.suggestion:
                line += f"\n     💡 {msg.suggestion}"
            formatted_lines.append(line)
    
    if warnings:
        formatted_lines.append(f"⚠️  {len(warnings)} warning(s):")
        for msg in warnings:
            line = f"   • {msg.path}: {msg.message}"
            if show_suggestions and msg.suggestion:
                line += f"\n     💡 {msg.suggestion}"
            formatted_lines.append(line)
    
    if infos:
        formatted_lines.append(f"ℹ️  {len(infos)} info message(s):")
        for msg in infos:
            formatted_lines.append(f"   • {msg.path}: {msg.message}")
    
    return "\n".join(formatted_lines)


class SchemaRegistry:
    """
    Registry for managing multiple schema documents.
    
    # REASONING: Schema registry enables schema management and organization for registry workflows.
    # Registry workflows require schema registry for schema management and organization in registry workflows.
    # Schema registry supports schema management, organization, and registry coordination while enabling
    # comprehensive registry strategies and systematic schema management workflows.
    """
    
    def __init__(self):
        """Initialize the schema registry."""
        self.schemas: Dict[str, SchemaDocument] = {}
        self.schema_paths: Dict[str, str] = {}
    
    def register_schema(self, name: str, schema_doc: SchemaDocument, file_path: Optional[str] = None):
        """
        Register a schema document.
        
        Args:
            name: Name to register the schema under
            schema_doc: The schema document
            file_path: Optional file path for the schema
        """
        self.schemas[name] = schema_doc
        if file_path:
            self.schema_paths[name] = file_path
    
    def load_schema_file(self, name: str, file_path: str):
        """
        Load and register a schema from file.
        
        Args:
            name: Name to register the schema under
            file_path: Path to the schema file
        """
        schema_doc = load_schema(file_path)
        self.register_schema(name, schema_doc, file_path)
    
    def get_schema(self, name: str) -> Optional[SchemaDocument]:
        """
        Get a registered schema by name.
        
        Args:
            name: The schema name
            
        Returns:
            SchemaDocument or None: The schema document if found
        """
        return self.schemas.get(name)
    
    def list_schemas(self) -> List[str]:
        """
        List all registered schema names.
        
        Returns:
            List[str]: List of schema names
        """
        return list(self.schemas.keys())
    
    def validate_config(self, config_data: Dict[str, Any], schema_name: str,
                       config_schema_name: Optional[str] = None) -> ValidationResult:
        """
        Validate configuration using a registered schema.
        
        Args:
            config_data: The configuration data to validate
            schema_name: Name of the registered schema to use
            config_schema_name: Optional specific schema within the document
            
        Returns:
            ValidationResult: The validation result
            
        Raises:
            ValueError: If schema name is not registered
        """
        if schema_name not in self.schemas:
            raise ValueError(f"Schema '{schema_name}' not registered")
        
        return validate_config(config_data, self.schemas[schema_name], config_schema_name)


# Global schema registry instance
_global_registry = SchemaRegistry()


def register_global_schema(name: str, schema_doc: SchemaDocument, file_path: Optional[str] = None):
    """Register a schema in the global registry."""
    _global_registry.register_schema(name, schema_doc, file_path)


def load_global_schema_file(name: str, file_path: str):
    """Load and register a schema file in the global registry."""
    _global_registry.load_schema_file(name, file_path)


def get_global_schema(name: str) -> Optional[SchemaDocument]:
    """Get a schema from the global registry."""
    return _global_registry.get_schema(name)


def validate_with_global_schema(config_data: Dict[str, Any], schema_name: str,
                               config_schema_name: Optional[str] = None) -> ValidationResult:
    """Validate configuration using a globally registered schema."""
    return _global_registry.validate_config(config_data, schema_name, config_schema_name)
