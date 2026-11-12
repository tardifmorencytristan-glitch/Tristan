# Jarvis Paid Fulfillment R1

Public, secret-free deployment package for the bounded **Jarvis Repo QuickCheck** and **Audit Express 99 CAD** Stripe offers.

Flow:

Stripe payment fact -> verified bounded public GitHub review -> receipt -> delivery only after an external delivery receipt

R1 supports public github.com/owner/repo targets only. Unsupported input fails closed and never fabricates a report. It never mutates the customer repository.

Required environment variables for an enabled webhook worker:
- STRIPE_WEBHOOK_SECRET (a secret, never commit it)
- JARVIS_RESULT_DB (explicit, non-temporary SQLite path on storage with separately verified persistence)
- JARVIS_AUTOFULFILLMENT_ENABLED=true (only after the event destination, storage, and delivery gates have been independently tested)

`/health` is liveness only. `/ready` checks LOCAL CONFIGURATION, not whether Stripe
actually sends events, whether the database survives restarts, or whether a
customer received a report. When a signed paid-order webhook arrives with the
worker disabled or the DB path missing/temporary, the handler returns HTTP 503
rather than falsely acknowledging an unfulfillable order. Stripe retries.
No external webhook destination or tax registration is created by this code.

Start command:
uvicorn app:app --host 0.0.0.0 --port $PORT

Boundaries:
- Audit != Certification
- StaticPattern != Exploitability
- NoFlag != Safe
- PublicRead != MutationAuthority

R1.1 storage note: SQLite is ephemeral on free Render instances; deploy/restart may require Stripe event replay. This is explicit residual debt, not durable-storage proof.

R1.2 intake note: project is required; problem/scope may be omitted and compile to conservative public-GitHub read-only defaults. OptionalInput != BroaderAuthority.
