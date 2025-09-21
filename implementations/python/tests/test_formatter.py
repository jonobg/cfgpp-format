#!/usr/bin/env python3
"""
Tests for cfgpp-format code formatter.

Tests cover formatting styles, configuration options, and integration scenarios.
"""

import unittest
import sys
import os
from textwrap import dedent

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cfgpp.formatter import (
    CfgppFormatter,
    FormatterConfig,
    BraceStyle,
    ArrayStyle,
    CommentStyle,
    format_string,
    format_file,
)
from cfgpp.parser import loads, ConfigParseError


class TestFormatterConfig(unittest.TestCase):
    """Test formatter configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = FormatterConfig()

        self.assertEqual(config.indent_size, 4)
        self.assertFalse(config.use_tabs)
        self.assertEqual(config.brace_style, BraceStyle.SAME_LINE)
        self.assertEqual(config.array_style, ArrayStyle.AUTO)
        self.assertEqual(config.max_line_length, 100)

    def test_compact_config(self):
        """Test compact configuration preset."""
        config = FormatterConfig.compact()

        self.assertEqual(config.indent_size, 2)
        self.assertEqual(config.brace_style, BraceStyle.SAME_LINE)
        self.assertEqual(config.array_style, ArrayStyle.COMPACT)
        self.assertEqual(config.blank_lines_before_object, 0)

    def test_expanded_config(self):
        """Test expanded configuration preset."""
        config = FormatterConfig.expanded()

        self.assertEqual(config.indent_size, 4)
        self.assertEqual(config.brace_style, BraceStyle.NEW_LINE)
        self.assertEqual(config.array_style, ArrayStyle.ONE_PER_LINE)
        self.assertEqual(config.blank_lines_before_object, 2)


class TestBasicFormatting(unittest.TestCase):
    """Test basic formatting functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CfgppFormatter()

    def test_simple_object_formatting(self):
        """Test formatting of simple objects."""
        config_text = """
        AppConfig(
            string name="test",
            int port=8080,
            bool debug=true
        )
        """

        result = self.formatter.format(config_text)

        # Check that it parses and formats without errors
        self.assertIsInstance(result, str)
        self.assertIn("AppConfig", result)
        self.assertIn('name = "test"', result)

    def test_enum_formatting(self):
        """Test formatting of enum definitions."""
        config_text = """
        enum::Status {
            values = ["active", "inactive", "pending"],
            default = "active"
        }
        """

        result = self.formatter.format(config_text)

        self.assertIn("enum::Status {", result)
        self.assertIn("values =", result)
        self.assertIn("default =", result)

    def test_nested_objects(self):
        """Test formatting of nested objects."""
        config_text = """
        AppConfig(
            string name = "app",
            DatabaseConfig database
        ) {
            DatabaseConfig::database(
                string host = "localhost",
                int port = 5432
            );
        }
        """

        result = self.formatter.format(config_text)

        # Should format without errors and maintain structure
        self.assertIsInstance(result, str)
        self.assertIn("AppConfig", result)
        self.assertIn("DatabaseConfig::database", result)

    def test_array_formatting(self):
        """Test array formatting with different styles."""
        config_text = """
        Config(
            string[] hosts = ["host1", "host2", "host3"],
            int[] ports = [80, 443, 8080, 3000, 5432]
        )
        """

        # Test compact style
        compact_config = FormatterConfig(array_style=ArrayStyle.COMPACT)
        formatter = CfgppFormatter(compact_config)
        result = formatter.format(config_text)

        # Should keep arrays compact
        self.assertIn("[", result)
        self.assertIn("]", result)

        # Test expanded style
        expanded_config = FormatterConfig(array_style=ArrayStyle.ONE_PER_LINE)
        formatter = CfgppFormatter(expanded_config)
        result = formatter.format(config_text)

        # Should expand arrays
        self.assertIn("[\n", result)


class TestFormattingStyles(unittest.TestCase):
    """Test different formatting styles."""

    def test_brace_styles(self):
        """Test different brace placement styles."""
        config_text = """
        AppConfig(string name = "test") {
            value = "test";
        }
        """

        # Same line style
        same_line_config = FormatterConfig(brace_style=BraceStyle.SAME_LINE)
        formatter = CfgppFormatter(same_line_config)
        result = formatter.format(config_text)
        self.assertIn(") {", result)

        # New line style
        new_line_config = FormatterConfig(brace_style=BraceStyle.NEW_LINE)
        formatter = CfgppFormatter(new_line_config)
        result = formatter.format(config_text)
        # Should have opening brace on new line
        lines = result.strip().split("\n")
        has_standalone_brace = any(line.strip() == "{" for line in lines)
        self.assertTrue(has_standalone_brace)

    def test_indentation_styles(self):
        """Test different indentation configurations."""
        config_text = """
        AppConfig {
            value = "test";
        }
        """

        # 2-space indentation
        config_2_spaces = FormatterConfig(indent_size=2)
        formatter = CfgppFormatter(config_2_spaces)
        result = formatter.format(config_text)
        self.assertIn("  value =", result)  # 2 spaces

        # 4-space indentation
        config_4_spaces = FormatterConfig(indent_size=4)
        formatter = CfgppFormatter(config_4_spaces)
        result = formatter.format(config_text)
        self.assertIn("    value =", result)  # 4 spaces

    def test_spacing_styles(self):
        """Test different spacing configurations."""
        config_text = """
        AppConfig(string name="test")
        """

        # No space before equals
        no_space_config = FormatterConfig(
            space_before_equals=False, space_after_equals=True
        )
        formatter = CfgppFormatter(no_space_config)
        result = formatter.format(config_text)
        self.assertIn('name= "test"', result)

        # Space before and after equals
        space_config = FormatterConfig(
            space_before_equals=True, space_after_equals=True
        )
        formatter = CfgppFormatter(space_config)
        result = formatter.format(config_text)
        self.assertIn('name = "test"', result)


