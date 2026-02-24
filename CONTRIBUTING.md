# Contributing

Thanks for helping improve `coin-narrative-catcher`.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run checks

```bash
python -m unittest discover -s tests -v
```

## Commit guidelines

- Keep commits small and focused (one behavior change per commit when possible).
- Include evidence links when changing attribution logic.
- If you add a new external data source, also update `docs/data-sources.md`.
- For launchpad logic changes, add/update tests in `tests/test_check_launchpads.py`.

## Release flow

- Patch (`vX.Y.Z`): bug fix / no behavior changes to API contracts.
- Minor (`vX.Y.0`): new capabilities (new launchpad support, new heuristics).
- Major (`vX.0.0`): breaking behavior/output changes.
