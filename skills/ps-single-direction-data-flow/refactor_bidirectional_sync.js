Refactor this manual synchronization to single - direction flow:

```javascript
function onUserUpdate(user) {
    this.user = user;
    this.header.syncUser(user);
    this.footer.syncUser(user);
}
```
