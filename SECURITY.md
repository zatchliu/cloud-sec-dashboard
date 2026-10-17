# Security policy

This is a public learning project. Treat it as if it were production: **never
commit secrets**, and assume the git history is world-readable.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for suspected vulnerabilities.

1. Use GitHub **Security → Advisories → New draft security advisory** on this
   repository (private until you publish), or
2. Email the maintainer associated with this GitHub account.

Include what you found, how to reproduce it, and impact. I will acknowledge
the report and work on a fix before any public disclosure.

## Secrets and credentials

- Do not put AWS keys, tokens, or private keys in this repo, in GitHub Actions
  logs, or in issue comments.
- Local secrets belong in a gitignored `.env` (not present in Phase 0).
- If you accidentally commit a secret, **rotate it immediately**. Removing it
  from git history is not enough; the value is already compromised.

## Scope (current)

Phase 0 only ships repository controls: signed-commit workflow (local),
gitleaks via pre-commit, and a public GitHub Actions job that re-runs those
hooks. Application attack surface (API, UI, AWS) is documented as a draft in
[`docs/threat-model.md`](docs/threat-model.md) and is not implemented yet.
