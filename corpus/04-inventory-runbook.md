# Inventory API - Stock Reservation Runbook

## INV-409 diagnosis
INV-409 indicates a stock reservation conflict. Confirm available stock in Stock Database and inspect reservation expiry. INV-409 is not PAY-504 and does not indicate Ledger Database pool exhaustion.

## Ownership and response
Supply Team owns Inventory API and Stock Database. Investigate reservation conflicts with Supply Team. Do not contact Payments Team for a confirmed stock-only conflict.
