---
name: ps-composition-over-coordination
description: Build complexity by composing simple units, not orchestrating flows. Use when reviewing large functions or god objects.
severity: SUGGEST
---

# Composition Over Coordination

## Principle

Build complex systems by combining simple, focused units that work together through interfaces, not through centralized coordinators that orchestrate every detail.

Benefits:
- **Modularity**: Each unit has one clear responsibility
- **Testability**: Small units test in isolation
- **Flexibility**: Swap or extend units without affecting others
- **Clarity**: Behavior emerges from structure, not hidden in coordinators

## When to Use

**Use this pattern when:**
- Functions exceed 50 lines by orchestrating multiple steps
- Classes have "Manager", "Coordinator", "Orchestrator" in names
- Adding features requires changing central control flow
- Objects know too much about others' internal details

**Indicators you need this:**
- God objects with 10+ methods
- Manager classes that just delegate
- Deep call chains: `a.getB().getC().doX()`
- Conditional logic routing to different subsystems
- Classes with many dependencies (5+ injected services)

## Instructions

### Prefer composition over orchestration

1. **Identify coordination logic**
   - Look for procedural flows in large methods
   - Find classes that "know" about many other classes
   - Spot conditional branching that routes to subsystems

2. **Extract composable units**
   - Each unit handles one transformation or decision
   - Units accept input, return output
   - No cross-unit dependencies

3. **Compose through interfaces**
   - Units connect via function calls or data flow
   - Outer layers combine units into pipelines
   - No central coordinator holding all logic

### Structure guidelines

✅ **Do:**
- Create small, focused functions/classes
- Compose behavior from simple units
- Let structure express the algorithm
- Pass data between units explicitly
- Build pipelines and chains

❌ **Avoid:**
- Centralized managers that know everything
- Methods that orchestrate 5+ operations
- Objects that reach into other objects' internals
- Conditional logic that routes to subsystems
- Classes named Manager/Coordinator/Orchestrator

## Examples

### ✅ Good: Small composable units

```
FUNCTION calculateDiscount(order):
    subtotal = order.items.sum(item => item.price)
    RETURN subtotal * 0.1

FUNCTION applyDiscount(order):
    discount = calculateDiscount(order)
    RETURN order.total - discount

FUNCTION processOrder(order):
    finalPrice = applyDiscount(order)
    RETURN createInvoice(order, finalPrice)
```

*Each function has one clear job. They compose naturally without coordination.*

### ❌ Bad: Central coordinator

```
CLASS OrderManager:
    FUNCTION processOrder(order):
        items = order.getItems()
        subtotal = 0
        FOR EACH item IN items:
            subtotal = subtotal + item.getPrice()
        
        IF order.hasDiscount():
            discount = subtotal * 0.1
            subtotal = subtotal - discount
        
        invoice = NEW Invoice()
        invoice.setOrder(order)
        invoice.setAmount(subtotal)
        this.invoiceRepository.save(invoice)
        
        RETURN invoice
```

*One large method coordinates everything. Hard to test, modify, or reuse parts.*

## Common Anti-Patterns

### God Objects
Classes that do too much. Split into focused units that compose.

### Manager/Coordinator Classes
Classes that only delegate. Push behavior into the units themselves.

### Deep Chains
`order.getCustomer().getAddress().getZipCode()` - violates Law of Demeter. Pass the data you need.

### Orchestration Methods
50+ line methods coordinating calls. Extract units and compose them.

## Enforcement

When reviewing code, check:

- [ ] Are functions under 30 lines?
- [ ] Do classes have single, clear responsibilities?
- [ ] Is coordination logic minimal (just composition)?
- [ ] Can units be tested independently?
- [ ] Would adding a feature require changing one unit, not a coordinator?

**If function > 50 lines coordinating steps → SUGGEST: Extract composable units**  
**If class name ends in Manager/Coordinator → WARN: Likely violates composition principle**  
**If class has 5+ dependencies → SUGGEST: Split into smaller composable units**

## Testing Strategy

**Small Units:**
```
TEST "unit transforms input correctly":
    // Arrange
    input = createTestInput()
    expected = createExpectedOutput()
    
    // Act
    result = transform(input)
    
    // Assert
    ASSERT result EQUALS expected
```

**Composed Systems:**
```
TEST "pipeline produces correct result":
    // Arrange
    pipeline = compose(unitA, unitB, unitC)
    input = createTestData()
    expected = createExpectedResult()
    
    // Act
    result = pipeline(input)
    
    // Assert
    ASSERT result EQUALS expected
```

Focus tests on individual units. Composed behavior emerges automatically if units are correct.

## Related Patterns

- **Single Responsibility Principle**: Each unit does one thing
- **Functional Core, Imperative Shell**: Compose pure functions, coordinate effects at edges
- **Naming as Design**: Names reveal composition structure
- **Explicit State Invariants**: Units enforce their own invariants
