# Documentation Updates Needed

## 🔍 Files Found with Old API Usage

### High Priority (User-Facing):
1. ✅ **docs/api-reference.md** - UPDATED with new API and legacy warnings
2. ✅ **QUICKSTART.md** - UPDATED with new API examples  
3. **docs/getting-started.md** - Contains `loads()` examples
4. **docs/error-handling.md** - Multiple `loads()` examples  
5. **docs/contributing.md** - Test examples use `loads()`

### Medium Priority (Technical Docs):
6. **docs/implementation-strategy-risk-minimized.md** - Implementation examples
7. **docs/immediate-next-steps.md** - Performance examples

## 🎯 Update Strategy

For each file, we need to:
1. **Add new API examples first** (parse_string, parse_file)
2. **Show legacy API as secondary option** with deprecation notice
3. **Maintain backward compatibility documentation**
4. **Encourage migration to new clearer API**

## ✅ Pattern for Updates:

**Before:**
```python
from cfgpp import loads
result = loads(config_text)
```

**After:**
```python
# New clear API (recommended)
from cfgpp import parse_string
result = parse_string(config_text)

# Legacy API (still works but less clear)  
from cfgpp import loads
result = loads(config_text)  # Use parse_string() instead
```
