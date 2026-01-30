Refactor this state object to use a discriminated union to prevent invalid combinations:

```javascript
const state = {
    isLoading: false,
    isError: true,
    data: null,
    error: 'Network timeout'
};
```
