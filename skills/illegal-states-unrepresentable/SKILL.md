---
name: illegal-states-unrepresentable
description: System design should prevent misuse by construction. Use when reviewing defensive code with runtime checks.
---

# Illegal States Unrepresentable

## Principle

Design data structures so that illegal states cannot be represented. Use the type system to enforce invariants at compile time rather than runtime validation.

Benefits:
- **Correctness**: Invalid states literally cannot exist
- **Maintainability**: Eliminate defensive runtime checks
- **Clarity**: Type declarations document valid states
- **Refactoring safety**: Type errors catch breaking changes

## When to Use

**Use this pattern when:**
- Multiple fields have interdependent constraints
- Boolean flags create ambiguous combinations
- Validation logic is scattered across the codebase
- Runtime errors indicate impossible states were reached

**Indicators you need this:**
- Multiple booleans that shouldn't all be true/false together
- Fields that are only valid in certain states
- Comments explaining "if X then Y must be Z"
- Defensive assertions checking state consistency
- Nullable fields that are "sometimes required"

## Instructions

### Replace primitive obsession with domain types

1. **Identify invalid state combinations**
   - Map out which field combinations are meaningless
   - Note which validations are performed at runtime
   - Find booleans that represent states, not properties

2. **Model states explicitly with union types**
   - Create a type/variant for each valid state
   - Include only relevant fields in each variant
   - Use discriminated unions (tagged unions)

3. **Parse, don't validate**
   - Accept raw input at boundaries
   - Parse into domain types immediately
   - Internal code works only with validated types
   - Make invalid data unrepresentable

### Common Transformations

**Boolean pairs → Enum/Union:**
- `{ loading: bool, error: bool, data: T }` → Union of Loading | Error | Success states

**Nullable with conditions → Discriminated union:**
- `{ status: string, error?: string, result?: T }` → Explicit state variants

**Multiple modes → Sum types:**
- `{ editMode: bool, viewMode: bool }` → Single Mode enum

### Common Pitfalls

❌ **Avoid:**
- Representing states with multiple independent booleans
- Using strings/numbers for states without type constraints
- Nullable fields that are "required in some cases"
- Validation functions that check state consistency
- Comments explaining when fields are valid

✅ **Do:**
- Use discriminated unions for mutually exclusive states
- Make illegal combinations unrepresentable in types
- Parse external data into constrained types at boundaries
- Let the compiler enforce state transitions
- Encode business rules in types, not runtime checks

## Examples

### ✅ Good: States are distinct types

```
TYPE RemoteData<T> =
    | NotAsked
    | Loading
    | Success(data: T)
    | Failure(error: string)

FUNCTION render(state: RemoteData<User>):
    MATCH state:
        CASE NotAsked:
            RETURN "Click to load"
        CASE Loading:
            RETURN "Loading..."
        CASE Success(data):
            RETURN displayUser(data)
        CASE Failure(error):
            RETURN showError(error)

// Impossible states:
// - Loading AND has data
// - Success without data
// - Failure without error message
```

*Type system prevents invalid states. Compiler catches missing cases.*

### ❌ Bad: Booleans allow invalid combinations

```
STRUCTURE RemoteData<T>:
    isLoading: boolean
    isError: boolean
    data: T OR null
    error: string OR null

FUNCTION render(state: RemoteData<User>):
    IF state.isLoading AND state.isError:
        // Can this happen? Should we show loading or error?
        
    IF state.data IS NOT null AND state.isError:
        // Have both data and error? Which to display?
        
    // Must defensively check all combinations
    // Still might miss edge cases

// Possible states: 2^4 = 16 combinations
// Valid states: 4
// Invalid states we must handle: 12
```

*Most combinations are meaningless. Runtime checks scattered everywhere.*

## Type System Strategies

### Discriminated Unions (TypeScript/Flow)
Use a discriminant field to distinguish variants. The type system narrows based on discriminant checks.

### Algebraic Data Types (Rust/Haskell/Scala)
Sum types (enums with data) naturally prevent invalid combinations.

### Phantom Types (Advanced)
Use type parameters that exist only at compile time to track state.

### Builder Pattern with States
Encode construction order in types so incomplete objects can't exist.

## Enforcement

**Code review checklist:**
- [ ] Are multiple booleans modeling a single state?
- [ ] Are there nullable fields that are "sometimes required"?
- [ ] Do comments explain field interdependencies?
- [ ] Are validation functions checking state consistency?
- [ ] Could invalid states be made unrepresentable?

**If you see defensive assertions → SUGGEST making state unrepresentable**
**If you see validation checking field combinations → WARN about type design**
**If multiple booleans control behavior → SUGGEST discriminated union**

## Common Questions

**Q: Doesn't this just move validation earlier?**  
A: Yes, but crucially to a single boundary where external data enters. Internal code operates on guaranteed-valid types.

**Q: What about backward compatibility with existing APIs?**  
A: Parse external format at the boundary. Internal representation can be better structured.

**Q: Is this overkill for simple cases?**  
A: If you have runtime checks for "impossible" states, this prevents real bugs. Simple cases don't need it.

**Q: How does this work in languages without algebraic types?**  
A: Use classes/interfaces with factory methods. Constructor is private; factories return only valid instances.

## Related Patterns

- **Parse, Don't Validate**: Transformation to validated types at boundaries
- **Functional Core, Imperative Shell**: Core uses domain types; shell handles parsing
- **Type-Driven Development**: Let types guide implementation
- **Builder Pattern**: Can enforce construction order via types

## References

- Yaron Minsky: "Make Illegal States Unrepresentable" (OCaml)
- Alexis King: "Parse, Don't Validate"
- Rich Hickey: "Simple Made Easy" (on truth and information)
