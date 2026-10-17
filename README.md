# Cloud security dashboard

Production-style **DevSecOps** learning project: a cloud security dashboard
built with a public GitHub pipeline, local-first development, and $0 cloud
spend in early phases.

**Phase 0 (current):** local repo, pre-commit (gitleaks + Conventional Commits),
and a GitHub Actions workflow that runs those same checks. There is no API, UI,
or AWS integration yet. Signed commits and branch protection are **not** used.

Stack decisions: [`docs/adr/0001-tech-stack.md`](docs/adr/0001-tech-stack.md).
Threat model (draft): [`docs/threat-model.md`](docs/threat-model.md).
Create the GitHub remote and watch Actions: [`docs/github-setup.md`](docs/github-setup.md).
Agent/contributor rules: [`AGENTS.md`](AGENTS.md).

## Local environment

This project uses **uv** and **Python 3.12**. Do not use Conda for this repo.

```bash
# uv and Python 3.12 (skip if already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.12

# clone, then:
cd cloud-sec-dashboard
uv sync --group dev
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Same checks as CI:

```bash
uv run pre-commit run --all-files
```

### Docker (needed in later phases)

Phase 0 does not start containers, but Postgres/Testcontainers will need Docker
from WSL2. If `docker ps` prints that Docker could not be found in this distro:

1. Open **Docker Desktop** on Windows.
2. **Settings → General**: Use the WSL 2 based engine.
3. **Settings → Resources → WSL integration**: enable your Ubuntu distro.
4. Apply, then in WSL run `docker ps` again.

### GitHub CLI

`gh` should be on `PATH` (`~/.local/bin/gh`). Authenticate with
`gh auth login` when you create the public remote (see
[`docs/github-setup.md`](docs/github-setup.md)).

## License

MIT. See [LICENSE](LICENSE).
