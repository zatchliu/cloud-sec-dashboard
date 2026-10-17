# ADR-0001: Tech stack, monorepo, and local-first cost constraint

- Status: Accepted
- Date: 2026-10-17

## Context

This repository is a learning and resume project: a cloud security dashboard
built with production-style DevSecOps practices, at **zero ongoing cloud
cost** during early phases. The stack must be modern, hireable, and runnable
on a laptop (WSL2) before any AWS demo.

## Decision

### Language and packaging

- **Python 3.12** with **uv** (lockfile, isolated `.venv`, no Conda for this
  repo). uv is fast, produces a committed `uv.lock`, and matches how CI will
  install the same versions.

### API, data, and UI (later phases)

- **FastAPI + Pydantic v2** for the API.
- **PostgreSQL** (Docker locally), **SQLAlchemy 2.0**, **Alembic**.
- **React + TypeScript (Vite)** and **TanStack Query** for the UI.
- **boto3** for AWS API access in a later demo phase only.

### Repository shape

- **Monorepo** (one git repo, one pipeline, one threat model, one hook
  config) rather than separate API/UI/IaC repositories.
- Directories `apps/api`, `apps/web`, and `infra` are **documented now** and
  **created when that phase starts**, so the tree stays honest.

### Quality, supply chain, and CI (phased)

- Phase 0: **pre-commit** (gitleaks, Conventional Commits, file hygiene) and
  **GitHub Actions** job `ci` that runs the same hooks. Public repo so Actions
  minutes stay free.
- Later: ruff, mypy, pytest, Playwright, CodeQL/Semgrep, pip-audit, npm
  audit, Dependabot, Checkov, Trivy, Syft, cosign.

### Cloud and cost

- **Local-first.** No AWS, RDS, ALB, or Fargate in Phase 0.
- A later demo may use AWS Free Tier / credits. Until then, assume **$0**.
- **Public GitHub** on purpose: resume visibility and free Actions/GHCR later.

### Merge strategy

- **Squash merge** into `main` for a solo repository (linear history, one
  Conventional Commit per PR on `main`).

## Consequences

- Contributors and agents must use `uv`, not system or Conda Python.
- Changing the stack requires a new ADR, not a silent edit of this file.
- Empty placeholder packages are avoided; layout is this ADR plus `AGENTS.md`.
- Public history means secrets in git are a permanent incident — gitleaks is
  a Phase 0 control, not optional.
