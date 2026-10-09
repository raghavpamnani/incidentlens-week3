# Identity Service - Access Runbook

## AUTH-401 diagnosis
AUTH-401 means an access token is expired or has an invalid issuer. Check token expiry, clock skew, audience and issuer. Never paste raw tokens into incident tickets.

## Ownership
Identity Service is owned by Security Team.
Security Team manages token verification configuration. Application token validation failures are separate from Payments API database connection errors.
