# CFGPP Examples

This document provides practical examples of CFGPP configuration files for common use cases.

## Table of Contents

1. [Web Application Configuration](#web-application-configuration)
2. [Database Configuration](#database-configuration)
3. [Microservices Configuration](#microservices-configuration)
4. [Deployment Configuration](#deployment-configuration)
5. [Feature Flags](#feature-flags)
6. [Logging Configuration](#logging-configuration)
7. [Security Configuration](#security-configuration)

## Web Application Configuration

### Basic Web Server

```cfgpp
// Web server configuration
WebServer {
    name = "MyWebApp"
    version = "1.2.3"
    
    server = HTTP::Server {
        host = "0.0.0.0"
        port = 8080
        max_connections = 1000
        timeout = 30.0
        
        middleware = [
            "cors",
            "compression", 
            "rate_limiting",
            "authentication"
        ]
    }
    
    static_files = StaticFiles {
        enabled = true
        path = "/static"
        directory = "./public"
        cache_duration = 3600
    }
    
    session = Session::Redis {
        host = "redis.example.com"
        port = 6379
        database = 1
        timeout = 300
        secure = true
    }
}
```

### Full-Stack Application

```cfgpp
// Complete web application stack
FullStackApp {
    name = "E-Commerce Platform"
    environment = "production"
    
    // Frontend configuration
    frontend = Frontend::React {
        build_path = "./dist"
        api_base_url = "https://api.example.com"
        cdn_url = "https://cdn.example.com"
        
        features = Frontend::Features {
            hot_reload = false
            source_maps = false
            analytics = true
            sentry_dsn = "${SENTRY_DSN}"
        }
    }
    
    // API Gateway
    api_gateway = API::Gateway {
        host = "api.example.com"
        port = 443
        ssl = true
        
        rate_limiting = RateLimit::Config {
            requests_per_minute = 1000
            burst_size = 100
            whitelist = [
                "192.168.1.0/24",
                "10.0.0.0/8"
            ]
        }
        
        cors = CORS::Policy {
            allowed_origins = [
                "https://example.com",
                "https://app.example.com"
            ]
            allowed_methods = ["GET", "POST", "PUT", "DELETE"]
            allowed_headers = ["Authorization", "Content-Type"]
        }
    }
    
    // Microservices
    services = [
        Service::Authentication {
            name = "auth-service"
            port = 3001
            database = "auth_db"
            jwt_secret = "${JWT_SECRET}"
        },
        Service::Users {
            name = "user-service"
            port = 3002
            database = "users_db"
        },
        Service::Orders {
            name = "order-service"
            port = 3003
            database = "orders_db"
        }
    ]
}
```

## Database Configuration

### Multi-Database Setup

```cfgpp
// Database cluster configuration
DatabaseCluster {
    // Primary database
    primary = Database::PostgreSQL {
        host = "db-primary.example.com"
        port = 5432
        database = "myapp_prod"
        username = "app_user"
        password = "${DB_PASSWORD}"
        
        connection_pool = Pool::Config {
            min_connections = 5
            max_connections = 50
            idle_timeout = 300
            connection_timeout = 10
        }
        
        ssl = SSL::Config {
            enabled = true
            ca_cert = "/etc/ssl/ca.crt"
            client_cert = "/etc/ssl/client.crt"
            client_key = "/etc/ssl/client.key"
        }
    }
    
    // Read replicas
    replicas = [
        Database::PostgreSQL {
            host = "db-replica-1.example.com"
            port = 5432
            database = "myapp_prod"
            readonly = true
        },
        Database::PostgreSQL {
            host = "db-replica-2.example.com"
            port = 5432
            database = "myapp_prod"
            readonly = true
        }
    ]
    
    // Cache layer
    cache = Cache::Redis {
        cluster = [
            Redis::Node {
                host = "redis-1.example.com"
                port = 6379
                role = "master"
            },
            Redis::Node {
                host = "redis-2.example.com"
                port = 6379
                role = "slave"
            },
            Redis::Node {
                host = "redis-3.example.com"
                port = 6379
                role = "slave"
            }
        ]
        
        failover = Failover::Config {
            enabled = true
            timeout = 5.0
            retry_attempts = 3
        }
    }
    
    // Analytics database
    analytics = Database::ClickHouse {
        host = "analytics.example.com"
        port = 9000
        database = "analytics"
        
        batch_config = Batch::Config {
            size = 1000
            timeout = 60.0
            compression = true
        }
    }
}
```

## Microservices Configuration

### Service Mesh Configuration

```cfgpp
// Microservices mesh configuration
ServiceMesh {
    name = "payment-system"
    namespace = "payments"
    
    // Service registry
    registry = ServiceRegistry::Consul {
        host = "consul.example.com"
        port = 8500
        datacenter = "us-east-1"
        
        health_checks = HealthCheck::Config {
            interval = 10
            timeout = 3
            deregister_after = 30
        }
    }
    
    // Load balancer
    load_balancer = LoadBalancer::HAProxy {
        algorithm = "round_robin"
        health_check_uri = "/health"
        
        backends = [
            Backend::Service {
                name = "payment-api"
                instances = 3
                port = 8080
            },
            Backend::Service {
                name = "payment-processor"
                instances = 2
                port = 8081
            }
        ]
    }
    
    // Message queue
    messaging = Messaging::RabbitMQ {
        host = "mq.example.com"
        port = 5672
        virtual_host = "/payments"
        
        exchanges = [
            Exchange::Topic {
                name = "payment.events"
                durable = true
                auto_delete = false
            },
            Exchange::Direct {
                name = "payment.commands"
                durable = true
                auto_delete = false
            }
        ]
        
        queues = [
            Queue::Config {
                name = "payment.processing"
                durable = true
                exclusive = false
                auto_delete = false
                arguments = {
                    "x-message-ttl" = 300000
                    "x-max-retries" = 3
                }
            }
        ]
    }
    
    // Monitoring
    monitoring = Monitoring::Prometheus {
        endpoint = "/metrics"
        port = 9090
        
        metrics = [
            Metric::Counter {
                name = "payments_total"
                help = "Total number of payments processed"
                labels = ["status", "method"]
            },
            Metric::Histogram {
                name = "payment_duration_seconds"
                help = "Payment processing duration"
                buckets = [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
            }
        ]
    }
}
```

## Deployment Configuration

### Kubernetes Deployment

```cfgpp
// Kubernetes application deployment
KubernetesDeployment {
    metadata = Metadata {
        name = "myapp"
        namespace = "production"
        labels = {
            "app" = "myapp"
            "version" = "v1.2.3"
            "environment" = "production"
        }
    }
    
    deployment = Deployment::Config {
        replicas = 3
        
        strategy = Strategy::RollingUpdate {
            max_surge = 1
            max_unavailable = 0
        }
        
        template = Pod::Template {
            containers = [
                Container::App {
                    name = "myapp"
                    image = "myregistry/myapp:v1.2.3"
                    port = 8080
                    
                    resources = Resources::Limits {
                        cpu = "500m"
                        memory = "512Mi"
                        
                        requests = Resources::Requests {
                            cpu = "250m"
                            memory = "256Mi"
                        }
                    }
                    
                    env_vars = [
                        EnvVar::Secret {
                            name = "DATABASE_URL"
                            secret_name = "db-credentials"
                            secret_key = "url"
                        },
                        EnvVar::ConfigMap {
                            name = "API_BASE_URL"
                            config_map = "app-config"
                            key = "api_url"
                        }
                    ]
                    
                    health_checks = HealthChecks {
                        liveness_probe = Probe::HTTP {
                            path = "/health"
                            port = 8080
                            initial_delay = 30
                            period = 10
                        }
                        
                        readiness_probe = Probe::HTTP {
                            path = "/ready"
                            port = 8080
                            initial_delay = 5
                            period = 5
                        }
                    }
                }
            ]
        }
    }
    
    services = [
        Service::ClusterIP {
            name = "myapp-service"
            port = 80
            target_port = 8080
            selector = {
                "app" = "myapp"
            }
        }
    ]
    
    ingress = Ingress::NGINX {
        name = "myapp-ingress"
        host = "myapp.example.com"
        
        tls = TLS::Config {
            secret_name = "myapp-tls"
            hosts = ["myapp.example.com"]
        }
        
        annotations = {
            "cert-manager.io/cluster-issuer" = "letsencrypt-prod"
            "nginx.ingress.kubernetes.io/rate-limit" = "100"
        }
    }
}
```

## Feature Flags

### Feature Flag Configuration

```cfgpp
// Feature flags management
FeatureFlags {
    provider = FeatureProvider::LaunchDarkly {
        sdk_key = "${LAUNCHDARKLY_SDK_KEY}"
        base_uri = "https://app.launchdarkly.com"
        
        default_config = DefaultConfig {
            offline = false
            events_capacity = 10000
            flush_interval = 5.0
        }
    }
    
    flags = [
        Flag::Boolean {
            key = "new_checkout_flow"
            name = "New Checkout Flow"
            description = "Enable the redesigned checkout process"
            default_value = false
            
            variations = [
                Variation {
                    value = true
                    name = "Enabled"
                    description = "New checkout flow is active"
                },
                Variation {
                    value = false
                    name = "Disabled"
                    description = "Use legacy checkout flow"
                }
            ]
            
            targeting = Targeting::Rules {
                rules = [
                    Rule {
                        conditions = [
                            Condition {
                                attribute = "email"
                                operator = "endsWith"
                                values = ["@company.com"]
                            }
                        ]
                        variation = true
                        rollout = 100
                    }
                ]
                
                default_rule = DefaultRule {
                    variation = false
                    rollout = Rollout::Percentage {
                        percentage = 25
                        attribute = "user_id"
                    }
                }
            }
        },
        
        Flag::String {
            key = "api_version"
            name = "API Version"
            description = "Which API version to use"
            default_value = "v1"
            
            variations = [
                Variation {
                    value = "v1"
                    name = "Version 1"
                },
                Variation {
                    value = "v2"
                    name = "Version 2"
                },
                Variation {
                    value = "v3"
                    name = "Version 3 (Beta)"
                }
            ]
        }
    ]
    
    environments = [
        Environment {
            name = "development"
            key = "dev"
            default_ttl = 300
        },
        Environment {
            name = "staging"
            key = "staging"
            default_ttl = 600
        },
        Environment {
            name = "production"
            key = "prod"
            default_ttl = 3600
        }
    ]
}
```

## Logging Configuration

### Structured Logging Setup

```cfgpp
// Comprehensive logging configuration
LoggingConfig {
    // Global settings
    global = Global::Settings {
        level = "INFO"
        format = "json"
        timezone = "UTC"
        
        correlation = Correlation::Config {
            header_name = "X-Correlation-ID"
            generate_if_missing = true
        }
    }
    
    // Output destinations
    outputs = [
        Output::Console {
            name = "console"
            enabled = true
            level = "DEBUG"
            format = "human"
            
            colors = Colors::Config {
                enabled = true
                level_colors = {
                    "DEBUG" = "cyan"
                    "INFO" = "green"
                    "WARN" = "yellow"
                    "ERROR" = "red"
                }
            }
        },
        
        Output::File {
            name = "application"
            enabled = true
            level = "INFO"
            format = "json"
            
            rotation = Rotation::Config {
                max_size = "100MB"
                max_files = 10
                compress = true
            }
            
            path = "/var/log/app/application.log"
        },
        
        Output::Syslog {
            name = "syslog"
            enabled = true
            level = "WARN"
            facility = "local0"
            network = "udp"
            address = "syslog.example.com:514"
        },
        
        Output::Elasticsearch {
            name = "elasticsearch"
            enabled = true
            level = "INFO"
            
            cluster = ES::Cluster {
                hosts = [
                    "es-1.example.com:9200",
                    "es-2.example.com:9200",
                    "es-3.example.com:9200"
                ]
                
                auth = ES::Auth {
                    username = "logstash"
                    password = "${ES_PASSWORD}"
                }
                
                ssl = ES::SSL {
                    enabled = true
                    verify_certs = true
                    ca_file = "/etc/ssl/es-ca.crt"
                }
            }
            
            index = ES::Index {
                pattern = "app-logs-%{+yyyy.MM.dd}"
                template = "app-logs-template"
                
                settings = {
                    "number_of_shards" = 3
                    "number_of_replicas" = 1
                    "refresh_interval" = "5s"
                }
            }
        }
    ]
    
    // Logger configurations
    loggers = [
        Logger::Config {
            name = "root"
            level = "INFO"
            outputs = ["console", "application", "elasticsearch"]
        },
        
        Logger::Config {
            name = "database"
            level = "WARN"
            outputs = ["application", "syslog"]
            
            filters = [
                Filter::Regex {
                    field = "message"
                    pattern = "SELECT.*FROM.*"
                    action = "exclude"
                }
            ]
        },
        
        Logger::Config {
            name = "security"
            level = "DEBUG"
            outputs = ["syslog", "elasticsearch"]
            
            enrichment = Enrichment::Config {
                fields = {
                    "component" = "security"
                    "criticality" = "high"
                }
            }
        }
    ]
    
    // Structured logging fields
    structured_fields = StructuredFields {
        request_id = Field::UUID {
            source = "header"
            header_name = "X-Request-ID"
            generate_if_missing = true
        }
        
        user_id = Field::String {
            source = "context"
            context_key = "user.id"
            default_value = "anonymous"
        }
        
        ip_address = Field::IP {
            source = "request"
            field = "remote_addr"
            anonymize = true
        }
        
        timestamp = Field::Timestamp {
            format = "rfc3339"
            precision = "milliseconds"
        }
    }
}
```

## Security Configuration

### Authentication & Authorization

```cfgpp
// Security configuration
SecurityConfig {
    // Authentication providers
    authentication = Auth::Providers {
        primary = Auth::JWT {
            issuer = "https://auth.example.com"
            audience = "api.example.com"
            algorithm = "RS256"
            
            jwks = JWKS::Config {
                url = "https://auth.example.com/.well-known/jwks.json"
                cache_duration = 3600
                refresh_interval = 300
            }
            
            claims = Claims::Config {
                required = ["sub", "iss", "aud", "exp"]
                optional = ["name", "email", "roles"]
                
                validation = Claims::Validation {
                    verify_expiration = true
                    verify_not_before = true
                    leeway = 60
                }
            }
        }
        
        fallback = Auth::ApiKey {
            header_name = "X-API-Key"
            query_param = "api_key"
            
            validation = ApiKey::Validation {
                min_length = 32
                allowed_chars = "alphanumeric"
                rate_limiting = true
            }
        }
    }
    
    // Authorization policies
    authorization = AuthZ::RBAC {
        roles = [
            Role {
                name = "admin"
                description = "Full system access"
                permissions = [
                    "users:*",
                    "system:*",
                    "audit:read"
                ]
            },
            
            Role {
                name = "user"
                description = "Standard user access"
                permissions = [
                    "profile:read",
                    "profile:write",
                    "orders:read",
                    "orders:create"
                ]
            },
            
            Role {
                name = "readonly"
                description = "Read-only access"
                permissions = [
                    "profile:read",
                    "orders:read"
                ]
            }
        ]
        
        policies = [
            Policy::ResourceBased {
                name = "resource_owner"
                description = "Users can access their own resources"
                condition = "resource.owner_id == user.id"
                effect = "allow"
            },
            
            Policy::TimeBased {
                name = "business_hours"
                description = "Admin access only during business hours"
                condition = "user.role == 'admin' && time.hour >= 9 && time.hour <= 17"
                effect = "allow"
            }
        ]
    }
    
    // Encryption settings
    encryption = Encryption::Config {
        // Data at rest
        at_rest = Encryption::AES {
            algorithm = "AES-256-GCM"
            key_derivation = "PBKDF2"
            iterations = 100000
            
            key_management = KeyMgmt::Vault {
                address = "https://vault.example.com"
                token = "${VAULT_TOKEN}"
                mount_path = "secret/app"
                key_rotation = 2592000  // 30 days
            }
        }
        
        // Data in transit
        in_transit = Encryption::TLS {
            min_version = "1.2"
            cipher_suites = [
                "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305"
            ]
            
            certificates = TLS::Certificates {
                cert_file = "/etc/ssl/certs/app.crt"
                key_file = "/etc/ssl/private/app.key"
                ca_file = "/etc/ssl/certs/ca.crt"
                
                auto_renewal = AutoRenewal::ACME {
                    provider = "letsencrypt"
                    email = "admin@example.com"
                    staging = false
                }
            }
        }
    }
    
    // Security headers
    security_headers = Security::Headers {
        strict_transport_security = "max-age=31536000; includeSubDomains"
        content_type_options = "nosniff"
        frame_options = "SAMEORIGIN"
        xss_protection = "1; mode=block"
        referrer_policy = "strict-origin-when-cross-origin"
        
        content_security_policy = CSP::Policy {
            default_src = ["'self'"]
            script_src = ["'self'", "'unsafe-inline'", "cdn.example.com"]
            style_src = ["'self'", "'unsafe-inline'", "fonts.googleapis.com"]
            img_src = ["'self'", "data:", "*.example.com"]
            font_src = ["'self'", "fonts.gstatic.com"]
            connect_src = ["'self'", "api.example.com"]
        }
    }
}
```

These examples demonstrate real-world configuration patterns using CFGPP's features like namespaced types, nested objects, arrays, and type declarations. Each example shows how CFGPP can handle complex configuration scenarios while maintaining readability and structure.
