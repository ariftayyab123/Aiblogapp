# Public Repository Security Checklist

Use this checklist before publishing a release, accepting outside contributions, or sharing a repository archive.

## Before publication

- Confirm `.env` and environment-specific variants are ignored and absent from `git ls-files`.
- Keep only sanitized `.env.example` files with unmistakable placeholder values.
- Search the tracked tree for API keys, access tokens, private keys, passwords, connection strings, internal hosts, customer identifiers, and developer-specific paths.
- Keep LLM credentials in backend environment variables or the deployment platform's secret store. Never expose them through a `VITE_` variable.
- Review deployment manifests for `sync: false`, generated secrets, or equivalent secret references rather than literal values.
- Confirm screenshots contain no personal data, tokens, internal URLs, or customer content.
- Review generated documentation and examples for copied production data.

## Product-specific checks

- Treat generated citations as unverified model output until a person validates them.
- Remember that every completed post is currently readable through its public slug endpoint; do not generate or store confidential content.
- Treat the encrypted-looking blog ID in frontend URLs as obfuscation only. Backend ownership checks are the authorization boundary.
- Confirm both the web service and Celery worker use the same selected `LLM_PROVIDER` and corresponding secret key.
- Verify `/health/live` and `/health/ready` after deployment.

## Credential exposure response

If a real secret was ever committed:

1. Revoke or rotate it with the external provider first.
2. Replace it with a deployment secret reference and a safe example placeholder.
3. Assess Git history, release archives, CI logs, and forks for exposure.
4. Decide whether history cleanup is appropriate and coordinate it with collaborators.

History rewriting and credential rotation are intentionally manual operations; repository cleanup alone does not invalidate an exposed credential.

## Release verification

- Run Django checks with the intended LLM provider configuration.
- Run backend tests against PostgreSQL.
- Run frontend lint and the production build.
- Apply forward-only database migrations after taking a database backup.
- Exercise registration, login, generation, sharing, feedback, analytics, and health endpoints.
- Confirm rollback artifacts and database recovery procedures before changing production.
