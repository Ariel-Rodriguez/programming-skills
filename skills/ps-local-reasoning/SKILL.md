---
name: ps-local-reasoning
description: Ensures code is understandable locally without global context. Use when reviewing code with hidden dependencies or global state.
severity: WARN
---

# Local Reasoning

## Principle

Code should be understandable by reading it in isolation, without jumping to other files or searching for hidden dependencies.

Benefits:

- **Readability**: Understanding requires minimal context switching
- **Maintainability**: Changes are predictable and safe
- **Debugging**: Problem source is immediately visible
- **Onboarding**: New developers can understand code faster

## When to Use

**Use this skill when:**

- Writing functions that depend on external data
- Reviewing code with unclear data sources
- Refactoring code with scattered dependencies
- Debugging issues caused by hidden state

**Indicators you need this:**

- Must trace through multiple files to understand a function
- Function behavior changes based on global state
- Dependencies are implicit (imported modules, globals)
- "Magic" values appear from nowhere
- Function signatures don't reveal what's needed

## Instructions

### Make Dependencies Explicit

1. **Pass dependencies as parameters**
   - All data should be received as function arguments
   - No hidden globals, singletons, or module-level state
   - Function signature shows exactly what it needs

2. **Avoid implicit dependencies**
   - Don't access config objects directly
   - Don't use ambient values (process.env directly in logic)
   - Don't reference parent scope variables unnecessarily

3. **Minimize global state**
   - Reduce module-level mutable state
   - Prefer dependency injection over imports
   - Make state flow visible

### Structure for Clarity

1. **Declare dependencies at function boundaries**
   - All inputs as parameters
   - All outputs as return values
   - Side effects explicit in name or signature

2. **Keep related code together**
   - Helper functions near their usage
   - Constants near where they're used
   - Avoid forcing readers to jump files

3. **Make data flow visible**
   - Clear transformation pipeline
   - Explicit passing of data
   - No hidden mutation of shared state

### Common Pitfalls

❌ **Avoid:**

- Reading from global state inside functions
- Importing config deep in logic
- Hidden dependencies through closures
- Module-level side effects
- Accessing outer scope unnecessarily

✅ **Do:**

- Pass everything the function needs as parameters
- Make external dependencies obvious
- Keep function scope self-contained
- Document non-obvious dependencies
- Use types/interfaces to declare requirements

## Examples

### ✅ Good: All dependencies explicit

```
FUNCTION calculateDiscount(order, pricingRules, customerTier):
    basePrice = order.items.sum(item => item.price)

    tierMultiplier = pricingRules.getTierMultiplier(customerTier)
    discount = basePrice * tierMultiplier

    RETURN basePrice - discount

// Everything needed is in parameters
// Can understand without looking elsewhere
// Easy to test - just pass values
```

_Function signature reveals all dependencies. Fully understandable in isolation._

### ❌ Bad: Hidden dependencies

```
IMPORT { config } from "config"
IMPORT { pricingService } from "services"

FUNCTION calculateDiscount(order):
    basePrice = order.items.sum(item => item.price)

    customerTier = getCurrentUser().tier  // Where does this come from?
    tierMultiplier = pricingService.getTier(customerTier)  // Global import
    discount = basePrice * tierMultiplier * config.discountFactor  // Global config

    RETURN basePrice - discount

// Must read 3+ other files to understand
// getCurrentUser() - from where?
// pricingService - how is it configured?
// config - what value is this?
```

_Cannot understand without hunting through imports. Hidden dependencies make testing hard._

## Review Checklist

Before accepting code, verify:

- [ ] Can I understand this function without looking at other files?
- [ ] Are all data sources visible in the function signature?
- [ ] Is any global or module state being accessed?
- [ ] Could this function work in isolation with the right inputs?
- [ ] Are dependencies injected rather than imported inside?

**If function accesses globals → Refactor to accept as parameters (WARN)**  
**If dependencies are hidden → Make explicit in signature (SUGGEST)**  
**If behavior depends on external state → Pass state as argument (WARN)**

## Practical Patterns

### Dependency Injection

Instead of importing dependencies directly, accept them as parameters:

- Pass configuration objects as arguments
- Inject services rather than importing singletons
- Accept callbacks for side effects

### Pure Function Default

Make functions pure by default:

- All inputs via parameters
- All outputs via return value
- No side effects unless absolutely necessary

### Explicit Context

When context is needed, pass it explicitly:

- Request/response objects as parameters
- User context as explicit argument
- Transaction context passed down

### Colocation

Keep related code together:

- Helper functions near usage
- Type definitions with implementations
- Validation with data structures

## Language-Specific Patterns

### JavaScript/TypeScript

- Use function parameters over closure scope
- Prefer dependency injection over module imports
- Avoid ambient global access (process.env directly)
- Use TypeScript interfaces to make dependencies explicit

### Python

- Use function arguments instead of module-level variables
- Avoid mutable module state
- Pass config objects explicitly
- Use type hints to document dependencies

### Others

- Java: Constructor injection over field access
- C#: Dependency injection containers
- Go: Explicit context passing
- Rust: Ownership makes dependencies explicit

## Common Questions

**Q: Doesn't this make function signatures too long?**  
A: If a signature is too long, it's often a sign the function does too much. Consider breaking it into smaller functions or grouping related parameters into a context object.

**Q: What about configuration that everything needs?**  
A: Pass config objects at high levels and extract only what's needed for lower levels. Avoid accessing a global config object deep in business logic.

**Q: Isn't dependency injection overkill for small projects?**  
A: Start simple with explicit parameters. The principle is making dependencies visible, not requiring a DI framework.

**Q: How do I handle ambient context like user authentication?**  
A: Pass user/session context explicitly through the call chain, or use a request context object. Don't rely on thread-local or global state.

## Related Patterns

- **Functional Core, Imperative Shell**: Pure core has explicit dependencies
- **Explicit State Invariants**: Local reasoning enables easier invariant verification
- **Single Direction Data Flow**: Explicit data flow supports local reasoning
