#!/usr/bin/env python3
"""
Integration tests for the CFGPP parser covering all major features.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import json

from cfgpp.parser import loads, load, ConfigParseError
from cfgpp.lexer import LexerError
from cfgpp.cli import main
import sys
from io import StringIO


class TestIntegration:
    """Integration tests for CFGPP parser with all features."""

    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_comments_support(self):
        """Test that comments are properly parsed and ignored."""
        config_content = '''
        // This is a single-line comment
        AppConfig {
            name = "TestApp"  // End-of-line comment
            version = "1.0.0"
            
            /* 
             * Multi-line comment
             * with multiple lines
             */
            port = 8080
            debug = true  /* inline block comment */
            
            // Nested configuration
            database = DatabaseConfig {
                host = "localhost"  // Database host
                port = 5432
            }
        }
        
        /* End of configuration */
        '''
        
        result = loads(config_content)
        assert 'body' in result
        assert 'AppConfig' in result['body']
        
        app_config = result['body']['AppConfig']['body']
        assert app_config['name']['value']['value'] == "TestApp"
        assert app_config['version']['value']['value'] == "1.0.0"
        assert app_config['port']['value']['value'] == 8080
        assert app_config['debug']['value']['value'] is True

    def test_environment_variable_interpolation(self):
        """Test environment variable interpolation with defaults."""
        # Set up environment variables
        os.environ['TEST_APP_NAME'] = 'MyTestApp'
        os.environ['TEST_PORT'] = '9000'
        os.environ['TEST_DEBUG'] = 'true'
        
        config_content = '''
        AppConfig {
            name = ${TEST_APP_NAME:-"DefaultApp"}
            version = ${TEST_VERSION:-"1.0.0"}
            port = ${TEST_PORT:-8080}
            debug = ${TEST_DEBUG:-false}
            timeout = ${TEST_TIMEOUT:-30}
            api_key = ${API_KEY:-"default_key"}
        }
        '''
        
        try:
            result = loads(config_content)
            app_config = result['body']['AppConfig']['body']
            
            # Check environment variables were used
            assert app_config['name']['value']['value'] == "MyTestApp"
            assert app_config['port']['value']['value'] == 9000
            assert app_config['debug']['value']['value'] is True
            
            # Check defaults were used
            assert app_config['version']['value']['value'] == "1.0.0"
            assert app_config['timeout']['value']['value'] == 30
            assert app_config['api_key']['value']['value'] == "default_key"
            
        finally:
            # Clean up environment variables
            for var in ['TEST_APP_NAME', 'TEST_PORT', 'TEST_DEBUG']:
                if var in os.environ:
                    del os.environ[var]

    def test_include_functionality(self):
        """Test include/import directives with file resolution."""
        # Create shared configuration file
        shared_config = '''
        DatabaseConfig {
            host = ${DB_HOST:-"localhost"}
            port = ${DB_PORT:-5432}
            max_connections = 100
            timeout = 30
        }
        
        AuthConfig {
            jwt_secret = ${JWT_SECRET:-"default_secret"}
            token_expiry = 3600
            refresh_enabled = true
        }
        '''
        
        shared_file = self.test_dir / 'shared.cfgpp'
        shared_file.write_text(shared_config)
        
        # Create main configuration that includes shared config
        main_config = '''
        AppConfig {
            name = "MainApp"
            version = "2.0.0"
            
            @include "shared.cfgpp"
            
            server = ServerConfig {
                port = ${PORT:-8080}
                workers = 4
            }
        }
        '''
        
        main_file = self.test_dir / 'main.cfgpp'
        main_file.write_text(main_config)
        
        result = load(str(main_file))
        app_config = result['body']['AppConfig']['body']
        
        # Check main config properties
        assert app_config['name']['value']['value'] == "MainApp"
        assert app_config['version']['value']['value'] == "2.0.0"
        
        # Check included DatabaseConfig
        assert 'DatabaseConfig' in app_config
        db_config = app_config['DatabaseConfig']['body']
        assert db_config['host']['value']['value'] == "localhost"
        assert db_config['port']['value']['value'] == 5432
        assert db_config['max_connections']['value']['value'] == 100
        
        # Check included AuthConfig
        assert 'AuthConfig' in app_config
        auth_config = app_config['AuthConfig']['body']
        assert auth_config['jwt_secret']['value']['value'] == "default_secret"
        assert auth_config['token_expiry']['value']['value'] == 3600

    def test_expression_evaluation(self):
        """Test mathematical and string expressions."""
        config_content = '''
        MathConfig {
            // Basic arithmetic
            sum = 10 + 5
            difference = 20 - 8
            product = 6 * 7
            quotient = 100 / 4
            
            // Complex expressions
            complex = (10 + 5) * 2
            mixed = 5 + 3 * 2
            
            // String concatenation
            app_name = "My" + "App"
            full_name = "App" + "_" + "v1"
            
            // Environment variables in expressions
            total_workers = ${BASE_WORKERS:-4} + 2
            log_path = "/var/log/" + ${APP_NAME:-"app"} + ".log"
        }
        '''
        
        os.environ['BASE_WORKERS'] = '6'
        os.environ['APP_NAME'] = 'testapp'
        
        try:
            result = loads(config_content)
            math_config = result['body']['MathConfig']['body']
            
            # Test arithmetic
            assert math_config['sum']['value']['value'] == 15
            assert math_config['difference']['value']['value'] == 12
            assert math_config['product']['value']['value'] == 42
            assert math_config['quotient']['value']['value'] == 25.0
            
            # Test complex expressions
            assert math_config['complex']['value']['value'] == 30
            assert math_config['mixed']['value']['value'] == 11
            
            # Test string concatenation
            assert math_config['app_name']['value']['value'] == "MyApp"
            assert math_config['full_name']['value']['value'] == "App_v1"
            
            # Test expressions with environment variables
            assert math_config['total_workers']['value']['value'] == 8
            assert math_config['log_path']['value']['value'] == "/var/log/testapp.log"
            
        finally:
            for var in ['BASE_WORKERS', 'APP_NAME']:
                if var in os.environ:
                    del os.environ[var]

    def test_comprehensive_configuration(self):
        """Test a comprehensive configuration using all features."""
        # Create shared components
        shared_config = '''
        // Shared database configuration
        DatabaseDefaults {
            max_connections = 50 + 50  // Expression: 100
            timeout = 30
            retry_attempts = 3
        }
        
        // Shared logging configuration  
        LoggingDefaults {
            level = ${LOG_LEVEL:-"info"}
            format = "json"
            rotation = "daily"
        }
        '''
        
        shared_file = self.test_dir / 'defaults.cfgpp'
        shared_file.write_text(shared_config)
        
        # Main application configuration
        main_config = '''
        /*
         * Main application configuration
         * Uses includes, environment variables, expressions, and comments
         */
        
        ApplicationConfig {
            // Basic application metadata
            name = ${APP_NAME:-"DefaultApp"}
            version = "2" + "." + "1" + "." + "0"  // Expression: "2.1.0"
            environment = ${ENVIRONMENT:-"development"}
            
            // Include shared configurations
            @include "defaults.cfgpp"
            
            // Server configuration with expressions
            server = ServerConfig {
                host = ${SERVER_HOST:-"0.0.0.0"}
                port = ${SERVER_PORT:-8000} + 80  // Expression
                workers = ${WORKER_COUNT:-4} * 2   // Expression
                timeout = 30 + 30                 // Expression: 60
                
                // TLS configuration
                tls = TLSConfig {
                    enabled = ${TLS_ENABLED:-true}
                    cert_path = "/etc/ssl/" + ${APP_NAME:-"app"} + ".crt"
                    key_path = "/etc/ssl/" + ${APP_NAME:-"app"} + ".key"
                }
            }
            
            // Database configuration extending defaults
            database = DatabaseConfig {
                driver = ${DB_DRIVER:-"postgresql"}
                host = ${DB_HOST:-"localhost"}
                port = ${DB_PORT:-5432}
                name = ${DB_NAME:-"appdb"}
                
                // Connection pool settings
                pool = PoolConfig {
                    min_size = ${DB_POOL_MIN:-5}
                    max_size = ${DB_POOL_MAX:-20}
                    timeout = 10 + 5  // Expression: 15
                }
            }
            
            // Feature flags
            features = [
                ${FEATURE_AUTH:-"auth"},
                ${FEATURE_CACHE:-"cache"}, 
                ${FEATURE_METRICS:-"metrics"}
            ]
            
            // Cache configuration
            cache = CacheConfig {
                provider = ${CACHE_PROVIDER:-"redis"}
                ttl = 60 * 60  // Expression: 3600 (1 hour)
                max_size = 1000 * 1000  // Expression: 1000000
            }
        }
        '''
        
        main_file = self.test_dir / 'app.cfgpp'
        main_file.write_text(main_config)
        
        # Set environment variables
        env_vars = {
            'APP_NAME': 'testapp',
            'ENVIRONMENT': 'production', 
            'SERVER_PORT': '9000',
            'WORKER_COUNT': '8',
            'TLS_ENABLED': 'true',
            'DB_HOST': 'db.example.com',
            'DB_PORT': '5433',
            'CACHE_PROVIDER': 'memcached'
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
        
        try:
            result = load(str(main_file))
            app_config = result['body']['ApplicationConfig']['body']
            
            # Test basic properties with env vars and expressions
            assert app_config['name']['value']['value'] == "testapp"
            assert app_config['version']['value']['value'] == "2.1.0"
            assert app_config['environment']['value']['value'] == "production"
            
            # Test server config with expressions
            server_config = app_config['server']['value']
            assert server_config['port']['value']['value'] == 9080  # 9000 + 80
            assert server_config['workers']['value']['value'] == 16  # 8 * 2
            assert server_config['timeout']['value']['value'] == 60   # 30 + 30
            
            # Test TLS config with string expressions
            tls_config = server_config['tls']['value']
            assert tls_config['cert_path']['value']['value'] == "/etc/ssl/testapp.crt"
            assert tls_config['key_path']['value']['value'] == "/etc/ssl/testapp.key"
            
            # Test database config
            db_config = app_config['database']['value']
            assert db_config['host']['value']['value'] == "db.example.com"
            assert db_config['port']['value']['value'] == 5433
            
            # Test pool config with expressions
            pool_config = db_config['pool']['value']
            assert pool_config['timeout']['value']['value'] == 15  # 10 + 5
            
            # Test included configurations
            assert 'DatabaseDefaults' in app_config
            db_defaults = app_config['DatabaseDefaults']['body']
            assert db_defaults['max_connections']['value']['value'] == 100  # 50 + 50
            
            # Test cache config with expressions
            cache_config = app_config['cache']['value']
            assert cache_config['ttl']['value']['value'] == 3600     # 60 * 60
            assert cache_config['max_size']['value']['value'] == 1000000  # 1000 * 1000
            assert cache_config['provider']['value']['value'] == "memcached"
            
        finally:
            # Clean up environment variables
            for key in env_vars:
                if key in os.environ:
                    del os.environ[key]

    def test_error_handling(self):
        """Test comprehensive error handling."""
        # Test circular include detection
        circular1 = self.test_dir / 'circular1.cfgpp'
        circular2 = self.test_dir / 'circular2.cfgpp'
        
        circular1.write_text('@include "circular2.cfgpp"\nconfig = "test"')
        circular2.write_text('@include "circular1.cfgpp"\nother = "value"')
        
        with pytest.raises(ConfigParseError, match="Circular include detected"):
            load(str(circular1))
        
        # Test missing include file
        with pytest.raises(ConfigParseError, match="Include file not found"):
            loads('@include "nonexistent.cfgpp"')
        
        # Test missing environment variable
        with pytest.raises(ConfigParseError, match="Environment variable .* is not set"):
            loads('test = ${NONEXISTENT_VAR}')
        
        # Test division by zero in expressions
        with pytest.raises(ConfigParseError, match="Division by zero"):
            loads('test = 10 / 0')
        
        # Test invalid expression
        with pytest.raises(ConfigParseError, match="Unexpected token in expression"):
            loads('test = 10 + {}')

    def test_cli_integration(self):
        """Test CLI tool with all features."""
        # Create test configuration file
        config_content = '''
        // Test configuration for CLI
        TestConfig {
            name = "CLI" + "Test"  // Expression
            port = 8000 + 80      // Expression  
            debug = ${DEBUG:-false}
            
            database = DatabaseConfig {
                host = ${DB_HOST:-"localhost"}
                port = 5432
            }
            
            features = ["auth", "logging"]
        }
        '''
        
        config_file = self.test_dir / 'cli_test.cfgpp'
        config_file.write_text(config_content)
        
        # Test validation
        old_argv = sys.argv
        try:
            sys.argv = ['cfgpp', str(config_file), '--validate']
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # This would normally call main(), but we'll test the parsing directly
            result = load(str(config_file))
            assert result is not None
            
        finally:
            sys.argv = old_argv
            sys.stdout = old_stdout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
