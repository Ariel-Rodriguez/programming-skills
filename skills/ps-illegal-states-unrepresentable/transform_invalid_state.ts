Transform this type to make the state 'Success with Data' and 'Error with Message' mutually exclusive using a discriminated union:

    ```typescript
type Response = {
    status: 'success' | 'error';
    data?: any;
    errorMessage?: string;
}
```
