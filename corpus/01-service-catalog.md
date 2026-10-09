# Northstar Commerce - Service Catalog

All services, teams and incidents in this demo are fictional.

## Checkout Service
Checkout Service depends on Payments API.
Checkout Service depends on Inventory API.
Checkout Service is owned by Commerce Team.
Checkout Service handles purchase confirmation. Correlation IDs connect checkout requests to downstream payment traces. Checkout does not store card numbers.

## Payments API
Payments API depends on Ledger Database.
Payments API is owned by Payments Team.
Payments API uses a pooled database connection for authorization records. Connection acquisition waits can produce upstream timeout errors even when the database is reachable.

## Ledger Database
Ledger Database is owned by Platform Team.
Ledger Database stores payment authorization records. Database connection limits and slow queries should be checked during payment incidents.

## Inventory API
Inventory API is owned by Supply Team.
Inventory API depends on Stock Database.
Stock Database is owned by Supply Team.
Inventory is not involved in payment authorization. Confirm traces before attributing a checkout timeout to Inventory API.
