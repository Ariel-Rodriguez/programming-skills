Refactor this code to follow Explicit Boundaries & Adapters(Hexagonal Architecture).Move the database logic to an adapter:

```javascript
function enrollStudent(studentId, courseId) {
    const student = db.query('SELECT * FROM students WHERE id = ?', studentId);
    if (student.eligible) {
        db.execute('INSERT INTO enrollments ...');
    }
}
```
