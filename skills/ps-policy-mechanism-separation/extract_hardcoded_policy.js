Refactor this code to separate policy from mechanism:

```javascript
function filterExpiredItems(items) {
    return items.filter(item => {
        const age = Date.now() - item.createdAt;
        return age < 30 * 24 * 60 * 60 * 1000; // 30 days
    });
}
```
