Refactor this function to improve Local Reasoning by eliminating global state access:

```javascript
function getFinalPrice(order) {
    const taxRate = window.APP_CONFIG.taxRate; // Global access
    return order.total * (1 + taxRate);
}
```
