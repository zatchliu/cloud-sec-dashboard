# Agent and contributor conventions

This file is for humans and coding agents. Follow it so local work matches CI.

## Project status

Phase 0 is **repository and pipeline** only. Do not add FastAPI, React, Postgres,
Terraform, or AWS code until a later phase is explicitly requested.

## Tooling

- Use **uv** for Python. Do not use Conda, `pip install --user`, or `sudo pip`.
- Runtime is **Python 3.12**, pinned in `.python-version` and `requires-python`.
- Install hooks after clone:

  ```bash
  uv sync --group dev
  uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
  ```

- Run the same checks CI runs:

  ```bash
  uv run pre-commit run --all-files
  ```

## Git workflow

- Default branch is `main`. Do not commit application work directly on `main`.
- Branch names: `feat/...`, `fix/...`, `docs/...`, `chore/...`, `ci/...`.
- Commit messages must be [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, `build:`,
  `ci:`, `chore:`, `revert:`.
- Example: `docs: add Phase 0 threat model draft`.
- Sign commits (SSH signing; see [`docs/github-setup.md`](docs/github-setup.md)).

## Secrets

- Never commit `.env`, AWS keys, tokens, private keys, or credentials.
- Public GitHub Actions logs are world-readable. Do not echo secrets in CI.
- If a hook flags a false positive, document an allowlist change in the PR;
  do not disable gitleaks.

## Documentation

- Architecture decisions live in `docs/adr/`. Add a new ADR when changing
  stack, layout, or process; do not silently rewrite history in ADR-0001.
- Threat model: `docs/threat-model.md` (draft until the app exists).
- GitHub click-path setup (repo, rulesets, signing): `docs/github-setup.md`.

## Layout (decided, not created yet)

Monorepo. Future roots (create when that phase starts, not before):

- `apps/api` — FastAPI
- `apps/web` — React + TypeScript (Vite)
- `infra` — OpenTofu/Terraform

## PR expectations

- One concern per PR when practical.
- CI job `ci` must be green (`pre-commit` on all files).
- Do not add paid cloud resources or long-lived AWS credentials.
