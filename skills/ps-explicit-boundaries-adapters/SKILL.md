---
name: ps-explicit-boundaries-adapters
description: Isolates frameworks and external systems behind adapters. Use when reviewing code with tight framework coupling or direct API calls in business logic.
severity: WARN
---

# Explicit Boundaries Adapters

## Principle

Isolate external systems and frameworks behind explicit boundaries using adapters and ports:

- **Core Domain**: Business logic with no external dependencies
- **Ports**: Interfaces defining what the core needs
- **Adapters**: Implementations that connect to external systems

Benefits:

- **Testability**: Core logic tests without real infrastructure
- **Flexibility**: Swap implementations without changing core
- **Maintainability**: Changes to external systems don't ripple through domain logic

This is also known as Hexagonal Architecture or Ports & Adapters pattern.

## When to Use

**Use this pattern when:**

- Business logic directly imports framework code
- Core domain depends on database libraries
- External API clients used throughout the codebase
- Tests require complex infrastructure setup

**Indicators you need this:**

- Framework imports in business logic files
- Database client passed to domain functions
- HTTP client dependencies in core modules
- Difficult to test without running external services
- Cannot change infrastructure without touching domain code

## Instructions

### Define clear boundaries

1. **Identify external dependencies**
   - Databases (PostgreSQL, MongoDB, Redis)
   - External APIs (payment processors, email services)
   - Frameworks (Express, Django, Spring)
   - Infrastructure (file systems, message queues)

2. **Create port interfaces**
   - Define what operations the core needs
   - Use domain language, not technical details
   - Keep interfaces small and focused
   - Return domain objects, not DTOs or ORM models

3. **Implement adapters**
   - One adapter per external system
   - Translate between domain and external formats
   - Handle all technical concerns (connections, retries, serialization)
   - Keep adapters thin - no business logic

4. **Wire at composition root**
   - Inject adapters into core at application startup
   - Core never imports adapter implementations
   - Configuration determines which adapter to use

### Core Rules

✅ **Must:**

- Define ports as interfaces in core domain
- Implement adapters outside core domain
- Core depends only on port interfaces
- Adapters depend on ports and external libraries
- Pass domain objects through ports, not external types

❌ **Must not:**

- Import framework code in domain logic
- Pass database connections to core functions
- Return ORM models or HTTP response objects from core
- Put business logic in adapters
- Have core depend on adapter implementations

## Examples

### ✅ Good: Core depends on port interface

```
// Port (defined in domain)
INTERFACE UserRepository:
    METHOD save(user)
    METHOD findById(userId) RETURNS User OR Error

// Core domain logic
FUNCTION registerUser(userData, repository):
    user = createUser(userData)
    result = repository.save(user)
    IF result IS Error:
        RETURN Error("RegistrationFailed", result)
    RETURN Success(user)

// Adapter (separate module)
CLASS PostgresUserRepository IMPLEMENTS UserRepository:
    METHOD save(user):
        sql = "INSERT INTO users VALUES (...)"
        EXECUTE sql WITH user.data

    METHOD findById(userId):
        sql = "SELECT * FROM users WHERE id = ?"
        RETURN queryDatabase(sql, userId)
```

_Domain depends on interface. Adapter implements interface. Core has no database imports._

### ❌ Bad: Core depends on concrete infrastructure

```
IMPORT { PostgresClient } from "database-library"

FUNCTION registerUser(userData, dbClient):
    user = createUser(userData)
    TRY:
        dbClient.query("INSERT INTO users VALUES ...", user)
    CATCH error:
        RETURN Error("RegistrationFailed")
    RETURN user
```

_Domain tightly coupled to PostgreSQL. Cannot test without real database. Hard to switch databases._

## Testing Strategy

**Core Domain (with ports):**

```
TEST "business rule enforced":
    // Arrange
    mockRepo = {
        save: mockFunction(),
        findById: mockFunction()
    }
    order = createTestOrder()

    // Act
    result = processOrder(order, mockRepo)

    // Assert
    ASSERT result.isValid IS true
```

