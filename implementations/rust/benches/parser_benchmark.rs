use criterion::{black_box, criterion_group, criterion_main, Criterion};
use cfgpp::{Parser, CfgppValue};

fn benchmark_basic_parsing(c: &mut Criterion) {
    let config = r#"
    database {
        host = "localhost";
        port = 5432;
        ssl = true;
        connections = 100;
        timeout = 30.0;
    }
    
    servers = ["web1", "web2", "web3"];
    
    cache {
        enabled = true;
        size = 1024;
        ttl = 3600;
    }
    "#;

    c.bench_function("parse_basic_config", |b| {
        b.iter(|| {
            let mut parser = Parser::new();
            parser.parse(black_box(config)).unwrap()
        })
    });
}

fn benchmark_large_config(c: &mut Criterion) {
    let mut config = String::new();
    config.push_str("root {\n");
    
    for i in 0..1000 {
        config.push_str(&format!(
            r#"
    server_{} {{
        host = "server{}.example.com";
        port = {};
        enabled = true;
        load = {}.5;
    }}
"#, i, i, 8000 + i, i as f64 / 10.0
        ));
    }
    
    config.push_str("}\n");

    c.bench_function("parse_large_config", |b| {
        b.iter(|| {
            let mut parser = Parser::new();
            parser.parse(black_box(&config)).unwrap()
        })
    });
}

fn benchmark_nested_objects(c: &mut Criterion) {
    let config = r#"
    app {
        database {
            primary {
                host = "db1.example.com";
                port = 5432;
                credentials {
                    username = "admin";
                    password = "secret123";
                }
            }
            replica {
                host = "db2.example.com";
                port = 5432;
                credentials {
                    username = "readonly";
                    password = "readonly123";
                }
            }
        }
        
        services {
            web {
                instances = 3;
                port = 8080;
                health_check {
                    path = "/health";
                    interval = 30;
                }
            }
            api {
                instances = 2;
                port = 8081;
                health_check {
                    path = "/api/health";
                    interval = 15;
                }
            }
        }
    }
    "#;

    c.bench_function("parse_nested_objects", |b| {
        b.iter(|| {
            let mut parser = Parser::new();
            parser.parse(black_box(config)).unwrap()
        })
    });
}

fn benchmark_array_parsing(c: &mut Criterion) {
    let config = r#"
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    strings = ["hello", "world", "rust", "cfgpp", "parser"];
    booleans = [true, false, true, true, false];
    mixed = [1, "hello", true, 3.14, null];
    "#;

    c.bench_function("parse_arrays", |b| {
        b.iter(|| {
            let mut parser = Parser::new();
            parser.parse(black_box(config)).unwrap()
        })
    });
}

fn benchmark_env_var_expansion(c: &mut Criterion) {
    std::env::set_var("TEST_HOST", "localhost");
    std::env::set_var("TEST_PORT", "5432");
    
    let config = r#"
    database {
        host = ${TEST_HOST};
        port = ${TEST_PORT};
        url = ${DATABASE_URL:-"postgres://localhost:5432/test"};
    }
    "#;

    c.bench_function("parse_with_env_vars", |b| {
        b.iter(|| {
            let mut parser = Parser::new();
            parser.parse(black_box(config)).unwrap()
        })
    });
}

fn benchmark_value_access(c: &mut Criterion) {
    let config = r#"
    app {
        database {
            host = "localhost";
            port = 5432;
            settings {
                max_connections = 100;
                timeout = 30.0;
            }
        }
    }
    "#;

    let mut parser = Parser::new();
    let value = parser.parse(config).unwrap();

    c.bench_function("value_path_access", |b| {
        b.iter(|| {
            black_box(value.get_path("app.database.host"));
            black_box(value.get_path("app.database.port"));
            black_box(value.get_path("app.database.settings.max_connections"));
            black_box(value.get_path("app.database.settings.timeout"));
        })
    });
}

criterion_group!(
    benches,
    benchmark_basic_parsing,
    benchmark_large_config,
    benchmark_nested_objects,
    benchmark_array_parsing,
    benchmark_env_var_expansion,
    benchmark_value_access
);
criterion_main!(benches);
