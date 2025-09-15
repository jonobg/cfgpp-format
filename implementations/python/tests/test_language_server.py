#!/usr/bin/env python3
"""
Tests for cfgpp-format language server.

Tests cover LSP protocol handling, document management, diagnostics, and completion.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cfgpp.language_server import (
    CfgppLanguageServer, DocumentManager, DiagnosticsEngine, CompletionProvider,
    Position, Range, Diagnostic, CompletionItem
)


class TestDocumentManager(unittest.TestCase):
    """Test document lifecycle management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.doc_manager = DocumentManager()
    
    def test_open_document(self):
        """Test opening a new document."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig { value = "test"; }'
        
        self.doc_manager.open_document(uri, content)
        
        self.assertEqual(self.doc_manager.get_document_content(uri), content)
        self.assertIsNotNone(self.doc_manager.get_parsed_document(uri))
    
    def test_update_document(self):
        """Test updating document content."""
        uri = "file:///test.cfgpp"
        original_content = 'AppConfig { value = "test"; }'
        updated_content = 'AppConfig { value = "updated"; }'
        
        self.doc_manager.open_document(uri, original_content)
        self.doc_manager.update_document(uri, updated_content)
        
        self.assertEqual(self.doc_manager.get_document_content(uri), updated_content)
    
    def test_close_document(self):
        """Test closing a document."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig { value = "test"; }'
        
        self.doc_manager.open_document(uri, content)
        self.doc_manager.close_document(uri)
        
        self.assertIsNone(self.doc_manager.get_document_content(uri))
        self.assertIsNone(self.doc_manager.get_parsed_document(uri))
    
    def test_parse_valid_document(self):
        """Test parsing a valid document."""
        uri = "file:///test.cfgpp"
        content = '''
        enum::Status {
            values = ["active", "inactive"],
            default = "active"
        }
        
        AppConfig(string name = "test") {
            value = "configured";
        }
        '''
        
        self.doc_manager.open_document(uri, content)
        parsed = self.doc_manager.get_parsed_document(uri)
        
        self.assertIsNotNone(parsed)
        self.assertIn('body', parsed)
        self.assertIn('Status', parsed['body'])
        self.assertIn('AppConfig', parsed['body'])
    
    def test_parse_invalid_document(self):
        """Test parsing an invalid document."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig { invalid syntax }'
        
        self.doc_manager.open_document(uri, content)
        parsed = self.doc_manager.get_parsed_document(uri)
        
        self.assertIsNotNone(parsed)
        self.assertIn('error', parsed)


class TestDiagnosticsEngine(unittest.TestCase):
    """Test diagnostics and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.doc_manager = DocumentManager()
        self.diagnostics_engine = DiagnosticsEngine(self.doc_manager)
    
    def test_no_diagnostics_for_valid_document(self):
        """Test that valid documents produce no diagnostics."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig { value = "test"; }'
        
        self.doc_manager.open_document(uri, content)
        diagnostics = self.diagnostics_engine.validate_document(uri)
        
        # Should have no syntax errors
        syntax_errors = [d for d in diagnostics if d.source == "cfgpp"]
        self.assertEqual(len(syntax_errors), 0)
    
    def test_diagnostics_for_invalid_document(self):
        """Test that invalid documents produce diagnostics."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig { invalid'  # Missing closing brace
        
        self.doc_manager.open_document(uri, content)
        diagnostics = self.diagnostics_engine.validate_document(uri)
        
        # Should have syntax errors
        syntax_errors = [d for d in diagnostics if d.source == "cfgpp"]
        self.assertGreater(len(syntax_errors), 0)
    
    def test_diagnostic_structure(self):
        """Test that diagnostics have proper structure."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig { invalid'
        
        self.doc_manager.open_document(uri, content)
        diagnostics = self.diagnostics_engine.validate_document(uri)
        
        if diagnostics:
            diag = diagnostics[0]
            self.assertIsInstance(diag, Diagnostic)
            self.assertIsInstance(diag.range, Range)
            self.assertIsInstance(diag.range.start, Position)
            self.assertIsInstance(diag.range.end, Position)
            self.assertIn(diag.severity, [1, 2, 3, 4])  # Valid severity levels
            self.assertIsInstance(diag.message, str)


class TestCompletionProvider(unittest.TestCase):
    """Test auto-completion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.doc_manager = DocumentManager()
        self.completion_provider = CompletionProvider(self.doc_manager)
    
    def test_keyword_completion(self):
        """Test basic keyword completion."""
        uri = "file:///test.cfgpp"
        content = 'en'  # Partial enum keyword
        position = Position(line=0, character=2)
        
        self.doc_manager.open_document(uri, content)
        completions = self.completion_provider.provide_completion(uri, position)
        
        # Should include enum keyword
        labels = [c.label for c in completions]
        self.assertIn('enum', labels)
    
    def test_parameter_type_completion(self):
        """Test parameter type completion."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig(str'  # Partial string type
        position = Position(line=0, character=13)
        
        self.doc_manager.open_document(uri, content)
        completions = self.completion_provider.provide_completion(uri, position)
        
        # Should include string type
        labels = [c.label for c in completions]
        self.assertIn('string', labels)
    
    def test_enum_value_completion(self):
        """Test enum value completion."""
        uri = "file:///test.cfgpp"
        content = '''
        enum::Status {
            values = ["active", "inactive"]
        }
        AppConfig(Status status = "
        '''
        position = Position(line=5, character=30)
        
        self.doc_manager.open_document(uri, content)
        completions = self.completion_provider.provide_completion(uri, position)
        
        # Should include enum values
        labels = [c.label for c in completions]
        self.assertTrue(any('active' in label for label in labels))
        self.assertTrue(any('inactive' in label for label in labels))
    
    def test_completion_item_structure(self):
        """Test that completion items have proper structure."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig('
        position = Position(line=0, character=10)
        
        self.doc_manager.open_document(uri, content)
        completions = self.completion_provider.provide_completion(uri, position)
        
        if completions:
            completion = completions[0]
            self.assertIsInstance(completion, CompletionItem)
            self.assertIsInstance(completion.label, str)
            self.assertIsInstance(completion.kind, int)


