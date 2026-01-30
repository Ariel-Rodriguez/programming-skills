Refactor this function to be immutable.It should return a new object instead of mutating the input:

```javascript
function activateUser(user) {
    user.isActive = true;
    user.activatedAt = new Date();
    return user;
}
```
