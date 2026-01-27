---
name: naming-as-design
description: Names must encode intent and constraints, not implementation. Use when reviewing vague or generic names.
---

# Naming As Design

## Principle

Names are design decisions made visible. Every name reveals what you understand about the problem domain, the role of each component, and the boundaries between concepts.

**Core insight:**
- Good names make the design obvious
- Bad names reveal confused thinking
- When you can't name something clearly, the design needs work

## When to Use

**Use this pattern when:**
- Reviewing any new code or APIs
- A function/variable is hard to name (signals design problem)
- Names include "Manager", "Handler", "Data", "Info", "Process"
- Names require explaining what they mean

**Indicators you need this:**
- Comments explaining what variables mean
- Generic names (data, item, value, result, temp)
- Names mixing abstraction levels (getUserFromDBAndFormat)
- Names that don't reveal intent (handle, process, do, manage)

## Instructions

### Name reveals purpose, not implementation

Names should tell you **what** and **why**, not **how**.

❌ **Avoid implementation details:**
- `arrayOfUsers` → data structure is obvious from usage
- `getUserFromDatabase` → storage mechanism is internal
- `parseJSONAndValidate` → combining unrelated concerns

✅ **Reveal intent and role:**
- `eligibleCandidates` → tells you the selection criteria
- `authenticatedUser` → tells you the authorization state
- `validatedOrder` → tells you the business state

### Name reveals constraints and invariants

Good names encode business rules and constraints.

**Examples of constraint-encoding names:**
- `NonEmptyString` vs `string` - makes null handling explicit
- `PositiveAmount` vs `number` - encodes valid range
- `AuthenticatedUser` vs `User` - encodes state requirement
- `UnvalidatedInput` vs `data` - signals trust boundary

### Name forces single responsibility

If you can't name something without "And", "Or", "Manager", it's doing too much.

❌ **Signals mixed responsibilities:**
- `validateAndSave` → two responsibilities
- `UserManager` → vague, does everything
- `handleRequest` → what aspect of requests?

✅ **Clear, focused names:**
- `validateOrder`, then `saveOrder` → separate concerns
- `UserAuthenticator`, `UserRepository` → specific roles
- `parseRequest`, `authorizeRequest` → distinct operations

### Domain language over programmer jargon

Use terms from the problem domain, not computer science abstractions.

❌ **Generic programmer terms:**
- `UserFactory` → pattern name, not domain concept
- `DataAccessLayer` → technical architecture term
- `RequestProcessor` → says nothing about business logic

✅ **Domain-specific language:**
- `RegistrationService` → what business process?
- `OrderRepository` → what domain objects?
- `PaymentValidator` → what business rules?

## Common Pitfalls

❌ **Avoid:**
- Suffixes that hide poor design: Handler, Manager, Processor, Helper, Utility
- Generic containers: data, info, result, response, object
- Technical jargon when domain terms exist
- Names longer than 4 words (signals confused design)
- Abbreviations that obscure meaning (usrMgr, procReq)

✅ **Do:**
- Use nouns for objects, verbs for functions
- Make illegal states unrepresentable in names
- Let the type system handle types (no `userArray`, just `users`)
- When stuck naming, question the design first
- Rename aggressively when understanding improves

## Examples

### ✅ Good: Names reveal intent

```
TYPE PositiveAmount = number // constrained type
TYPE ValidatedEmail = string // passed validation

FUNCTION calculateRefundAmount(order, returnedItems):
    // Name reveals purpose, not implementation
    
FUNCTION authenticateUser(credentials):
    // Returns authenticated user or error
    
FUNCTION eligibleForDiscount(customer, order):
    // Boolean reveals business rule

CONST MINIMUM_ORDER_VALUE = 50
CONST MAXIMUM_RETRY_ATTEMPTS = 3

// Names encode constraints and intent
// No comments needed
// Clear from reading alone
```

*Every name tells a story. Intent is obvious. Constraints explicit.*

### ❌ Bad: Names hide intent

```
FUNCTION process(data):
    // What is being processed? How?
    
FUNCTION handleUser(u):
    // Handle how? Create? Update? Delete?
    
FUNCTION doStuff(x, y):
    // Completely opaque
    
CONST VALUE = 50  // What does this limit?
CONST LIMIT = 3   // Limit of what?

VAR temp = getUserData()
VAR result = processData(temp)
VAR info = result.data

// Generic names everywhere
// Must read implementation to understand
// Intent buried in code
```

*Names reveal nothing. Must read implementation. Maintenance nightmare.*

## Naming Patterns

### Booleans and Predicates
- Prefix with `is`, `has`, `can`, `should`: `isValid`, `hasPermission`
- Use positive names: `isEnabled` not `isNotDisabled`
- Make the condition explicit: `isOverBudget` not `checkBudget`

### Collections
- Use plural nouns: `users`, `orders`, `transactions`
- Name reveals filtering: `activeUsers`, `paidInvoices`, `recentPosts`
- Name reveals relationship: `usersByEmail`, `ordersByDate`

### Functions
- Verbs for actions: `calculate`, `validate`, `transform`
- Reveal what changes: `createUser`, `deleteOrder`, `updateInventory`
- Query vs Command: `getUser` (query) vs `fetchUser` (command with effects)

### Constants
- ALL_CAPS for true constants: `MAX_RETRIES`, `DEFAULT_TIMEOUT`
- Reveal the constraint: `MINIMUM_PASSWORD_LENGTH` not `PASSWORD_LIMIT`

## AI Review Checklist

When reviewing code, verify naming decisions:

- [ ] Can you understand the code's purpose without comments?
- [ ] Do names reveal business domain, not implementation?
- [ ] Are generic terms (data, info, manager, handler) replaced with specific names?
- [ ] Do boolean names clearly state the condition being checked?
- [ ] Are constraints and invariants visible in type/variable names?
- [ ] Can you remove "And" from any function names by splitting?
- [ ] Do abbreviations obscure meaning? Can they be spelled out?

**If name requires a comment to explain → REJECT and ask for clearer name**

**If name uses "Manager", "Handler", "Helper" → WARN and suggest specific role**

**If function name includes "And" → SUGGEST splitting into multiple functions**

## Related Patterns

- **Explicit State Invariants**: Names should reveal state requirements
- **Single Responsibility**: If you can't name it simply, it does too much
- **Type-Driven Design**: Types and names work together to encode constraints
