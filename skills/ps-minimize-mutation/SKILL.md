---
name: ps-minimize-mutation
description: Mutation must be controlled and localized. Use when reviewing code with scattered mutations or shared mutable state.
severity: WARN
---

# Minimize Mutation

## Principle

Mutation should be:

- **Localized**: Confined to small, clear scopes
- **Explicit**: Visible at call sites when mutation occurs
- **Controlled**: Used only when beneficial for performance or clarity

Benefits:

- **Predictability**: Easier to reason about code when values don't change unexpectedly
- **Thread Safety**: Immutable data is inherently safe for concurrent access
- **Debugging**: Fewer moving parts, simpler data flow
- **Testing**: Pure operations are easier to test

## When to Use

**Use this skill when:**

- Reviewing code with shared mutable state
- Functions modify their arguments unexpectedly
- Objects change state across multiple locations
- Tracking down bugs related to unexpected data changes

**Indicators you need this:**

- Functions with surprising side effects
- Collections modified while being iterated
- Object properties changed far from creation
- Multiple functions sharing and modifying the same structure
- Debugging sessions tracing when a value changed

## Instructions

### Prefer Immutable Updates

**Create new values instead of modifying existing ones:**

- Return new collections rather than mutating inputs
- Use spread operators, Object.assign, or copy methods
- Build new objects with updated properties

### Localize Mutation When Necessary

**When mutation is appropriate (performance, builder patterns):**

- Keep mutations within a single function scope
- Don't expose mutable references outside the scope
- Return immutable results to callers

### Make Mutation Explicit

**Signal mutation at function boundaries:**

- Name functions to indicate mutation (update, modify, add)
- Document when parameters are mutated
- Avoid mutating function parameters received from callers

### Acceptable Mutation Contexts

**Mutation is reasonable when:**

- Building large data structures incrementally (builders)
- Performance-critical loops processing arrays
- Local variables within a function (not escaping scope)
- Implementing caches or memoization
- Managing UI component state

**Mutation should be avoided when:**

- Functions operate on shared data structures
- Arguments could be reused by the caller
- The mutation affects code outside current scope
- Immutable alternatives have negligible cost

## Examples

### ✅ Good: Immutable updates

```
FUNCTION addItem(cart, newItem):
    RETURN {
        ...cart,
        items: [...cart.items, newItem],
        total: cart.total + newItem.price
    }

FUNCTION removeItem(cart, itemId):
    updatedItems = cart.items.filter(item => item.id !== itemId)
    updatedTotal = updatedItems.sum(item => item.price)

    RETURN {
        ...cart,
        items: updatedItems,
        total: updatedTotal
    }

// Original cart unchanged
// New cart returned
// Caller decides what to do with result
```

_Functions create new values. Original data preserved. Safe for concurrent access._

### ❌ Bad: Mutation scattered

```
FUNCTION addItem(cart, newItem):
    cart.items.push(newItem)  // Mutates input
    cart.total = cart.total + newItem.price  // Mutates input
    RETURN cart

FUNCTION processOrder(cart):
    addItem(cart, { id: 1, price: 10 })  // Mutates cart
    addItem(cart, { id: 2, price: 20 })  // Mutates cart again

    // Later... is cart the original or modified?
    // Which functions modified it?
    // Hard to track changes

// Shared mutable state
// Unpredictable behavior
// Hard to test or reason about
```

_Functions modify shared state. Caller's data changed without clear signal. Race conditions possible._

## Common Patterns

### Immutable Collection Updates

**Arrays:**

- Add: `[...array, newItem]`
- Remove: `array.filter(item => item !== toRemove)`
- Update: `array.map(item => item.id === id ? updated : item)`
- Slice: `array.slice(start, end)`

**Objects:**

- Add/Update property: `{...obj, key: newValue}`
- Remove property: `{...obj}; delete result.key` or use destructuring
- Nested update: `{...obj, nested: {...obj.nested, key: value}}`

**Maps/Sets:**

- Create new instances with changes
- Or use within a local scope and return frozen copy

### Builder Pattern for Complex Construction

When building complex objects step-by-step:

- Use a builder class with mutation methods
- Return immutable result from `.build()` method
- Builder is local, result is shared immutably

### Copy-on-Write

- Clone before modification for shared structures
- Preserve original reference for other consumers
- Common in Redux, React state updates

## AI Review Checklist

Before accepting code, verify:

- [ ] Are function parameters mutated? Could new values be returned instead?
- [ ] Do collection operations modify the original collection?
- [ ] Is shared state mutated from multiple locations?
- [ ] Are mutations clearly signaled by function names?
- [ ] Is locally-scoped mutation actually beneficial here?
- [ ] Could immutable alternatives simplify the logic?

**If function mutates parameters → SUGGEST returning new value (SUGGEST)**

**If shared object is mutated → WARN about unpredictable behavior (WARN)**

**If collection is modified during iteration → WARN about bugs (WARN)**

## Language-Specific Guidance

### JavaScript/TypeScript

- Use `const` by default to prevent reassignment
- Spread syntax for shallow copies: `[...array]`, `{...object}`
- Array methods: `.map()`, `.filter()`, `.slice()` (non-mutating)
- Avoid: `.push()`, `.pop()`, `.splice()`, `.sort()` on shared arrays
- Immutable libraries: Immer, Immutable.js for deep structures

### Python

- Tuples for immutable sequences
- `dataclasses(frozen=True)` for immutable objects
- List comprehensions create new lists
- `.copy()` for shallow copies, `copy.deepcopy()` for deep
- Avoid mutating lists/dicts passed as arguments

### Java

- `final` for reference immutability
- Immutable collections: `List.of()`, `Set.of()`, `Map.of()`
- Records (Java 14+) for immutable data classes
- Defensive copies in constructors/getters
- Stream API for functional transformations

### Go

- Value semantics for structs (copies by default)
- Don't return pointers to mutable internal state
- Append to slices creates new backing array when needed
- Explicit copying with `copy()` for slices

## Common Questions

**Q: Isn't immutability inefficient?**  
A: Modern runtimes optimize immutable operations. Profile first. Immutability often prevents bugs that are more costly than minor performance differences.

**Q: When should I use mutation?**  
A: When building large structures in tight loops, implementing performance-critical algorithms, or when mutation is clearly scoped and doesn't escape the function.

**Q: How do I update nested immutable structures?**  
A: Use spreading at each level, or use libraries like Immer (JS), lenses (functional languages), or copy-on-write helpers. Keep nesting shallow when possible.

**Q: What about builder patterns?**  
A: Builders are fine—they use mutation internally but expose an immutable interface. The builder itself is transient and local.

## References

- "Effective Java" (Joshua Bloch) - Item 17: Minimize Mutability
- Redux documentation on immutability
- "Clojure for the Brave and True" - Immutable Data Structures
- Rich Hickey's talks on "The Value of Values"
