/**
 * REFACTORED: Composition Over Coordination
 * 
 * Instead of one large coordinator, we compose small, focused units.
 * Each unit has a single responsibility and can be tested independently.
 */

// ============================================
// COMPOSABLE UNITS - Each does ONE thing
// ============================================

class AuthenticationResult {
    constructor(userId, email, isValid) {
        this.userId = userId;
        this.email = email;
        this.isValid = isValid;
    }

    static unauthorized() {
        return new AuthenticationResult(null, null, false);
    }
}

function authenticate(authService) {
    return async (token) => {
        const session = await authService.getSession(token);
        if (!session || !session.isValid) {
            return AuthenticationResult.unauthorized();
        }
        return new AuthenticationResult(session.userId, session.email, true);
    };
}

function validatePaymentRequest(request) {
    if (!request.amount || request.amount <= 0) {
        throw new Error("Invalid amount");
    }
    if (!request.currency || request.currency !== 'USD') {
        throw new Error("Only USD supported");
    }
    return request;
}

function checkRisk(db) {
    return async (userId) => {
        const riskScore = await db.query(
            "SELECT score FROM risk_profiles WHERE user_id = ?", 
            userId
        );
        if (riskScore > 80) {
            throw new Error("High risk transaction");
        }
        return riskScore;
    };
}

function chargeBank(bankApi) {
    return async (request, userId) => {
        const transaction = await bankApi.charge({
            card: request.cardNumber,
            amount: request.amount,
            ref: `TXN-${Date.now()}`
        });
        
        if (transaction.status !== 'success') {
            throw new Error(`Bank error: ${transaction.errorMessage}`);
        }
        
        return transaction;
    };
}

function recordTransaction(db) {
    return async (transaction, userId, amount) => {
        await db.execute(
            "UPDATE accounts SET balance = balance - ? WHERE user_id = ?", 
            [amount, userId]
        );
        await db.execute(
            "INSERT INTO transactions (id, user_id, amount) VALUES (?, ?, ?)", 
            [transaction.id, userId, amount]
        );
        return transaction;
    };
}

function sendNotification(emailService) {
    return async (email, amount) => {
        await emailService.send(
            email, 
            "Payment Successful", 
            `You charged $${amount}`
        );
    };
}

// ============================================
// COMPOSITION - Combine units into a pipeline
// ============================================

class PaymentProcessor {
    constructor(authService, db, bankApi, emailService) {
        // Create composed units
        this.authenticate = authenticate(authService);
        this.checkRisk = checkRisk(db);
        this.chargeBank = chargeBank(bankApi);
        this.recordTransaction = recordTransaction(db);
        this.sendNotification = sendNotification(emailService);
    }

    async processPayment(request) {
        // Pipeline: each step transforms or validates data
        const auth = await this.authenticate(request.token);
        if (!auth.isValid) {
            throw new Error("Unauthorized");
        }

        validatePaymentRequest(request);
        await this.checkRisk(auth.userId);
        
        const transaction = await this.chargeBank(request, auth.userId);
        await this.recordTransaction(transaction, auth.userId, request.amount);
        await this.sendNotification(auth.email, request.amount);

        return {
            success: true,
            transactionId: transaction.id
        };
    }
}

// ============================================
// BENEFITS OF THIS APPROACH
// ============================================

/**
 * ✅ Each unit is small (< 15 lines) and focused
 * ✅ Units are testable independently:
 *    - validatePaymentRequest(request) - pure function
 *    - authenticate(mockAuth)(token) - easy to mock
 * ✅ Reusable: checkRisk() can be used in other flows
 * ✅ Clear data flow: input → output for each unit
 * ✅ Easy to extend: add fraud detection unit without changing others
 * ✅ No deep coupling: units don't reach into each other
 */

// ============================================
// EXAMPLE TESTS - Simple because units are small
// ============================================

// Test individual units
function testValidation() {
    const valid = { amount: 100, currency: 'USD' };
    const result = validatePaymentRequest(valid);
    console.assert(result.amount === 100, "Validation should pass");
    
    try {
        validatePaymentRequest({ amount: 0, currency: 'USD' });
        console.assert(false, "Should throw for zero amount");
    } catch (e) {
        console.assert(e.message === "Invalid amount");
    }
}

// Test composition without real dependencies
async function testPaymentFlow() {
    const mockAuth = {
        getSession: async (token) => ({ userId: 123, email: 'user@test.com', isValid: true })
    };
    const mockDb = {
        query: async () => 50, // Low risk
        execute: async () => {}
    };
    const mockBank = {
        charge: async () => ({ id: 'TXN-001', status: 'success' })
    };
    const mockEmail = {
        send: async () => {}
    };

    const processor = new PaymentProcessor(mockAuth, mockDb, mockBank, mockEmail);
    const result = await processor.processPayment({
        token: 'abc',
        amount: 100,
        currency: 'USD',
        cardNumber: '4111'
    });

    console.assert(result.success === true);
    console.assert(result.transactionId === 'TXN-001');
}

// ============================================
// COMPARISON: Before vs After
// ============================================

/**
 * BEFORE (Coordination):
 * - 1 method, 60+ lines
 * - 4 dependencies mixed throughout
 * - Hard to test: must mock everything at once
 * - Hard to change: touching anything risks breaking everything
 * - Hard to reuse: logic trapped in coordinator
 * 
 * AFTER (Composition):
 * - 6 focused units, each < 15 lines
 * - Dependencies injected per unit
 * - Easy to test: mock one unit at a time
 * - Easy to change: swap units independently
 * - Easy to reuse: units work in other contexts
 * 
 * Main method went from orchestrating details to composing units.
 * Behavior emerges from structure, not procedural logic.
 */