class TestFormatterIntegration(unittest.TestCase):
    """Test formatter integration with other components."""

    def test_format_string_function(self):
        """Test the format_string convenience function."""
        config_text = """
        enum::Status{values=["active","inactive"]}
        AppConfig(string name="test",Status status="active")
        """

        result = format_string(config_text)

        # Should be properly formatted
        self.assertIsInstance(result, str)
        self.assertIn("enum::Status {", result)
        self.assertIn('name = "test"', result)

    def test_invalid_config_handling(self):
        """Test handling of invalid configuration."""
        invalid_config = """
        InvalidConfig {
            missing_value =
        }
        """

        formatter = CfgppFormatter()

        with self.assertRaises(ConfigParseError):
            formatter.format(invalid_config)

    def test_empty_config_handling(self):
        """Test handling of empty configuration."""
        empty_config = ""

        formatter = CfgppFormatter()
        result = formatter.format(empty_config)

        # Should return empty or minimal content
        self.assertEqual(result.strip(), "")

    def test_whitespace_normalization(self):
        """Test whitespace and blank line normalization."""
        messy_config = """
        
        
        AppConfig {
        
        
            value = "test";
        
        
        }
        
        
        """

        formatter = CfgppFormatter()
        result = formatter.format(messy_config)

        # Should normalize excessive whitespace
        lines = result.split("\n")

        # Remove empty lines from start and end for comparison
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        # Should not have excessive consecutive blank lines
        consecutive_blanks = 0
        max_consecutive = 0

        for line in lines:
            if not line.strip():
                consecutive_blanks += 1
                max_consecutive = max(max_consecutive, consecutive_blanks)
            else:
                consecutive_blanks = 0

        self.assertLessEqual(max_consecutive, 2)  # At most 2 consecutive blank lines


class TestComplexFormatting(unittest.TestCase):
    """Test formatting of complex configurations."""

    def test_comprehensive_config(self):
        """Test formatting of comprehensive configuration with all features."""
        config_text = """
        enum::Environment{values=["dev","staging","prod"],default="dev"}
        enum::LogLevel{values=["debug","info","error"]}
        
        AppConfig(string name="MyApp",Environment env="prod",LogLevel logLevel="info"){
            DatabaseConfig::database(string host="db.example.com",int port=5432){
                ConnectionPool::pool(int minConnections=5,int maxConnections=50);
            }
            ServerConfig::server(string host="0.0.0.0",int port=3000,string[] allowedOrigins=["https://example.com","https://app.example.com"]);
        }
        """

        # Format with default configuration
        formatter = CfgppFormatter()
        result = formatter.format(config_text)

        # Should handle all components correctly
        self.assertIn("enum::Environment {", result)
        self.assertIn("enum::LogLevel {", result)
        self.assertIn("AppConfig(", result)
        self.assertIn("DatabaseConfig::database", result)
        self.assertIn("ConnectionPool::pool", result)
        self.assertIn("ServerConfig::server", result)

        # Should be valid parseable configuration
        try:
            loads(result)
        except ConfigParseError as e:
            self.fail(f"Formatted output is not valid: {e}")

    def test_sorting_options(self):
        """Test key and value sorting options."""
        config_text = """
        enum::Status {
            values = ["pending", "active", "inactive"]
        }
        
        Config {
            zebra = "last";
            alpha = "first";
            beta = "second";
        }
        """

        # Test with sorting enabled
        sort_config = FormatterConfig(sort_object_keys=True, sort_enum_values=True)
        formatter = CfgppFormatter(sort_config)
        result = formatter.format(config_text)

        # Should maintain structure (exact sorting behavior depends on implementation)
        self.assertIn("alpha", result)
        self.assertIn("beta", result)
        self.assertIn("zebra", result)


class TestFormatterEdgeCases(unittest.TestCase):
    """Test formatter edge cases and error conditions."""

    def test_very_long_lines(self):
        """Test handling of very long lines."""
        config_text = """
        Config {
            veryLongPropertyNameThatExceedsReasonableLength = "This is a very long string value that should trigger line wrapping behavior in the formatter when it exceeds the maximum line length configuration";
        }
        """

        short_line_config = FormatterConfig(max_line_length=50)
        formatter = CfgppFormatter(short_line_config)
        result = formatter.format(config_text)

        # Should handle long lines gracefully
        self.assertIsInstance(result, str)
        self.assertIn("veryLongPropertyNameThatExceedsReasonableLength", result)

    def test_special_characters(self):
        """Test handling of special characters in strings."""
        config_text = """
        Config {
            specialChars = "String with \\"quotes\\" and \\n newlines";
            unicode = "Unicode: 🚀 emoji and åccénts";
        }
        """

        formatter = CfgppFormatter()
        result = formatter.format(config_text)

        # Should preserve special characters
        self.assertIn('\\"quotes\\"', result)
        self.assertIn("🚀", result)
        self.assertIn("åccénts", result)

    def test_minimal_config(self):
        """Test formatting of minimal configuration."""
        config_text = "SimpleConfig {}"

        formatter = CfgppFormatter()
        result = formatter.format(config_text)

        self.assertIn("SimpleConfig {}", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
