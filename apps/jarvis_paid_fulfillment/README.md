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


## R149 bounded durable intake ? deployment remains gated

The existing FastAPI service now persists a **signed, paid, supported Checkout
Session** to SQLite in a single transaction before returning 200. The handler
does **not** perform the GitHub review during the webhook request. Duplicate
Stripe events for the same session reuse the original job; a conflicting
payload returns 409 instead of replacing the order. Unsupported or unpaid
sessions are not fulfilled.

An existing authorized Jarvis/PC runner may use `python worker.py --max-jobs 1`
for a **bounded one-shot drain**. `python worker.py --check` only reads boolean
configuration. The script does not register a scheduler, publish to a customer,
charge a card, issue a refund, or create a Stripe event destination.

State machine: `QUEUED ? PROCESSING ? READY`, with `RETRY` (network faults,
exponential bounded backoff), `HOLD` (invalid target, permanent error,
exhausted retries), and a lease on `PROCESSING`. An expired lease can be
reclaimed after a worker crash. Each claim has a random fencing token; a
late/stale worker cannot overwrite a new claim. The queue stores only the
canonical public repository URL and required bounded audit inputs, **not**
the customer's email address. It does not auto-replay legacy R1/R148
`PROCESSING` records; these require manual reconciliation to avoid duplication.

**READY means a generated report, not proof of independent delivery.**
Customer results are not publicly indexable and are not cached, but knowledge
of a Checkout session identifier may grant access. Treat these URLs as bearer
links and do not publish or log them. Stronger customer authorization is still
required before broader commercial rollout.

**Critical residuals (OAK-blocking):**

- A non-temporary SQLite pathname does not prove persistent storage. Test disk
  durability, restart, replica behavior, backups, recovery, and failover;
  ephemeral Render filesystems are not an acceptable commercial store.
- No live Stripe webhook destination or secret has been validated. Configure
  one only for the explicitly authorized public HTTPS service, with least-
  privilege secrets and the two Checkout success events.
- A real Jarvis owner must invoke `worker.py`; no daemon or new scheduler
  is installed. Never claim autonomous processing from a config flag alone.
- Validate a sandbox payment ? signed event ? durable queue ? local worker ?
  report ? authenticated customer receipt, including crash/replay/duplicate
  checks and external delivery acknowledgement.
- Review tax registrations, product tax codes, refund paths, privacy/retention,
  invoices, subscriptions, dispute handling, security and policy requirements.
- Promotion requires independent OAK and Jarvis committee receipts, exact-head
  comparison, authorization, rollback, and production readback. Do not use
  GitHub Actions or GitHub CI for tests.

To roll back application behavior: redeploy the last verified artifact after
reviewing already queued orders. Do **not** drop or delete the queue or its
database on rollback; isolate and reconcile outstanding paid orders first.
