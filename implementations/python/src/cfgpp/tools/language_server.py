#!/usr/bin/env python3
"""
CFG++ Language Server Protocol implementation.

# REASONING: Language server enables professional IDE integration for developer productivity workflows.
# Developer productivity workflows require language server for professional IDE integration in productivity workflows.
# Language server supports professional IDE integration, developer productivity, and workflow coordination while enabling
# comprehensive development strategies and systematic IDE integration workflows.

# REASONING: LSP standardization ensures broad editor compatibility for universal development workflows.
# Universal development workflows require LSP standardization for broad editor compatibility in universal workflows.
# LSP standardization supports broad editor compatibility, universal development, and compatibility coordination while enabling
# comprehensive compatibility strategies and systematic universal development workflows.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from ..core.parser import loads, ConfigParseError
from ..schema.integration import auto_discover_schema, load_with_auto_schema
from ..schema.schema_validator import ValidationResult, ValidationMessage, ValidationSeverity
from ..core.formatter import format_string


# LSP Protocol Types
@dataclass
class Position:
    """LSP Position type."""

    line: int
    character: int


@dataclass
class Range:
    """LSP Range type."""

    start: Position
    end: Position


@dataclass
class Diagnostic:
    """LSP Diagnostic type."""

    range: Range
    severity: int  # 1=Error, 2=Warning, 3=Information, 4=Hint
    code: Optional[Union[int, str]]
    source: str
    message: str
    related_information: Optional[List[Dict]] = None


@dataclass
class CompletionItem:
    """LSP CompletionItem type."""

    label: str
    kind: int  # CompletionItemKind
    detail: Optional[str] = None
    documentation: Optional[str] = None
    insert_text: Optional[str] = None
    text_edit: Optional[Dict] = None


@dataclass
class Hover:
    """LSP Hover type."""

    contents: Union[str, Dict]
    range: Optional[Range] = None


class DocumentManager:
    """
    Manages document lifecycle and parsing for LSP operations.

    # REASONING: Document management enables efficient incremental parsing for real-time development workflows.
    # Real-time development workflows require document management for efficient incremental parsing in development workflows.
    # Document management supports efficient incremental parsing, real-time development, and parsing coordination while enabling
    # comprehensive efficiency strategies and systematic incremental parsing workflows.
    """

    def __init__(self) -> None:
        self.documents: Dict[str, str] = {}  # URI -> content
        self.parsed_documents: Dict[str, Dict] = {}  # URI -> parsed AST
        self._logger = logging.getLogger(__name__)

    def open_document(self, uri: str, content: str) -> None:
        """Open and parse a new document."""
        self._logger.info(f"Opening document: {uri}")
        self.documents[uri] = content
        self._parse_document(uri, content)

    def update_document(self, uri: str, content: str) -> None:
        """Update document content and reparse."""
        self._logger.info(f"Updating document: {uri}")
        self.documents[uri] = content
        self._parse_document(uri, content)

    def close_document(self, uri: str) -> None:
        """Close and clean up document."""
        self._logger.info(f"Closing document: {uri}")
        self.documents.pop(uri, None)
        self.parsed_documents.pop(uri, None)

    def get_document_content(self, uri: str) -> Optional[str]:
        """Get document content by URI."""
        return self.documents.get(uri)

    def get_parsed_document(self, uri: str) -> Optional[Dict]:
        """Get parsed document AST by URI."""
        return self.parsed_documents.get(uri)

    def _parse_document(self, uri: str, content: str) -> None:
        """Parse document and store AST."""
        try:
            # REASONING: Exception handling enables robust parsing for error-resilient development workflows.
            # Error-resilient development workflows require exception handling for robust parsing in development workflows.
            # Exception handling supports robust parsing, error resilience, and parsing coordination while enabling
            # comprehensive robustness strategies and systematic error-resilient parsing workflows.

            parsed = loads(content)
            self.parsed_documents[uri] = parsed
            self._logger.debug(f"Successfully parsed document: {uri}")
        except ConfigParseError as e:
            self._logger.warning(f"Parse error in document {uri}: {e}")
            # Store partial information for error recovery
            self.parsed_documents[uri] = {
                "error": str(e),
                "line": getattr(e, "line", 0),
                "col": getattr(e, "col", 0),
            }
        except Exception as e:
            self._logger.error(f"Unexpected error parsing document {uri}: {e}")
            self.parsed_documents[uri] = {"error": str(e)}


class DiagnosticsEngine:
    """
    Provides real-time validation and diagnostics for cfgpp documents.

    # REASONING: Real-time diagnostics enable immediate feedback for efficient development workflows.
    # Efficient development workflows require real-time diagnostics for immediate feedback in development workflows.
    # Real-time diagnostics support immediate feedback, efficient development, and feedback coordination while enabling
    # comprehensive efficiency strategies and systematic immediate feedback workflows.
    """

    def __init__(self, document_manager: DocumentManager):
        self.document_manager = document_manager
        self._logger = logging.getLogger(__name__)

    def validate_document(self, uri: str) -> List[Diagnostic]:
        """Validate document and return diagnostics."""
        diagnostics: List[Diagnostic] = []

        content = self.document_manager.get_document_content(uri)
        if not content:
            return diagnostics

        parsed = self.document_manager.get_parsed_document(uri)
        if not parsed:
            return diagnostics

        # Check for parsing errors
        if "error" in parsed:
            error_line = parsed.get("line", 0)
            error_col = parsed.get("col", 0)

            # Ensure line and col are integers
            if not isinstance(error_line, int):
                error_line = 0
            if not isinstance(error_col, int):
                error_col = 0

            diagnostic = Diagnostic(
                range=Range(
                    start=Position(line=error_line, character=error_col),
                    end=Position(line=error_line, character=error_col + 10),
                ),
                severity=1,  # Error
                code="parse_error",
                source="cfgpp",
                message=parsed["error"],
            )
            diagnostics.append(diagnostic)

        # Schema validation if available
        try:
            schema_diagnostics = self._validate_schema(uri, parsed)
            diagnostics.extend(schema_diagnostics)
        except Exception as e:
            self._logger.warning(f"Schema validation error for {uri}: {e}")

        return diagnostics

    def _validate_schema(self, uri: str, parsed_doc: Dict) -> List[Diagnostic]:
        """Perform schema validation and return diagnostics."""
        diagnostics = []

        # REASONING: Schema integration enables comprehensive validation for quality-assured development workflows.
        # Quality-assured development workflows require schema integration for comprehensive validation in development workflows.
        # Schema integration supports comprehensive validation, quality assurance, and validation coordination while enabling
        # comprehensive quality strategies and systematic validation workflows.

        try:
            # Auto-discover and validate against schema
            file_path = Path(uri.replace("file://", ""))

            # Try to load with schema validation
            _, validation_result = load_with_auto_schema(str(file_path), validate=True)

            if validation_result and validation_result.messages:
                for msg in validation_result.messages:
                    severity_map = {
                        ValidationSeverity.ERROR: 1,
                        ValidationSeverity.WARNING: 2,
                        ValidationSeverity.INFO: 3,
                    }
                    severity = severity_map.get(msg.severity, 2)

                    diagnostic = Diagnostic(
                        range=Range(
                            start=Position(line=msg.line or 0, character=msg.col or 0),
                            end=Position(
                                line=msg.line or 0, character=(msg.col or 0) + 10
                            ),
                        ),
                        severity=severity,
                        code="schema_validation",
                        source="cfgpp-schema",
                        message=msg.message,
                    )
                    diagnostics.append(diagnostic)

        except Exception as e:
            self._logger.debug(f"Schema validation not available: {e}")

        return diagnostics


class CompletionProvider:
    """
    Provides auto-completion suggestions for cfgpp documents.

    # REASONING: Auto-completion enables efficient code writing for productive development workflows.
    # Productive development workflows require auto-completion for efficient code writing in development workflows.
    # Auto-completion supports efficient code writing, productive development, and completion coordination while enabling
    # comprehensive productivity strategies and systematic code completion workflows.
    """

    def __init__(self, document_manager: DocumentManager):
        self.document_manager = document_manager
        self._logger = logging.getLogger(__name__)

    def provide_completion(self, uri: str, position: Position) -> List[CompletionItem]:
        """Generate context-aware completion suggestions."""
        completions: List[CompletionItem] = []

        content = self.document_manager.get_document_content(uri)
        parsed = self.document_manager.get_parsed_document(uri)

        if not content or not parsed:
            return completions

        # Get current line for context analysis
        lines = content.split("\n")
        if position.line >= len(lines):
            return completions

        current_line = lines[position.line]
        line_before_cursor = current_line[: position.character]

        # Enum value completion
        if self._is_enum_context(line_before_cursor):
            completions.extend(self._complete_enum_values(parsed))

        # Parameter completion
        elif self._is_parameter_context(line_before_cursor):
            completions.extend(self._complete_parameters())

        # Property name completion
        elif self._is_property_context(line_before_cursor):
            completions.extend(self._complete_properties())

        # Keyword completion
        else:
            completions.extend(self._complete_keywords())

        return completions

    def _is_enum_context(self, line_before_cursor: str) -> bool:
        """Check if cursor is in enum value context."""
        # Check if we're in a string context after an enum type parameter
        # Pattern: SomeEnumType paramName = "
        if '= "' in line_before_cursor:
            return True
        # Also check for enum definition values context
        return "enum::" in line_before_cursor and "values" in line_before_cursor

    def _is_parameter_context(self, line_before_cursor: str) -> bool:
        """Check if cursor is in parameter context."""
        return "(" in line_before_cursor and ")" not in line_before_cursor

    def _is_property_context(self, line_before_cursor: str) -> bool:
        """Check if cursor is in property assignment context."""
        return "{" in line_before_cursor and "=" not in line_before_cursor

    def _complete_enum_values(self, parsed_doc: Dict) -> List[CompletionItem]:
        """Complete enum values from document."""
        completions: List[CompletionItem] = []

        if "body" not in parsed_doc:
            return completions

        for name, obj in parsed_doc["body"].items():
            if obj.get("type") == "enum_definition":
                values = obj.get("values", [])
                for value in values:
                    completions.append(
                        CompletionItem(
                            label=f'"{value}"',
                            kind=12,  # Value
                            detail=f"Enum value from {name}",
                            insert_text=f'"{value}"',
                        )
                    )

        return completions

    def _complete_parameters(self) -> List[CompletionItem]:
        """Complete common parameter types."""
        return [
            CompletionItem(label="string", kind=14, detail="String parameter type"),
            CompletionItem(label="int", kind=14, detail="Integer parameter type"),
            CompletionItem(label="bool", kind=14, detail="Boolean parameter type"),
            CompletionItem(label="float", kind=14, detail="Float parameter type"),
        ]

    def _complete_properties(self) -> List[CompletionItem]:
        """Complete common property names."""
        return [
            CompletionItem(label="name", kind=5, detail="Configuration name"),
            CompletionItem(label="value", kind=5, detail="Configuration value"),
            CompletionItem(label="enabled", kind=5, detail="Enable/disable flag"),
            CompletionItem(label="timeout", kind=5, detail="Timeout setting"),
        ]

    def _complete_keywords(self) -> List[CompletionItem]:
        """Complete cfgpp keywords."""
        return [
            CompletionItem(
                label="enum", kind=14, detail="Define enumeration", insert_text="enum::"
            ),
            CompletionItem(label="values", kind=5, detail="Enum values array"),
            CompletionItem(label="default", kind=5, detail="Default enum value"),
        ]


class CfgppLanguageServer:
    """
    Main Language Server Protocol implementation for cfgpp.

    # REASONING: Centralized coordination enables comprehensive IDE integration for professional development workflows.
    # Professional development workflows require centralized coordination for comprehensive IDE integration in development workflows.
    # Centralized coordination supports comprehensive IDE integration, professional development, and coordination while enabling
    # comprehensive professional strategies and systematic IDE integration workflows.
    """

    def __init__(self) -> None:
        self.document_manager = DocumentManager()
        self.diagnostics_engine = DiagnosticsEngine(self.document_manager)
        self.completion_provider = CompletionProvider(self.document_manager)

        self._logger = logging.getLogger(__name__)

        # LSP capabilities
        self.server_capabilities = {
            "textDocumentSync": {
                "openClose": True,
                "change": 1,  # Full document sync
                "save": {"includeText": True},
            },
            "completionProvider": {
                "triggerCharacters": ["::", "=", '"', "["],
                "resolveProvider": False,
            },
            "hoverProvider": True,
            "diagnosticsProvider": True,
            "documentFormattingProvider": True,
            "documentSymbolProvider": True,
        }

    async def initialize(self, params: Dict) -> Dict:
        """Initialize the language server."""
        self._logger.info("Initializing CFG++ Language Server")

        # Store client capabilities
        self.client_capabilities = params.get("capabilities", {})

        return {
            "capabilities": self.server_capabilities,
            "serverInfo": {"name": "cfgpp-language-server", "version": "1.0.0"},
        }

    async def text_document_did_open(self, params: Dict) -> None:
        """Handle document open notification."""
        doc = params["textDocument"]
        uri = doc["uri"]
        content = doc["text"]

        self.document_manager.open_document(uri, content)
        await self._send_diagnostics(uri)

    async def text_document_did_change(self, params: Dict) -> None:
        """Handle document change notification."""
        doc = params["textDocument"]
        uri = doc["uri"]
        changes = params["contentChanges"]

        # For full document sync, take the last change
        if changes and "text" in changes[-1]:
            content = changes[-1]["text"]
            self.document_manager.update_document(uri, content)
            await self._send_diagnostics(uri)

    async def text_document_did_close(self, params: Dict) -> None:
        """Handle document close notification."""
        doc = params["textDocument"]
        uri = doc["uri"]

        self.document_manager.close_document(uri)

    async def text_document_completion(self, params: Dict) -> Dict:
        """Handle completion request."""
        doc = params["textDocument"]
        position = Position(
            line=params["position"]["line"], character=params["position"]["character"]
        )

        completions = self.completion_provider.provide_completion(doc["uri"], position)

        return {
            "isIncomplete": False,
            "items": [self._completion_item_to_dict(item) for item in completions],
        }

    async def text_document_formatting(self, params: Dict) -> List[Dict]:
        """Handle document formatting request."""
        doc = params["textDocument"]
        uri = doc["uri"]

        content = self.document_manager.get_document_content(uri)
        if not content:
            return []

        try:
            formatted = format_string(content)

            # Return full document replacement
            lines = content.split("\n")
            return [
                {
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": len(lines), "character": 0},
                    },
                    "newText": formatted,
                }
            ]
        except Exception as e:
            self._logger.error(f"Formatting error: {e}")
            return []

    async def _send_diagnostics(self, uri: str) -> None:
        """Send diagnostics for a document."""
        diagnostics = self.diagnostics_engine.validate_document(uri)

        # Convert diagnostics to LSP format
        lsp_diagnostics = [self._diagnostic_to_dict(d) for d in diagnostics]

        # Send diagnostics notification (would be sent to client in real implementation)
        self._logger.debug(f"Diagnostics for {uri}: {len(lsp_diagnostics)} issues")

    def _diagnostic_to_dict(self, diagnostic: Diagnostic) -> Dict:
        """Convert Diagnostic to LSP dictionary."""
        return {
            "range": {
                "start": {
                    "line": diagnostic.range.start.line,
                    "character": diagnostic.range.start.character,
                },
                "end": {
                    "line": diagnostic.range.end.line,
                    "character": diagnostic.range.end.character,
                },
            },
            "severity": diagnostic.severity,
            "code": diagnostic.code,
            "source": diagnostic.source,
            "message": diagnostic.message,
        }

    def _completion_item_to_dict(self, item: CompletionItem) -> Dict:
        """Convert CompletionItem to LSP dictionary."""
        return {
            "label": item.label,
            "kind": item.kind,
            "detail": item.detail,
            "documentation": item.documentation,
            "insertText": item.insert_text or item.label,
        }


# Entry point for standalone server
if __name__ == "__main__":
    import sys

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("cfgpp-lsp.log"),
            logging.StreamHandler(sys.stderr),
        ],
    )

    server = CfgppLanguageServer()

    # In a real implementation, this would start the JSON-RPC server
    print("CFG++ Language Server initialized")
    print("Server capabilities:")
    import pprint

    pprint.pprint(server.server_capabilities)
