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


## R150: report access is independently authorized (fail-closed)

The original `/result?session_id=...` and `/receipt/{session_id}` endpoints
were insufficiently protected because a Checkout session identifier alone was
a bearer credential. In R150, **both routes require a separate short-lived
HMAC capability token sent in the HTTP `Authorization: Bearer ...` header**.
The token is cryptographically bound to exactly one Checkout session and expires
after at most 900 seconds. Missing, expired, forged, wrong-session, query-only,
or incorrectly signed tokens are rejected **before database lookup**. Receipt
responses remain `private, no-store`, `noindex`, and `no-referrer`.
The webhook signing secret is not accepted as a report-access secret.

Configuration (no secrets committed):
- `JARVIS_RESULT_ACCESS_SECRET`: independent, high-entropy key with at least
  32 UTF-8 bytes, stored in a platform vault or restricted secret settings.
- Rotate report-access secrets when access must be revoked globally. Individual
  token revocation is not implemented.
- TLS and appropriate logging redaction must be enforced by the HTTPS host.

The `result_access.issue_result_access_token(...)` function **does not identify
a customer**. An already-authenticated customer delivery owner must establish
the legitimate recipient by independent server-side checks before issuing a
token. This repository deliberately exposes **no public token-minting API**,
does not email tokens or give them out on the Checkout success page, and does
not put tokens in URLs. Do not build automated delivery by copying this helper
into unauthenticated browser code.

The customer-facing delivery flow is **blocked** until an authorized account,
customer portal, or similarly verified delivery channel exists and has been
end-to-end tested. An otherwise green `/ready` checks only inbound intake
configuration; it does not imply private report delivery is configured.

**Security claims limited to:** isolated tests of signed capability verification
and rejection of unauthenticated report reads. This does not verify the host,
customer identity, backups, revocation, or real production delivery.

## R151: account catalog reconciliation and evidence completeness

`catalog_audit.py` is a **read-only, standard-library, offline reconciler**:
it consumes private, pre-sanitized Stripe product/price/payment-link snapshots
and checked payment-link line items. It makes **no authenticated Stripe API
calls itself** and never changes products, prices, billing, customer data, links,
tax registrations, payment methods, or webhook settings. Its `--report` output
is redacted by design (aggregate counts and codes only). Private source
snapshots must stay outside public repositories; no customer data is ingested.

The Stripe list endpoints may report `has_more=false` even when direct
`GET /prices/{id}` / `GET /products/{id}` and search confirm additional linked
resources. R151 therefore distinguishes *listed* from *identified-at-least*
counts, and will **never** assert complete catalog coverage from a single list.

Run locally, with an already-authorized private snapshot:

```powershell
python apps/jarvis_paid_fulfillment/catalog_audit.py --snapshot PRIVATE.json --report REDACTED.json
python apps/jarvis_paid_fulfillment/catalog_audit.py --snapshot PRIVATE.json --report GATE.json --gate
```

The optional `--gate` returns exit code 2 if promotion remains blocked. A
successful audit run is **not** a commercial/go-live PASS. The reconciler
detects incomplete references, product/price mismatches, active links pointing
to HOLD products, missing webhook destinations, tax configuration review,
active offers without default prices or links, and unsupported claims of
exhaustiveness. Missing default prices and no active links are potential
business choices, not proof of errors.

A catalog fix that can affect customer charges, tax, links or existing
subscriptions must be evaluated separately against real obligations, affected
customers, explicit authority, independent Jarvis committee reviews, OAK and
rollback before any Stripe mutation. NO_ACTION is a valid decision.