class TestCfgppLanguageServer(unittest.TestCase):
    """Test main language server functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = CfgppLanguageServer()
    
    def test_initialization(self):
        """Test server initialization."""
        params = {
            'capabilities': {
                'textDocument': {
                    'completion': {'dynamicRegistration': True}
                }
            }
        }
        
        # Since initialize is async, we'll test the sync parts
        self.assertIsNotNone(self.server.server_capabilities)
        self.assertIn('textDocumentSync', self.server.server_capabilities)
        self.assertIn('completionProvider', self.server.server_capabilities)
    
    def test_server_capabilities(self):
        """Test that server declares proper capabilities."""
        capabilities = self.server.server_capabilities
        
        # Essential capabilities
        self.assertTrue(capabilities['textDocumentSync']['openClose'])
        self.assertEqual(capabilities['textDocumentSync']['change'], 1)  # Full sync
        self.assertTrue(capabilities['completionProvider']['triggerCharacters'])
        self.assertTrue(capabilities['hoverProvider'])
        self.assertTrue(capabilities['documentFormattingProvider'])
    
    def test_diagnostic_conversion(self):
        """Test conversion of diagnostics to LSP format."""
        diagnostic = Diagnostic(
            range=Range(
                start=Position(line=1, character=5),
                end=Position(line=1, character=15)
            ),
            severity=1,
            code="test_error",
            source="cfgpp",
            message="Test error message"
        )
        
        lsp_dict = self.server._diagnostic_to_dict(diagnostic)
        
        self.assertEqual(lsp_dict['range']['start']['line'], 1)
        self.assertEqual(lsp_dict['range']['start']['character'], 5)
        self.assertEqual(lsp_dict['severity'], 1)
        self.assertEqual(lsp_dict['code'], "test_error")
        self.assertEqual(lsp_dict['source'], "cfgpp")
        self.assertEqual(lsp_dict['message'], "Test error message")
    
    def test_completion_item_conversion(self):
        """Test conversion of completion items to LSP format."""
        completion = CompletionItem(
            label="test_completion",
            kind=14,
            detail="Test detail",
            documentation="Test documentation",
            insert_text="test_insert"
        )
        
        lsp_dict = self.server._completion_item_to_dict(completion)
        
        self.assertEqual(lsp_dict['label'], "test_completion")
        self.assertEqual(lsp_dict['kind'], 14)
        self.assertEqual(lsp_dict['detail'], "Test detail")
        self.assertEqual(lsp_dict['documentation'], "Test documentation")
        self.assertEqual(lsp_dict['insertText'], "test_insert")


class TestLSPIntegration(unittest.TestCase):
    """Test LSP protocol integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = CfgppLanguageServer()
    
    def test_document_lifecycle(self):
        """Test complete document lifecycle."""
        uri = "file:///test.cfgpp"
        content = 'AppConfig { value = "test"; }'
        
        # Simulate document open
        self.server.document_manager.open_document(uri, content)
        
        # Check document is stored
        self.assertEqual(self.server.document_manager.get_document_content(uri), content)
        
        # Simulate document update
        new_content = 'AppConfig { value = "updated"; }'
        self.server.document_manager.update_document(uri, new_content)
        
        # Check document is updated
        self.assertEqual(self.server.document_manager.get_document_content(uri), new_content)
        
        # Simulate document close
        self.server.document_manager.close_document(uri)
        
        # Check document is removed
        self.assertIsNone(self.server.document_manager.get_document_content(uri))
    
    def test_formatting_integration(self):
        """Test document formatting integration."""
        uri = "file:///test.cfgpp"
        messy_content = 'enum::Status{values=["active","inactive"]}AppConfig(string name="test"){value="test";}'
        
        self.server.document_manager.open_document(uri, messy_content)
        
        # Test formatting parameters structure
        params = {
            'textDocument': {'uri': uri},
            'options': {'tabSize': 4, 'insertSpaces': True}
        }
        
        # The formatting method is async, but we can test the synchronous parts
        content = self.server.document_manager.get_document_content(uri)
        self.assertEqual(content, messy_content)
        
        # Test that document exists for formatting
        self.assertIsNotNone(content)
    
    def test_completion_integration(self):
        """Test completion provider integration."""
        uri = "file:///test.cfgpp"
        content = '''
        enum::Status {
            values = ["active", "inactive"]
        }
        
        AppConfig(string name = "test") {
            value = "";
        }
        '''
        
        self.server.document_manager.open_document(uri, content)
        
        # Test completion at various positions
        position = Position(line=6, character=20)
        completions = self.server.completion_provider.provide_completion(uri, position)
        
        # Should provide some completions
        self.assertIsInstance(completions, list)
    
    def test_diagnostics_integration(self):
        """Test diagnostics engine integration."""
        uri = "file:///test.cfgpp"
        invalid_content = 'AppConfig { invalid syntax without closing'
        
        self.server.document_manager.open_document(uri, invalid_content)
        diagnostics = self.server.diagnostics_engine.validate_document(uri)
        
        # Should produce diagnostics for invalid content
        self.assertIsInstance(diagnostics, list)
        
        # Test with valid content
        valid_content = 'AppConfig { value = "test"; }'
        self.server.document_manager.update_document(uri, valid_content)
        diagnostics = self.server.diagnostics_engine.validate_document(uri)
        
        # Should have fewer or no syntax errors
        syntax_errors = [d for d in diagnostics if d.source == "cfgpp"]
        # Valid content should have no syntax errors
        self.assertEqual(len(syntax_errors), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
