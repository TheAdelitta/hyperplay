# Hyperplay Backend

FastAPI integration layer for Hyperplay. It accepts educational material, extracts PDF text,
calls the configured Azure AI deployment, validates a declarative simulation specification, and
returns it to the frontend.

## Local setup

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

PowerShell activation is `.\.venv\Scripts\Activate.ps1`; copy the environment template with
`Copy-Item ..\.env.example .env`.

## Verify

```bash
ruff check .
pytest -q
python scripts/export_schema.py
```

The generated schema belongs at `../contracts/simulation-spec.schema.json`. Commit contract
changes only after coordinating with both integration partners.

## Frontend integration

Use `GET /api/v1/simulations/demo` before Azure is ready. Submit live material as multipart form
data to `POST /api/v1/simulations/generate`, using either `text` or `file`.

## Azure integration

`AzureSimulationGenerator` is the only model-specific adapter. If the Azure teammate provides a
custom HTTP endpoint instead of direct model credentials, replace this adapter while preserving
the `SimulationGenerator` protocol and API routes.

