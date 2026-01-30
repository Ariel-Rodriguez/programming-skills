---
name: ps-functional-core-imperative-shell
description: Separate pure computation from side effects. Core business logic is pure functions, shell handles IO. Use when mixing calculations with database, HTTP, or file operations.
severity: BLOCK
---

# Functional Core, Imperative Shell

## Principle

Organize code into two layers:
- **Pure Core**: Deterministic computations with no side effects
- **Imperative Shell**: Coordinates effects (IO, state, external calls)

Benefits:
- **Testability**: Pure functions need no mocks
- **Reliability**: Same input → same output
- **Maintainability**: Business logic isolated from infrastructure

## When to Use

**Use this pattern when:**
- Business logic depends on external data
- Calculations should be deterministic
- Testing pure logic without infrastructure setup

**Indicators you need this:**
- Database calls mixed into validation
- HTTP requests inside calculation functions
- File IO scattered throughout business logic
- Unit tests requiring extensive mocking

## Instructions

### Structure your code

1. **Identify pure vs effectful operations**
   - Pure: calculations, transformations, validations
   - Effectful: database, HTTP, filesystem, logging, time

2. **Extract pure core**
   - Move business logic to pure functions
   - Accept all data as parameters
   - Return results, never perform effects

3. **Build imperative shell**
   - Load data from external sources
   - Call pure functions with loaded data
   - Save results back to external sources

### Common Pitfalls

❌ **Avoid:**
- Side effects in pure functions (logging, DB calls)
- Pure functions reading global state
- Business logic in shell layer
- Passing IO objects to core (connections, file handles)

✅ **Do:**
- Pass values, not connections
- Keep shell thin (just orchestration)
- Make effects explicit in function signatures
- Test core without infrastructure

## Examples

### ✅ Good: Pure core, effects in shell

```
// PURE CORE - No side effects
FUNCTION calculateOrderTotal(items, discountRules):
    subtotal = sum(items.map(item => item.price))
    discount = applyDiscountRules(subtotal, discountRules)
    RETURN subtotal - discount

FUNCTION applyDiscountRules(amount, rules):
    FOR EACH rule IN rules:
        IF rule.applies(amount):
            amount = amount * (1 - rule.percentage)
    RETURN amount

// IMPERATIVE SHELL - Coordinates effects
FUNCTION processOrder(orderId):
    items = database.getOrderItems(orderId)
    discountRules = database.getActiveDiscounts()
    
    total = calculateOrderTotal(items, discountRules)
    
    database.updateOrder(orderId, total)
    RETURN total
```

*Core is pure - testable without database. Shell coordinates IO.*

### ❌ Bad: Side effects mixed with logic

```
FUNCTION calculateOrderTotal(orderId):
    items = database.getOrderItems(orderId)  // Side effect!
    discountRules = database.getActiveDiscounts()  // Side effect!
    
    log("Calculating total for order " + orderId)  // Side effect!
    
    subtotal = sum(items.map(item => item.price))
    discount = 0
    FOR EACH rule IN discountRules:
        IF rule.applies(subtotal):
            discount = discount + (subtotal * rule.percentage)
    
    total = subtotal - discount
    database.updateOrder(orderId, total)  // Side effect!
    RETURN total
```

*Cannot test calculation without database. Cannot reuse logic. Hard to reason about.*

## Testing Strategy

**Pure Core:**
```
TEST "calculates correctly":
    // Arrange
    items = createTestItems()
    expectedValue = 150
    
    // Act
    result = calculateTotal(items)
    
    // Assert
    ASSERT result EQUALS expectedValue
```

**Imperative Shell:**
```
TEST "coordinates effects":
    // Arrange
    mockDB.save = mockFunction()
    orderId = "test-order-123"
    
    // Act
    processOrder(orderId)
    
    // Assert
    ASSERT mockDB.save WAS CALLED
```

## Enforcement

- **Code review**: Verify core functions have no side effects
- **Architecture tests**: Assert core modules don't import IO libraries
- **Linter rules**: Warn on console.log / global state in core


## Related Patterns

- **Explicit State Invariants**: Pure functions enforce invariants
- **Single Direction Data Flow**: Shell orchestrates unidirectional flow
- **Naming as Design**: Name layers clearly (core/ vs shell/)
