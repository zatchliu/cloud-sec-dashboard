# Cloud security dashboard

A local-first cloud security dashboard learning project built with Python 3.12,
FastAPI, and AWS SDK tooling. The repository currently contains a small API,
domain models for resources and findings, an S3 bucket collector, PostgreSQL
configuration and an initial database migration. This is an early foundation:
there is no dashboard UI, scan orchestration, findings API, authentication, or
deployed AWS infrastructure yet.

## Current functionality

- `GET /` returns a basic greeting; `GET /health` returns `{"status":"ok"}`.
- `collect_s3_buckets(client)` reads bucket region, public access block
  configuration, ACL grants, and bucket policy into domain `Resource` objects.
  It accepts a boto3 S3 client; it is not exposed through an API endpoint.
- The domain package defines `Resource`, `Finding`, and finding severity.
- Alembic has an initial migration for a `cloud_accounts` table. The API does
  not currently read or write to PostgreSQL.
- GitHub Actions runs the repository's pre-commit hooks on pushes to `main`
  and pull requests.

Stack decisions: [`docs/adr/0001-tech-stack.md`](docs/adr/0001-tech-stack.md).
Threat model (draft): [`docs/threat-model.md`](docs/threat-model.md).
GitHub remote setup: [`docs/github-setup.md`](docs/github-setup.md).
Contributor conventions: [`AGENTS.md`](AGENTS.md).

## Local development

Use **uv** with **Python 3.12**. After installing uv and Python 3.12, clone the
repository and run:

```bash
uv sync --group dev
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Start the API locally with hot reload:

```bash
uv run uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API docs are at
`http://127.0.0.1:8000/docs`.

## PostgreSQL

The Compose configuration starts PostgreSQL 16 with a local development
database named `csd`:

```bash
make db-up
```

The configured default connection URL is
`postgresql+psycopg://csd:csd@localhost:5432/csd`. To create the current schema,
run:

```bash
uv run alembic upgrade head
```

Stop the database with `make db-down`. The API currently starts without a
database connection; database persistence is not implemented yet.

## Checks

Run the same pre-commit checks as CI:

```bash
uv run pre-commit run --all-files
```

The repository also provides `make test` for pytest and `make lint` for Ruff
and mypy.

## License

MIT. See [LICENSE](LICENSE).
