/**
 * PaymentOrchestrator - A classic "God Object" or "Coordinator" that violates
 * the Composition Over Coordination principle.
 * 
 * It coordinates multiple subsystems (Auth, Validation, Bank, DB, Email)
 * inside a single large method, making it hard to test or reuse parts.
 */
class PaymentProcessor {
    constructor(authService, db, bankApi, emailService) {
        this.authService = authService;
        this.db = db;
        this.bankApi = bankApi;
        this.emailService = emailService;
    }

    async processPayment(request) {
        // 1. Authentication
        const session = await this.authService.getSession(request.token);
        if (!session || !session.isValid) {
            throw new Error("Unauthorized");
        }

        // 2. Validation
        if (!request.amount || request.amount <= 0) {
            throw new Error("Invalid amount");
        }
        if (!request.currency || request.currency !== 'USD') {
            throw new Error("Only USD supported");
        }

        // 3. Risk Check
        const riskScore = await this.db.query("SELECT score FROM risk_profiles WHERE user_id = ?", session.userId);
        if (riskScore > 80) {
            throw new Error("High risk transaction");
        }

        // 4. Bank Communication
        const transaction = await this.bankApi.charge({
            card: request.cardNumber,
            amount: request.amount,
            ref: `TXN-${Date.now()}`
        });

        if (transaction.status !== 'success') {
            await this.db.execute("INSERT INTO audit_logs (event, status) VALUES (?, ?)", ['payment_failed', transaction.errorMessage]);
            throw new Error(`Bank error: ${transaction.errorMessage}`);
        }

        // 5. Database Update
        await this.db.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", [request.amount, session.userId]);
        await this.db.execute("INSERT INTO transactions (id, user_id, amount) VALUES (?, ?, ?)", [transaction.id, session.userId, request.amount]);

        // 6. Notification
        await this.emailService.send(session.email, "Payment Successful", `You charged $${request.amount}`);

        return {
            success: true,
            transactionId: transaction.id
        };
    }
}
