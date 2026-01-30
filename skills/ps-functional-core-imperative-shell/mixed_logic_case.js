Refactor this code to follow Functional Core, Imperative Shell principles:

```javascript
function updateStock(productId, soldQuantity) {
    const product = db.query('SELECT * FROM products WHERE id = ?', productId);
    if (product.stock < soldQuantity) {
        throw new Error('Insufficient stock');
    }
    const newStock = product.stock - soldQuantity;
    db.execute('UPDATE products SET stock = ? WHERE id = ?', [newStock, productId]);
    return newStock;
}
```
