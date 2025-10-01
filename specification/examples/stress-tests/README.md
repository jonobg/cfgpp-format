# CFGPP Stress Tests and Advanced Examples

## 🚨 **WARNING: EXTREME CONFIGURATIONS AHEAD!**

This directory contains **ultra-advanced CFGPP configurations** that push the parser to its absolute limits. These examples are designed to:

- **Stress test** parser performance and memory usage
- **Validate** complex syntax combinations
- **Benchmark** parsing speed on various hardware
- **Test** edge cases and boundary conditions
- **Demonstrate** maximum CFGPP capabilities

## 📊 **Performance Baseline (15-year-old Hardware)**

**Test Environment:**
- **CPU**: Intel Core 2 Duo / AMD equivalent (~2008-2010)
- **RAM**: 4-8GB DDR2/DDR3
- **Storage**: Traditional HDD (not SSD)
- **OS**: Windows/Linux with legacy drivers

**Expected Performance Targets:**
- **Small configs** (<10KB): <100ms parse time
- **Medium configs** (10-100KB): <500ms parse time  
- **Large configs** (100KB-1MB): <2000ms parse time
- **Massive configs** (1MB+): <10000ms parse time
- **Memory usage**: <512MB for any single config

## 🧪 **Test Categories**

### **1. Parser Stress Tests** (`parser-stress/`)
- **Deeply nested hierarchies** (20+ levels)
- **Massive arrays** (10,000+ elements)
- **Complex cross-references** (1000+ @ref() calls)
- **Large string literals** (1MB+ text blocks)

### **2. Performance Benchmarks** (`benchmarks/`)
- **Parsing speed** measurements
- **Memory consumption** tracking
- **Cross-reference resolution** timing
- **Validation performance** metrics

### **3. Advanced Feature Tests** (`advanced-features/`)
- **AI-aware configurations** with full feature sets
- **Enterprise-grade** security and compression
- **Industrial IoT** with thousands of sensors
- **Disaster recovery** with complex failover logic

### **4. Edge Case Validation** (`edge-cases/`)
- **Unicode and special characters**
- **Circular reference** detection
- **Malformed syntax** recovery
- **Memory limit** boundary testing

## 🎯 **Testing Methodology**

### **Performance Testing**
```bash
# Run parser performance tests
python test_parser_performance.py --config stress-tests/benchmarks/
python test_memory_usage.py --config stress-tests/advanced-features/
python test_validation_speed.py --config stress-tests/parser-stress/
```

### **Compatibility Testing**
```bash
# Test on legacy hardware simulation
python test_legacy_performance.py --simulate-old-hardware
python test_memory_constraints.py --max-memory 512MB
python test_slow_disk.py --simulate-hdd
```

### **Regression Testing**
```bash
# Ensure advanced configs don't break basic functionality
python test_regression.py --basic-examples --stress-examples
```

## 📈 **Success Criteria**

### **✅ Parser Robustness**
- **Zero crashes** on any valid CFGPP syntax
- **Graceful error handling** for invalid syntax
- **Memory cleanup** after parsing failures
- **Consistent results** across multiple runs

### **✅ Performance Targets**
- **Sub-second parsing** for configs <100KB
- **Linear memory scaling** with config size
- **Efficient cross-reference** resolution
- **Reasonable performance** on 15-year-old hardware

### **✅ Feature Validation**
- **All AI-aware features** work correctly
- **Compression and hashing** validate properly
- **Complex keying systems** resolve accurately
- **Enterprise features** maintain security

## 🚀 **Advanced Examples Moved Here**

The following **ultra-advanced examples** have been moved to stress tests:

### **From `ai-aware/`:**
- `ai-reasoning-modes.ai.cfgpp` → `advanced-features/ai-reasoning-modes.ai.cfgpp`
- `trust-networks.ai.cfgpp` → `advanced-features/trust-networks.ai.cfgpp`
- `streaming-compression.c.cfgpp` → `advanced-features/streaming-compression.c.cfgpp`

### **From `real-world/`:**
- `disaster-recovery.c.h.cfgpp` → `advanced-features/disaster-recovery.c.h.cfgpp`
- `security-policy.h.s.cfgpp` → `advanced-features/security-policy.h.s.cfgpp`
- `industrial-automation.k.cfgpp` → `advanced-features/industrial-automation.k.cfgpp`

### **From `keying/`:**
- `key-performance-benchmark.k.cfgpp` → `benchmarks/key-performance-benchmark.k.cfgpp`

## 🔧 **Testing Tools**

### **Performance Profiler**
```python
# Example usage
from cfgpp_profiler import ProfileParser

profiler = ProfileParser()
results = profiler.benchmark_file("stress-tests/benchmarks/massive-config.cfgpp")
print(f"Parse time: {results.parse_time_ms}ms")
print(f"Memory usage: {results.peak_memory_mb}MB")
print(f"Cross-refs resolved: {results.cross_ref_count}")
```

### **Memory Monitor**
```python
# Track memory usage during parsing
from cfgpp_memory import MemoryMonitor

monitor = MemoryMonitor()
with monitor.track():
    config = parse_cfgpp_file("stress-tests/advanced-features/ai-reasoning-modes.ai.cfgpp")
print(f"Peak memory: {monitor.peak_usage_mb}MB")
```

## 📋 **Test Results Template**

```markdown
## Test Results - [Date]

**Hardware:** [CPU/RAM/Storage details]
**Parser Version:** [Version]
**Test Duration:** [Time]

### Performance Results
| Config File | Size | Parse Time | Memory Usage | Cross-Refs | Status |
|-------------|------|------------|--------------|------------|--------|
| basic-example.cfgpp | 2KB | 15ms | 8MB | 5 | ✅ |
| ai-reasoning-modes.ai.cfgpp | 45KB | 250ms | 64MB | 127 | ✅ |
| industrial-automation.k.cfgpp | 78KB | 420ms | 89MB | 234 | ✅ |
| disaster-recovery.c.h.cfgpp | 123KB | 680ms | 156MB | 89 | ✅ |

### Issues Found
- [List any parsing failures, performance issues, or memory problems]

### Recommendations
- [Suggestions for parser improvements or config optimizations]
```

## 🎯 **Next Steps**

1. **Move advanced examples** to appropriate stress test directories
2. **Create performance benchmarks** for each category
3. **Implement automated testing** pipeline
4. **Document performance baselines** for different hardware
5. **Optimize parser** based on stress test results

## 🌟 **Goal: Production-Ready Parser**

These stress tests ensure that CFGPP can handle:
- **Enterprise-scale configurations** with thousands of elements
- **AI-aware features** without performance degradation  
- **Complex cross-referencing** with O(1) lookup performance
- **Legacy hardware compatibility** for broad adoption
- **Graceful failure handling** under extreme conditions

**Let's make CFGPP bulletproof! 🛡️⚡**
