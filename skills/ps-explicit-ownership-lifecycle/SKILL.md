---
name: ps-explicit-ownership-lifecycle
description: Every resource must have clear ownership and lifetime. Use when reviewing resource management, subscriptions, or cleanup code.
severity: WARN
---

# Explicit Ownership Lifecycle

## Principle

Every resource must have exactly one clear owner responsible for its lifecycle. The owner creates, manages, and destroys the resource deterministically.

Benefits:

- **No leaks**: Resources always cleaned up
- **No double-free**: Single ownership prevents duplicate cleanup
- **Predictability**: Lifetime is explicit and obvious
- **Safety**: No use-after-free or dangling references

## When to Use

**Use this pattern when:**

- Working with limited resources (connections, file handles, memory)
- Managing subscriptions or event listeners
- Dealing with external systems (databases, APIs, hardware)
- Implementing cleanup logic

**Indicators you need this:**

- Memory leaks in production
- Unclosed connections or file handles
- Event listeners not unregistered
- Resources outliving their intended scope
- Cleanup code scattered or missing
- Unclear who should call `.close()` or `.dispose()`

## Instructions

### Establish clear ownership

1. **Single Owner Rule**
   - Every resource has exactly one owner at any time
   - Owner is responsible for cleanup
   - Ownership can be transferred but not shared

2. **Deterministic Lifecycle**
   - Clear creation point
   - Explicit usage scope
   - Predictable destruction point

3. **RAII Pattern (Resource Acquisition Is Initialization)**
   - Acquire resource in constructor/initializer
   - Release resource in destructor/finalizer
   - Automatic cleanup when owner goes out of scope

### Structure your code

1. **Make ownership explicit**
   - Use naming conventions (owned vs borrowed)
   - Document ownership in function signatures
   - Prefer constructor/destructor pairs

2. **Scope resources tightly**
   - Create resources close to usage
   - Destroy as soon as no longer needed
   - Avoid long-lived resources when possible

3. **Implement cleanup patterns**
   - Try-finally blocks for cleanup
   - Context managers / using statements
   - Dispose patterns with explicit cleanup
   - Weak references for non-owning relationships

### Common Pitfalls

❌ **Avoid:**

- Shared ownership without clear rules
- Resources outliving their scope
- Cleanup in finalizers/garbage collection only
- Passing ownership implicitly
- Forgetting cleanup in error paths

✅ **Do:**

- Make owner explicit in code structure
- Clean up in reverse order of acquisition
- Use language-provided cleanup mechanisms
- Document ownership transfer
- Handle errors without leaking resources

## Examples

### ✅ Good: Clear ownership with deterministic cleanup

```
FUNCTION processFile(filePath):
    file = openFile(filePath)  // Acquire resource
    TRY:
        data = file.read()
        result = processData(data)
        RETURN result
    FINALLY:
        file.close()  // Always cleanup, even on error

FUNCTION createConnection():
    connection = database.connect()
    RETURN ConnectionWrapper(connection)  // Transfer ownership

CLASS ConnectionWrapper:
    CONSTRUCTOR(connection):
        this.connection = connection

    METHOD use():
        RETURN this.connection.query(...)

    METHOD close():
        this.connection.disconnect()  // Owner responsible for cleanup
```

_Resource acquired, used in scope, cleaned up deterministically. Ownership clear at each step._

### ❌ Bad: Unclear ownership, missing cleanup

```
FUNCTION loadData(filePath):
    file = openFile(filePath)
    data = file.read()
    RETURN data  // File never closed - leak!

FUNCTION setupListener():
    eventBus.subscribe("event", handleEvent)
    // Who unsubscribes? When? Lifetime unclear.

GLOBAL connection = null

FUNCTION getConnection():
    IF connection IS null:
        connection = database.connect()
    RETURN connection  // Shared ownership - who closes?
```

_Resources created but never cleaned up. Ownership ambiguous. Leaks in error paths._

## Enforcement Checklist

Before accepting code, verify:

- [ ] Every resource has a clear owner (who creates it?)
- [ ] Cleanup is deterministic (not relying on GC alone)
- [ ] Error paths also clean up resources
- [ ] No resource outlives its intended scope
- [ ] Ownership transfer is explicit and documented
- [ ] Related resources cleaned up in correct order

**If resource created but no cleanup visible → WARN: "Where is this resource cleaned up?"**

**If cleanup only in finalizer/destructor → WARN: "Add deterministic cleanup (try-finally, using, defer)"**

**If multiple references to same resource → ASK: "Who owns this? Who is responsible for cleanup?"**

## Practical Patterns

### Pattern: Constructor/Destructor Pairing

Acquire in constructor, release in destructor. Use language's scope-based cleanup.

### Pattern: Try-Finally

Acquire resource, use in try block, clean up in finally block guarantees cleanup.

### Pattern: Context Managers

Use `with` (Python), `using` (C#), or `defer` (Go) for automatic cleanup.

### Pattern: Builder with Close

Builder pattern with explicit `.close()` or `.dispose()` method. Document who calls it.

### Pattern: Ownership Transfer

When transferring ownership, return resource and document that caller now owns it.

### Pattern: Weak References

For non-owning relationships, use weak references that don't prevent cleanup.

## Language-Specific Patterns

### JavaScript/TypeScript

- Use try-finally for cleanup
- Implement `.dispose()` or `.close()` methods
- Use WeakMap/WeakRef for non-owning references
- AbortController for cancellation
- Symbol.dispose for explicit resource management (TC39 proposal)

### Python

- Context managers with `__enter__` and `__exit__`
- `with` statement for automatic cleanup
- `contextlib.closing()` for objects with `.close()`
- Weak references via `weakref` module

### Go

- `defer` for cleanup (executes in reverse order)
- Explicit `.Close()` methods
- Context for cancellation and timeouts

### Rust

- RAII via Drop trait (automatic cleanup)
- Ownership system enforced by compiler
- Borrow checker prevents use-after-free

### C#

- `IDisposable` interface with `.Dispose()`
- `using` statement for automatic disposal
- Finalizers as backup (not primary mechanism)

### Java

- Try-with-resources for AutoCloseable
- Explicit `.close()` methods
- Avoid finalizers (deprecated)

## Common Questions

**Q: What if multiple objects need the same resource?**  
A: One object owns it, others borrow/reference it. Owner outlives borrowers. Or use shared ownership with reference counting (std::shared_ptr, Arc) but make this explicit.

**Q: When should cleanup happen in garbage-collected languages?**  
A: Immediately when done, not at garbage collection. GC is for memory; external resources need deterministic cleanup.

**Q: How do I handle cleanup in async code?**  
A: Same rules apply. Use async context managers, ensure cleanup in finally blocks of promises, or use cancellation tokens.

**Q: What about resources that need initialization after construction?**  
A: Use factory methods or builder patterns. Ensure partially constructed objects can still be safely cleaned up.

## Related Patterns

- **Single Responsibility**: Owner's responsibility includes cleanup
- **Fail-Fast**: Detect leaked resources early in development
- **Make Illegal States Unrepresentable**: Type system prevents invalid lifetimes

## References

- RAII (Resource Acquisition Is Initialization) - C++ core pattern
- Dispose Pattern - .NET Framework Design Guidelines
- Context Managers - Python PEP 343
- Ownership and Borrowing - Rust Book
