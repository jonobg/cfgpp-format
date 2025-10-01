# Advanced CFGPP Examples

**Master the sophisticated type system and advanced features!** ⭐⭐ Intermediate

These examples demonstrate CFGPP's advanced capabilities including complex enums, type validation, nested hierarchies, and sophisticated configuration patterns. Perfect for developers ready to leverage CFGPP's full power.

## 🎯 **Advanced Features Covered**

### **Complex Type System**
- **Enum inheritance and composition**
- **Advanced type validation and constraints**
- **Conditional logic and computed values**
- **Nested object hierarchies**

### **Sophisticated Patterns**
- **Array operations and transformations**
- **Object composition and inheritance**
- **Validation rules and custom constraints**
- **Dynamic configuration generation**

## 📚 **Examples in This Category**

| File | Description | Advanced Concepts |
|------|-------------|-------------------|
| **[complex-enums.cfgpp](complex-enums.cfgpp)** | Advanced enum definitions | Inheritance, constraints, computed values |
| **[enum-inheritance.cfgpp](enum-inheritance.cfgpp)** | Enum composition patterns | Base enums, extensions, overrides |
| **[type-validation.cfgpp](type-validation.cfgpp)** | Advanced type checking | Custom validators, constraints, rules |
| **[nested-hierarchies.cfgpp](nested-hierarchies.cfgpp)** | Deep object structures | Multi-level nesting, navigation |
| **[conditional-logic.cfgpp](conditional-logic.cfgpp)** | Dynamic configuration | If/when conditions, computed values |
| **[array-operations.cfgpp](array-operations.cfgpp)** | Array manipulation | Filtering, mapping, transformations |
| **[object-composition.cfgpp](object-composition.cfgpp)** | Object inheritance | Mixins, composition, polymorphism |
| **[validation-rules.cfgpp](validation-rules.cfgpp)** | Custom validation | Business rules, constraints, checks |

## 🔧 **Advanced Type System**

### **Complex Enums with Inheritance**
```cfgpp
enum::BaseLogLevel {
    values = ["debug", "info", "warn", "error"]
}

enum::ExtendedLogLevel extends BaseLogLevel {
    additional_values = ["trace", "fatal", "audit"],
    constraints = {
        "production" = ["warn", "error", "fatal"],
        "development" = ["trace", "debug", "info"]
    }
}
```

### **Type Validation with Custom Rules**
```cfgpp
DatabaseConfig::primary(
    string host = "localhost",
    int port = 5432
) {
    @validate {
        host.length > 0 && host.length <= 255,
        port > 0 && port <= 65535,
        port != 22 && port != 80 && port != 443  // Avoid system ports
    }
}
```

### **Conditional Configuration**
```cfgpp
ServerConfig::adaptive(
    string environment = "production"
) {
    @when(environment == "production") {
        int replicas = 5,
        string log_level = "warn"
    },
    @when(environment == "development") {
        int replicas = 1,
        string log_level = "debug"
    }
}
```

## 🏗️ **Nested Hierarchies**

### **Deep Object Structures**
```cfgpp
Enterprise::global(
    RegionConfig regions = RegionConfig(
        USConfig us = USConfig(
            DataCenterConfig east = DataCenterConfig(
                ServerConfig primary = ServerConfig(
                    CPUConfig cpu = CPUConfig(
                        CoreConfig core1 = CoreConfig(
                            int threads = 8
                        )
                    )
                )
            )
        )
    )
)

// Access: Enterprise.regions.us.east.primary.cpu.core1.threads
```

### **Navigation and Querying**
```cfgpp
// Find all CPU configurations
find_nodes_by_type("CPUConfig")

// Get all server configurations in US region
query("Enterprise.regions.us.*.*.cpu")

// List all data centers
list_children("Enterprise.regions.us")
```

## 🔄 **Array Operations**

### **Advanced Array Manipulation**
```cfgpp
ServerFarm::production(
    array[ServerConfig] servers = [
        ServerConfig(name = "web-001", cpu = 4, memory = 8),
        ServerConfig(name = "web-002", cpu = 8, memory = 16),
        ServerConfig(name = "web-003", cpu = 4, memory = 8)
    ]
) {
    // Filter high-memory servers
    @computed array[ServerConfig] high_memory_servers = 
        @filter(servers, server => server.memory >= 16)
    
    // Calculate total CPU
    @computed int total_cpu = 
        @sum(@map(servers, server => server.cpu))
    
    // Group by CPU count
    @computed object servers_by_cpu = 
        @group_by(servers, server => server.cpu)
}
```

