# INC-204 - Checkout Timeout Postmortem

## Timeline and symptoms
On 2026-09-18, fictional Northstar Commerce observed PAY-504 errors and checkout latency above 8 seconds. Payments API health checks stayed green while Ledger Database connection acquisition stalled. Inventory API latency was normal.

## Confirmed cause
Incident INC-204 was caused by a database connection leak in Payments API release 2.8.1. A missing connection release in the authorization retry path exhausted the 40-connection pool. This historical cause is not proof that a new incident has the same cause.

## Resolution and follow-up
An operator rolled Payments API back to release 2.8.0. Payments Team added a connection-release regression test; Platform Team added pool-wait alerting. The incident was closed after checkout success remained above 99% for ten minutes.

## Synthetic contact appendix
Demo contact: alex.morgan@example.test. Synthetic phone: +1-202-555-0147. Demo API key: sk-demo-ABCDEFGHIJKLMNOPQRSTUVWX. These deliberately fake values are included only to demonstrate redaction and must not be exposed in answers or evidence snippets.
