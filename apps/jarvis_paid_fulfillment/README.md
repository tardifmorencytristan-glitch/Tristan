# Jarvis Paid Fulfillment R1

Public, secret-free deployment package for the existing **Audit Express 99 CAD** Stripe offer.

Flow:

Stripe Checkout -> signed webhook -> bounded public GitHub audit -> Redis receipt -> result page

R1 supports public github.com/owner/repo targets only. Unsupported input fails closed and never fabricates a report. It never mutates the customer repository.

Required environment variables:
- STRIPE_WEBHOOK_SECRET
- REDIS_URL

Start command:
uvicorn app:app --host 0.0.0.0 --port $PORT

Boundaries:
- Audit != Certification
- StaticPattern != Exploitability
- NoFlag != Safe
- PublicRead != MutationAuthority
