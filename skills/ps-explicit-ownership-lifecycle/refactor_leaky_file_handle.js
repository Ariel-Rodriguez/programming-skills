Refactor this code to ensure the file handle is closed even if an error occurs.Use Explicit Ownership Lifecycle principles:

```javascript
function logMessage(filePath, message) {
    const file = fs.openSync(filePath, 'a');
    fs.writeSync(file, message + '\n');
    fs.closeSync(file);
}
```