## 🎭 **Object Composition**

### **Mixin Patterns**
```cfgpp
mixin::Loggable {
    string log_level = "info",
    bool enable_debug = false,
    string log_format = "json"
}

mixin::Monitorable {
    bool enable_metrics = true,
    int metrics_port = 9090,
    string metrics_path = "/metrics"
}

WebService::api includes Loggable, Monitorable {
    string name = "api-service",
    int port = 8080,
    
    // Inherited from Loggable: log_level, enable_debug, log_format
    // Inherited from Monitorable: enable_metrics, metrics_port, metrics_path
}
```

## ✅ **Validation Rules**

### **Custom Business Logic**
```cfgpp
PaymentConfig::processor(
    string provider = "stripe",
    float transaction_fee = 0.029,
    int max_amount_cents = 100000
) {
    @validate {
        // Business rule: Stripe has different fee structure
        @when(provider == "stripe") {
            transaction_fee >= 0.029 && transaction_fee <= 0.035
        },
        @when(provider == "paypal") {
            transaction_fee >= 0.025 && transaction_fee <= 0.040
        },
        
        // Security rule: Reasonable transaction limits
        max_amount_cents <= 10000000,  // $100,000 max
        max_amount_cents >= 100,       // $1 minimum
        
        // Compliance rule: Fee transparency
        transaction_fee <= 0.050  // Max 5% fee
    }
}
```

## 🧪 **Testing Advanced Features**

```bash
# Test complex enum validation
cd implementations/python
python -c "
from cfgpp.parser import loads
config = loads(open('specification/examples/advanced/complex-enums.cfgpp').read())
print('Enum validation:', config.validate_enums())
"

# Test nested hierarchy navigation
python -c "
from cfgpp.ai.extensions.hierarchical import HierarchicalExtension
# Test deep path access
result = config.query('Enterprise.regions.us.east.primary.cpu.core1.threads')
print('Deep lookup result:', result)
"

# Test validation rules
python -c "
from cfgpp.validation import ValidationEngine
validator = ValidationEngine()
result = validator.validate_config(config)
print('Validation result:', result)
"
```

## 🎯 **Learning Path**

### **Prerequisites**
Before diving into advanced examples, ensure you're comfortable with:
- **[Basic Examples](../basic/)** - Fundamental CFGPP concepts
- **[Keying Examples](../keying/)** - Hierarchical navigation

### **Progression Through Advanced Examples**
1. **Start with `complex-enums.cfgpp`** - Advanced enum patterns
2. **Move to `type-validation.cfgpp`** - Validation concepts
3. **Explore `nested-hierarchies.cfgpp`** - Deep structures
4. **Master `conditional-logic.cfgpp`** - Dynamic configuration
5. **Practice `array-operations.cfgpp`** - Data manipulation
6. **Study `object-composition.cfgpp`** - Inheritance patterns
7. **Complete `validation-rules.cfgpp`** - Business logic

### **Next Steps**
After mastering advanced features:
1. **[AI-Aware Examples](../ai-aware/)** - Revolutionary AI features
2. **[Real-World Examples](../real-world/)** - Production patterns
3. **[Integration Examples](../integration/)** - System integration

## 🌟 **Advanced Benefits**

### **Type Safety**
- **Compile-time validation** of configuration correctness
- **Custom constraint checking** for business rules
- **Enum inheritance** for extensible type systems
- **Polymorphic configuration** with type checking

### **Maintainability**
- **Hierarchical organization** for complex systems
- **Reusable patterns** through mixins and composition
- **Validation rules** prevent configuration errors
- **Clear structure** for large configuration files

### **Flexibility**
- **Conditional logic** for environment-specific config
- **Computed values** for dynamic configuration
- **Array operations** for data transformation
- **Custom validation** for domain-specific rules

### **AI Integration**
- **Structured reasoning** over complex hierarchies
- **Type-aware validation** for AI safety
- **Pattern recognition** in configuration structures
- **Automated optimization** based on constraints

---

*Master these advanced concepts and unlock CFGPP's full potential for sophisticated configuration management!* ⚡🚀
