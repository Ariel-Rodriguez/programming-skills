---
name: ps-explicit-state-invariants
description: Ensures state is intentionally designed with explicit invariants. Use when reviewing stateful code, designing data models, or refactoring boolean flag explosions. Prevents impossible states and race conditions.
severity: BLOCK
---

# Explicit State & Invariants

## Principle

State must be intentionally designed and always valid. Every piece of state must obey explicit invariants at all times.

**If you can't state the invariant, the state is already broken.**

Benefits:

- **Reliability**: Impossible states become unrepresentable
- **Debuggability**: Invalid states eliminated at design time
- **Maintainability**: Invariants encoded in type system, not documentation

## When to Use

**Use this pattern when:**

- Designing state shapes for components or stores
- Reviewing code with multiple boolean flags
- Implementing state machines or workflows
- Designing APIs that manage state

**Indicators you need this:**

- Boolean flag combinations creating invalid states
- Race conditions from temporarily invalid state
- Defensive checks scattered throughout codebase
- Comments explaining "don't do X when Y is true"

## Instructions

### Design state intentionally

1. **Identify valid states**
   - List all legitimate states your system can be in
   - Not combinations of flags, but discrete states
   - Example: `idle`, `loading`, `loaded`, `error` (not `isLoading && hasError`)

2. **State the invariants**
   - What must always be true?
   - Write them down explicitly
   - Encode them in types when possible

3. **Make invalid states unrepresentable**
   - Use tagged unions/sum types
   - Eliminate independent boolean flags
   - Group related data together

### Preserve invariants during transitions

1. **Atomic state changes**
   - Move from one valid state directly to another
   - Never leave state temporarily broken
   - Use transactions or single assignments

2. **Explicit transition functions**
   - Named functions for each state change
   - Document allowed transitions
   - Validate preconditions

3. **Handle temporary transition data**
   - Model transitions as distinct states
   - Include both old and new data if needed
   - Clean up transition state when complete

### Common Pitfalls

❌ **Avoid:**

- Multiple independent boolean flags
- Undocumented invariants (living in human memory)
- Temporarily invalid state during updates
- Optional fields that are only sometimes valid

✅ **Do:**

- Use discriminated unions for mutually exclusive states
- Encode invariants in type system
- Document what must always be true
- Make optionality explicit and intentional

## Examples

### ✅ Good: Explicit states with invariants

```
TYPE RequestState =
    | Idle
    | Loading
    | Success(data)
    | Error(message)

FUNCTION render(state):
    MATCH state:
        CASE Idle:
            RETURN "Click to load"
        CASE Loading:
            RETURN "Loading..."
        CASE Success(data):
            RETURN displayData(data)
        CASE Error(message):
            RETURN showError(message)

// Invariant: Exactly one state at a time
// Cannot be Loading AND have Error
// Data exists only in Success state
```

_State is explicit. Invalid combinations impossible. Compiler enforces invariants._

### ❌ Bad: Boolean flags allow invalid states

```
STRUCTURE ComponentState:
    isLoading: boolean
    hasError: boolean
    errorMessage: string OR null
    data: Data OR null

FUNCTION render(state):
    IF state.isLoading AND state.hasError:
        // This shouldn't be possible - but it is!
        RETURN "???"

    IF state.data IS NOT null AND state.hasError:
        // Have data AND error? Which to show?
        RETURN "???"

// Invariants not enforced
// 16 possible combinations (2^4), most invalid
```

_Flags allow impossible states. No invariants enforced. Defensive checks everywhere._

## AI Review Checklist

Before accepting code, verify:

- [ ] What must always be true about this state?
- [ ] Where is that invariant enforced?
- [ ] Which transitions are allowed?
- [ ] Can invalid combinations occur?
- [ ] Are invariants documented?

**If invariants live only in human memory → REJECT (BLOCK)**

## Common Questions

**Q: What if I need temporary state during a transition?**  
A: Model the transition itself as a distinct state (e.g., `{ status: 'updating', oldData, newData }`).

**Q: How do I handle optional data?**  
A: Make optionality explicit: `{ status: 'loaded'; data: T | null }` or use separate states.

**Q: Can I have multiple simultaneous states?**  
A: Yes, but compose them clearly: `{ formState: FormState; networkState: NetworkState }`.

**Q: What about gradual migrations from bad state?**  
A: Wrap legacy state with adapters that enforce invariants at boundaries.

## Enforcement

- **Code review**: Challenge any boolean flag combinations
- **Type system**: Use discriminated unions to eliminate invalid states
- **Documentation**: Require explicit invariant statements
- **Testing**: Verify impossible states truly cannot be created

## Related Patterns

- **Functional Core, Imperative Shell**: Pure functions naturally preserve invariants
- **Single Direction Data Flow**: Unidirectional flow prevents inconsistent state
- **Naming as Design**: Names should reflect valid states, not implementation flags

## References

- [Making Impossible States Impossible - Richard Feldman](https://www.youtube.com/watch?v=IcgmSRJHu_8)
- [Parse, Don't Validate - Alexis King](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)
