# Threat model (draft)

Status: **draft**. The application does not exist yet. This document names
trust boundaries and crown jewels so later design is not security-as-afterthought.

Method: lightweight [STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
(Spoofing, Tampering, Repudiation, Information disclosure, Denial of service,
Elevation of privilege). Not a commercial TM tool.

## System (intended)

```text
Developer laptop --git push--> GitHub (public) --> GitHub Actions
Future user --> React UI --> FastAPI --> PostgreSQL
                              FastAPI --> AWS APIs
```

## Trust boundaries

| Boundary | Why it matters |
| --- | --- |
| Laptop → GitHub | Public repo: everything pushed is world-readable. |
| GitHub Actions | Workflow YAML and logs are public; secrets in env leak. |
| Browser → API | Untrusted clients; authn/z not designed yet. |
| API → Postgres | Findings and account identifiers concentrate here. |
| API → AWS | Credentials are the highest-value secret in the system. |

## Crown jewels

1. **AWS credentials** (access keys or assumed-role sessions).
2. **Database contents** (security findings, account IDs, resource ARNs).
3. **Future session cookies / tokens** for the dashboard.

## STRIDE (current vs later)

| Category | Phase 0 (this repo) | Later (to be designed) |
| --- | --- | --- |
| Spoofing | Not in scope for this solo repo (no signed commits). | Dashboard login, AWS IAM identity for the scanner. |
| Tampering | CI re-runs hooks on each push; no branch protection. | Integrity of findings, IaC, container images. |
| Repudiation | Git history on `main`. | Audit log of who scanned which account. |
| Information disclosure | gitleaks + gitignore of `.env`; assume public GitHub. | XSS in the UI, over-broad AWS list APIs, Postgres exposure. |
| Denial of service | N/A for a docs/tooling repo. | Rate limits, AWS API throttling, expensive scans. |
| Elevation of privilege | Single GitHub owner account. | Confused deputy: scanner IAM too broad; IDOR on findings. |

## Phase 0 controls (in place)

- Never commit secrets; `.env` is gitignored.
- **gitleaks** on commit and in CI (job `ci`).
- Public-repo assumption: no GitHub Actions secrets in Phase 0.

## Open questions (later phases)

- How the app authenticates to AWS (OIDC / short-lived roles vs static keys).
- Who can view findings (single user vs multi-tenant).
- Whether scan results are considered sensitive enough for encryption at rest
  beyond Postgres defaults.
