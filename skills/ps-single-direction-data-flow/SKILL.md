---
name: ps-single-direction-data-flow
description: Enforces unidirectional data flow with clear ownership. Use when reviewing data flows, debugging race conditions, or designing state management. Prevents ghost updates and synchronization bugs.
severity: BLOCK
---

# Single Direction of Data Flow

## Principle

Data flows one way. No backchannels. No hidden feedback loops. No circular dependencies.

This is about **reasoning locality**: you should be able to trace data flow linearly without jumping through multiple files.

Benefits:

- **Predictability**: Updates follow a single path
- **Debuggability**: No hidden state mutations
- **Maintainability**: Clear ownership boundaries

## When to Use

**Use this pattern when:**

- Designing state management architecture
- Reviewing components that share state
- Debugging "why did this re-render?" issues
- Setting up reactive systems or event streams

**Indicators you need this:**

- Race conditions from multiple writers
- Difficulty tracing where data changes
- Components falling out of sync
- Bidirectional bindings creating update loops

## Instructions

### One Source of Truth

Each piece of data has exactly one owner:

- Owner is the sole writer
- Other code reads from the owner
- Updates propagate from the owner downward

### Clear Ownership

For every piece of state, know:

- **Who owns this data?** (Which component/module)
- **Who may change it?** (Only the owner)
- **How do others get changes?** (Subscriptions, props, parameters)

### Updates Flow Down, Events Flow Up

Establish clear communication paths:

- **Parent owns state**: Single source of truth
- **Children receive state**: Via props/parameters
- **Children send events up**: Actions, callbacks, events
- **Parent decides**: How to respond to events

### Common Pitfalls

❌ **Avoid:**

- Multiple components writing to shared state
- Children mutating parent state directly
- Circular data dependencies
- Backchannel updates through side effects

✅ **Do:**

- Single owner per state value
- Explicit update paths
- Events for upward communication
- Derived data, not duplicate state

## Examples

### ✅ Good: Unidirectional flow

```
// PARENT - owns state
COMPONENT ShoppingCart:
    STATE items = []

    FUNCTION addItem(item):
        this.items = [...this.items, item]

    FUNCTION render():
        RETURN CartView(
            items: this.items,
            onAddItem: this.addItem
        )

// CHILD - receives state, emits events
COMPONENT CartView(items, onAddItem):
    FUNCTION render():
        DISPLAY items
        BUTTON "Add Item" ONCLICK:
            onAddItem(newItem)  // Event up

// Data flows down: parent -> child
// Events flow up: child -> parent
// Single source of truth: parent owns items
```

_Clear ownership. Data flows one way. Easy to trace updates._

### ❌ Bad: Bidirectional updates

```
GLOBAL sharedCart = { items: [] }

COMPONENT CartView:
    FUNCTION addItem(item):
        sharedCart.items.push(item)  // Direct mutation
        notifyOtherComponents()  // Manual sync

    FUNCTION render():
        DISPLAY sharedCart.items

COMPONENT CartSummary:
    FUNCTION removeItem(itemId):
        sharedCart.items = sharedCart.items.filter(...)
        updateCartView()  // Backchannel update

    FUNCTION render():
        DISPLAY sharedCart.items.length

// Multiple writers to shared state
// Hidden dependencies
// Race conditions possible
// Synchronization nightmare
```

_Shared mutable state. Multiple writers. Updates flow in all directions. Debugging nightmare._

## AI Review Checklist

Before accepting code, verify:

- [ ] Who owns this data?
- [ ] Who is allowed to change it?
- [ ] Can I trace the update path linearly without jumping files?
- [ ] Are there any backchannel updates?
- [ ] Do any dependencies form a cycle?

**If tracing requires global search → Architecture violation (BLOCK)**

## Enforcement

- **Code review**: Verify single ownership per state
- **Architecture tests**: Detect circular dependencies
- **Debugging**: Trace data flow without IDE search

## Common Questions

**Q: What about two-way data binding (like Vue v-model)?**  
A: It's syntactic sugar. Under the hood, it's still unidirectional (value down, event up).

**Q: Can siblings share state?**  
A: Not directly. Lift state to common parent. Parent owns, siblings read.

**Q: What about caching/derived data?**  
A: Derive from source of truth. Don't store redundant state.

**Q: How do I handle circular dependencies in legacy code?**  
A: Refactor to extract shared logic to a parent module. Break the cycle.

## Related Patterns

- **Functional Core, Imperative Shell**: Pure core benefits from single-direction flow
- **Explicit State Invariants**: Unidirectional updates make invariants easier to enforce
- **Naming as Design**: Clear ownership reflected in naming

## References

- [Flux Architecture - Facebook](https://facebook.github.io/flux/docs/in-depth-overview/)
- [Redux - Dan Abramov](https://redux.js.org/understanding/thinking-in-redux/motivation)
- [Unidirectional Data Flow - André Staltz](https://staltz.com/unidirectional-user-interface-architectures.html)
