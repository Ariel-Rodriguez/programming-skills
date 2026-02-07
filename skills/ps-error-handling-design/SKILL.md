---
name: ps-error-handling-design
description: Design systems with explicit error handling. Avoid throwing exceptions for domain errors. Use Result/Either types to make errors part of the function signature.
severity: WARN
---

# Principle

Treat error handling as a first-class design concern, not an afterthought:

- **Explicit errors**: Make failure modes visible in function signatures
- **Type-safe failures**: Use Result types, not exceptions for control flow
- **Intentional recovery**: Distinguish recoverable from non-recoverable errors
- **Strategic failure**: Choose between fail-fast and graceful degradation

Benefits:

- **Reliability**: Errors can't be accidentally ignored
- **Clarity**: Function signatures document failure modes
- **Safety**: Compiler enforces error handling
- **Debuggability**: Explicit error paths are easier to trace

## When to Use

**Use this pattern when:**

- Functions can fail in predictable ways
- Error handling affects business logic flow
- Silently ignoring errors would corrupt state
- Callers need to decide how to respond to failures

**Indicators you need this:**

- Try-catch blocks with empty handlers
- Errors logged but not acted upon
- Silent failure causing debugging nightmares
- Unclear which functions can throw/fail
- Mixing domain errors with infrastructure errors

## Instructions

### 1. Make Errors Explicit in Signatures

**Use Result/Either types instead of exceptions:**

- Return types encode both success and failure
- Compiler forces callers to handle both paths
- Errors become part of the type contract

**Distinguish error categories:**

- **Domain errors**: Expected business failures (validation, not found)
- **Infrastructure errors**: External system failures (network, DB)
- **Programming errors**: Bugs (null reference, type mismatch)

### 2. Recoverable vs Non-Recoverable

**Recoverable errors** (use Result types):

- Validation failures
- Not found / already exists
- Permission denied
- Rate limit exceeded
- Expected external service failures

**Non-recoverable errors** (crash immediately):

- Null pointer / undefined
- Programming logic errors
- Corrupted state
- Impossible conditions
- Configuration missing at startup

### 3. Fail Fast vs Graceful Degradation

**Fail fast when:**

- Early detection prevents worse failure later
- Corrupted state would spread
- Recovery is impossible or unsafe
- Developer error (should never happen in production)

**Degrade gracefully when:**

- Partial functionality is acceptable
- User experience benefits from fallback
- System can recover automatically
- Non-critical features

### Common Pitfalls

❌ **Avoid:**

- Catching exceptions just to log and rethrow
- Empty catch blocks (swallowing errors)
- Using exceptions for control flow
- Returning null/undefined to indicate failure
- Mixing error types (domain with infrastructure)
- Generic error messages ("Something went wrong")

✅ **Do:**

- Return Result types for expected failures
- Crash on programming errors
- Propagate errors to appropriate level
- Include context in error messages
- Handle errors at boundary (UI, API)
- Document failure modes in API contracts

## Examples

### ✅ Good: Explicit error in return type

```
FUNCTION findUser(userId):
    user = database.query(userId)
    IF user EXISTS:
        RETURN Success(user)
    ELSE:
        RETURN Error("UserNotFound", userId)

FUNCTION processRequest(userId):
    result = findUser(userId)
    IF result IS Success:
        RETURN response(result.value)
    ELSE IF result.error IS "UserNotFound":
        RETURN notFoundResponse(result.context)
```

_Errors are visible in the type. Caller must handle both paths. Cannot ignore failure._

### ❌ Bad: Hidden exceptions

```
FUNCTION findUser(userId):
    user = database.query(userId)
    IF user IS NULL:
        THROW Exception("User not found")
    RETURN user

FUNCTION processRequest(userId):
    TRY:
        user = findUser(userId)
        RETURN response(user)
    CATCH error:
        log(error)
        // Error swallowed, no recovery
```

_Exception is hidden. Easy to forget to catch. Error silently ignored._

## Error Handling Strategy

### At Different Layers

**Domain Layer:**

- Return Result types for business rule violations
- Never throw exceptions
- Pure functions that validate and transform

**Application Layer:**

- Coordinate operations
- Convert Results to appropriate responses
- Handle transaction boundaries

**Infrastructure Layer:**

- Wrap external failures in domain errors
- Retry transient failures
- Circuit breakers for external services

**Presentation Layer:**

- Convert errors to user-friendly messages
- Log technical details
- Provide recovery actions

### Testing Error Paths

**Test both happy and error paths:**

```
TEST "handles validation failure":
    // Arrange
    invalidData = createInvalidData()

    // Act
    result = validate(invalidData)

    // Assert
    ASSERT result.isError IS true
    ASSERT result.error.type EQUALS "VALIDATION_ERROR"

TEST "handles not found":
    // Arrange
    nonexistentId = "nonexistent"

    // Act
    result = findUser(nonexistentId)

    // Assert
    ASSERT result.isError IS true
    ASSERT result.error.type EQUALS "NOT_FOUND"
```

**Test error propagation:**

- Verify errors bubble correctly
- Check error context is preserved
- Ensure no information leakage

## AI Review Checklist

Before accepting code, verify:

- [ ] Are all failure modes explicit in function return types?
- [ ] Are errors categorized (domain vs infrastructure vs programming)?
- [ ] Is error handling appropriate for error type (Result vs crash)?
- [ ] Are errors handled at the right level (not too early, not too late)?
- [ ] Do error messages include actionable context?
- [ ] Are empty catch blocks or swallowed errors present?
- [ ] Does code distinguish recoverable from non-recoverable errors?
- [ ] Are null/undefined used to signal errors? (anti-pattern)

**If try-catch with no recovery → SUGGEST: Remove or propagate**
**If function returns null for errors → SUGGEST: Use Result type**
**If generic error message → SUGGEST: Add context (what, why, how to fix)**
**If domain error thrown → SUGGEST: Return Result instead**

## Common Questions

**Q: Should I use exceptions or Result types?**  
A: Use Result types for expected domain errors, exceptions only for non-recoverable programming errors. Result types make error handling explicit and type-safe.

**Q: When should I crash vs handle gracefully?**  
A: Crash on programming errors and corrupted state. Handle gracefully when partial functionality is acceptable and user experience benefits.

**Q: How detailed should error messages be?**  
A: Include what failed, why it failed, and how to fix it. Balance between helpful debugging and not exposing sensitive internals.

**Q: Should I log and throw?**  
A: No. Either handle the error or propagate it. Log at the boundary where it's handled. Logging and rethrowing creates duplicate logs.

**Q: What about validation errors?**  
A: Return a Result with structured validation errors. Let the caller decide how to present them. Don't throw exceptions for expected validation failures.

## Related Patterns

- **Functional Core, Imperative Shell**: Pure core returns Results, shell handles effects
- **Explicit State Invariants**: Failed validations prevent invalid state
- **Parse Don't Validate**: Transform input to types that can't represent invalid state

## References

- Railway Oriented Programming (Scott Wlaschin)
- Effective Error Handling (Joe Duffy)
- Domain-Driven Design error handling patterns
