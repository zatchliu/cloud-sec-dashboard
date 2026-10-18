# Agent and contributor conventions

## Project status

This is a learning project. Default to explaining and reviewing, not generating.
- Never write more than a small snippet unless I explicitly say "generate this".
- When I share my own code, review it and list issues instead of rewriting it.
- When I hit an error, give hints before the fix.
- For anything non-trivial, explain why, not just what.

## Tooling

- Use **uv** for Python. Do not use Conda, `pip install --user`, or `sudo pip`.
- Runtime is **Python 3.12**, pinned in `.python-version` and `requires-python`.
- After clone:

  ```bash
  uv sync --group dev
  uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
  ```

- Same checks as CI:

  ```bash
  uv run pre-commit run --all-files
  ```

## Git workflow

- Default branch is `main`. Pushing to `main` is fine for this solo project.
- Commit messages use [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `chore:`, `ci:`, …) because the `commit-msg` hook
  and CI expect that format.
- Do **not** require SSH/GPG signed commits.

## Secrets

- Never commit `.env`, AWS keys, tokens, private keys, or credentials.
- Public GitHub Actions logs are world-readable. Do not echo secrets in CI.

## Documentation

- Stack decisions: `docs/adr/0001-tech-stack.md`
- Threat model draft: `docs/threat-model.md`
- How to create the GitHub remote: `docs/github-setup.md`

## Layout (decided, not created yet)

- `apps/api` — FastAPI
- `apps/web` — React + TypeScript (Vite)
- `infra` — OpenTofu/Terraform