**Adapters (integration tests):**

```
TEST "persists domain objects":
    // Arrange
    db = setupTestDatabase()
    domainObject = createTestObject()

    // Act
    adapter.save(domainObject)
    retrieved = adapter.findById(domainObject.id)

    // Assert
    ASSERT retrieved EQUALS domainObject
```

## Common Patterns

### Repository Pattern

Port defines `save()`, `find()`, `delete()` operations. Adapters implement for specific databases. Core never knows if it's PostgreSQL or MongoDB.

### Gateway Pattern

Port defines external service operations in domain terms. Adapters handle HTTP, authentication, data mapping. Core thinks in domain concepts.

### Notification Pattern

Port defines `notify(user, message)`. Adapters implement via email, SMS, push notifications. Core doesn't care about delivery mechanism.

### File Storage Pattern

Port defines `store(file)`, `retrieve(id)`. Adapters implement for local filesystem, S3, Azure Blob. Core logic unchanged when storage moves to cloud.

## Language-Specific Patterns

### JavaScript/TypeScript

- Use TypeScript interfaces for ports
- Dependency injection via constructor parameters
- Factory functions at composition root
- Avoid importing concrete implementations in domain files

### Python

- Use ABC (Abstract Base Class) for ports
- Type hints with Protocol for structural typing
- Dependency injection via constructor or function parameters
- Keep domain in separate package from adapters

### Java/C#

- Use interfaces for ports
- Dependency injection frameworks (Spring, .NET Core)
- Package structure: `domain/` `ports/` `adapters/`
- Avoid `new` keyword in domain code

### Go

- Use interfaces for ports (idiomatic Go)
- Small, focused interfaces
- Accept interfaces, return structs
- Composition root in `main()` or initialization code

## AI Review Checklist

Before accepting code, verify:

- [ ] Are external dependencies (DB, HTTP, frameworks) imported in business logic?
- [ ] Are port interfaces defined in domain language?
- [ ] Do adapters translate between domain and external formats?
- [ ] Can core logic be tested without real infrastructure?
- [ ] Is dependency direction correct (adapters depend on ports, not vice versa)?
- [ ] Are domain objects used across boundaries, not external types?

**If domain imports framework code → SUGGEST extracting port interface (WARN)**

**If adapter contains business logic → SUGGEST moving to domain (WARN)**

**If port returns external types (ORM models, DTOs) → SUGGEST using domain objects (SUGGEST)**

**If tests require real database for domain logic → SUGGEST using port test doubles (SUGGEST)**

## Common Questions

**Q: Isn't this over-engineering for simple applications?**  
A: For trivial CRUD apps, yes. But if you have business rules, validation, or complex workflows, explicit boundaries pay off quickly. Start simple, add boundaries when coupling becomes painful.

**Q: How many ports should I create?**  
A: Start with one port per external system type. Split when a port grows beyond 5-7 methods or when different parts of the system need different subsets of operations.

**Q: Should every database table have an adapter?**  
A: No. Group related data access into repositories by aggregate root or bounded context. One adapter might handle multiple tables that form a cohesive unit.

**Q: What about frameworks that expect you to extend their classes?**  
A: Create a thin adapter layer that extends framework classes and delegates to your domain. Keep framework coupling isolated to adapter layer.

**Q: How do I handle transactions across adapters?**  
A: Define a transaction port in domain. Adapters implement transaction management. Core orchestrates but doesn't manage transactions directly.

## References

- Alistair Cockburn: "Hexagonal Architecture" (original pattern)
- Robert C. Martin: "Clean Architecture" (dependency rule)
- Vaughn Vernon: "Implementing Domain-Driven Design" (Chapter 4: Architecture)
- Martin Fowler: "Patterns of Enterprise Application Architecture" (Repository, Gateway patterns)
