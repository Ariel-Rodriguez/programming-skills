---
name: policy-mechanism-separation
description: Business rules must be separated from execution mechanisms. Use when reviewing code with hardcoded rules in loops or handlers.
---

# Policy Mechanism Separation

## Principle

Separate what to do (policy) from how to do it (mechanism):
- **Policy**: Business rules, decisions, configuration, strategies
- **Mechanism**: Reusable implementation, algorithms, infrastructure

Benefits:
- **Flexibility**: Change decisions without touching implementation
- **Reusability**: Same mechanism serves multiple policies
- **Clarity**: Business rules explicit and discoverable
- **Testing**: Test policies and mechanisms independently

## When to Use

**Use this pattern when:**
- Business rules are hardcoded in loops or handlers
- Same logic needs different behaviors in different contexts
- Rules change frequently but implementation is stable
- Configuration should be editable without code changes

**Indicators you need this:**
- Magic numbers or strings scattered in code
- Duplicated logic with slight variations
- if/else chains encoding business rules
- Code changes required for simple rule adjustments
- Similar functions differing only in thresholds or conditions

## Instructions

### Structure your code

1. **Identify policy vs mechanism**
   - Policy: "discard messages older than 30 days"
   - Mechanism: "filter array by date comparison"
   - Policy: "retry 3 times with exponential backoff"
   - Mechanism: "retry with configurable strategy"

2. **Extract mechanism as reusable function**
   - Accept policy parameters (thresholds, rules, strategies)
   - Implement general-purpose algorithm
   - Make no assumptions about specific use cases

3. **Define policy separately**
   - Configuration objects
   - Strategy functions
   - Rule definitions
   - Constants with meaningful names

4. **Connect policy to mechanism**
   - Pass policy as arguments
   - Use strategy pattern
   - Apply configuration at call site

### Common Pitfalls

❌ **Avoid:**
- Hardcoding business rules in loops
- Mixing rule definitions with execution logic
- Duplicating mechanisms to support different policies
- Making policy changes require code modifications

✅ **Do:**
- Pass rules as parameters
- Use configuration objects for policies
- Keep mechanisms generic and reusable
- Document what policies are available
- Name policy constants descriptively

## Examples

### ✅ Good: Policy separated from mechanism

```
// POLICY - Business rules
CONST DISCOUNT_RULES = [
    { minTotal: 100, discountPercent: 10 },
    { minTotal: 50, discountPercent: 5 }
]

CONST RETRY_POLICY = {
    maxAttempts: 3,
    backoffMs: 1000,
    shouldRetry: (error) => error.type === "NETWORK"
}

// MECHANISM - Reusable implementation
FUNCTION applyDiscountRules(order, rules):
    FOR EACH rule IN rules:
        IF order.total >= rule.minTotal:
            RETURN order.total * (1 - rule.discountPercent / 100)
    RETURN order.total

FUNCTION retryWithPolicy(operation, policy):
    FOR attempt FROM 1 TO policy.maxAttempts:
        result = operation()
        IF result IS Success OR NOT policy.shouldRetry(result.error):
            RETURN result
        WAIT policy.backoffMs * attempt
    RETURN result
```

*Rules defined separately. Mechanism is reusable. Easy to test independently.*

### ❌ Bad: Policy hardcoded in mechanism

```
FUNCTION applyDiscount(order):
    IF order.total > 100:  // Hardcoded policy
        RETURN order.total * 0.9  // Magic number
    ELSE IF order.total > 50:  // Hardcoded policy
        RETURN order.total * 0.95  // Magic number
    RETURN order.total

FUNCTION fetchWithRetry(url):
    FOR attempt FROM 1 TO 3:  // Hardcoded max
        result = fetch(url)
        IF result IS Success:
            RETURN result
        WAIT 1000 * attempt  // Hardcoded backoff
    RETURN result

// Policy buried in implementation
// Cannot reuse for different rules
// Changing rules requires code changes
```

*Business rules scattered in code. Cannot reuse. Must modify code to change policy.*

## Testing Strategy

**Test mechanism:**
```
TEST "executes correctly with policy A":
    // Arrange
    data = createTestData()
    policyA = createPolicyA()
    expectedA = createExpectedResultA()
    
    // Act
    result = mechanism(data, policyA)
    
    // Assert
    ASSERT result EQUALS expectedA

TEST "executes correctly with policy B":
    // Arrange
    data = createTestData()
    policyB = createPolicyB()
    expectedB = createExpectedResultB()
    
    // Act
    result = mechanism(data, policyB)
    
    // Assert
    ASSERT result EQUALS expectedB
```

**Test policy:**
```
TEST "policy defines correct rules":
    // Arrange
    retryPolicy = createRetryPolicy()
    
    // Act & Assert
    ASSERT retryPolicy.maxAttempts EQUALS 3
    ASSERT retryPolicy.backoffMs EQUALS 1000
```

## Enforcement

**Code review checklist:**
- [ ] Are business rules defined separately from implementation?
- [ ] Can rules change without modifying mechanism code?
- [ ] Is the mechanism reusable with different policies?
- [ ] Are policy parameters named descriptively?
- [ ] Could this logic serve other use cases with different rules?

**Red flags:**
- Magic numbers in loops or conditionals
- Similar functions differing only in constants
- Comments explaining "business rule: X"
- Frequent changes to core algorithms for rule tweaks

## Practical Patterns

### Configuration Object Pattern
```
// Policy
const validationRules = {
  minLength: 8,
  requireUppercase: true,
  requireNumbers: true
};

// Mechanism
function validate(input, rules) { /* ... */ }
```

### Strategy Pattern
```
// Policies
const strategies = {
  aggressive: (value) => value * 2,
  conservative: (value) => value * 0.5
};

// Mechanism
function apply(data, strategy) {
  return data.map(strategy);
}
```

### Rule Definition Pattern
```
// Policy
const discountRules = [
  { condition: (order) => order.total > 100, discount: 0.1 },
  { condition: (order) => order.items > 5, discount: 0.05 }
];

// Mechanism
function applyRules(data, rules) {
  return rules.find(r => r.condition(data));
}
```

## Related Patterns

- **Functional Core, Imperative Shell**: Policy in pure core, mechanism in shell
- **Single Direction Data Flow**: Policy flows through mechanism
- **Explicit State Invariants**: Policies enforce invariants via mechanisms

## Common Questions

**Q: When is separation overkill?**  
A: When the policy will never change and has only one use case. Don't abstract prematurely.

**Q: Should policies be in configuration files?**  
A: Depends on who changes them. Developer-controlled policies can live in code. Business-controlled policies should be in config/database.

**Q: How granular should policy separation be?**  
A: Separate when policies change independently. Keep together when they always change together.

**Q: What if the mechanism needs to know about the policy?**  
A: Pass policy as data, not behavior. The mechanism should work with any valid policy.

## References

- "Separating Policy from Mechanism" - Design principle from operating systems
- Strategy Pattern - Gang of Four Design Patterns
- Configuration Management - Clean Code practices
