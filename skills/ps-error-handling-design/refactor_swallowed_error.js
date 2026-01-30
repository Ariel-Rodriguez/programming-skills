Refactor this code to follow Error Handling Design principles:

```javascript
function saveUser(user) {
  try {
    db.insert(user);
  } catch (e) {
    console.log('error saving user');
  }
}
```
