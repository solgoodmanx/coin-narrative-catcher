# coin-narrative-catcher

CT-first memecoin narrative analysis skill for OpenClaw.

## What it does

- Prioritizes catalyst origin + credibility graph + narrative payload
- Uses tape/flow as secondary confirmation
- Includes launchpad attribution checks for:
  - Virtuals (exact)
  - Clanker (exact)
  - Bankr (exact)
  - Flaunch (heuristic)
  - Doppler (heuristic/index signal)

## Trust model (attribution confidence)

- **exact**: first-party launch source returns an exact CA match
- **heuristic**: strong indirect evidence (e.g., flETH quote token, indexed launch page)
- **none**: no reliable source signal

Output includes:
- `classification`
- `confidenceTier`
- `alsoIndexedOn` (secondary index hints)

## Why these APIs are used

These are not random outbound calls; they are domain-specific crypto launch/trading data providers.

- `api.dexscreener.com` for market/tape and quote-token heuristics
- `api2.virtuals.io` for Virtuals attribution
- `www.clanker.world` for Clanker exact-match attribution
- `api.bankr.bot` for Bankr launch metadata (including deployer + fee recipient)
- `app.doppler.lol` for Doppler index detection
- `api.fxtwitter.com` for tweet resolution where needed
- `agdp.io` for Virtuals agent deep links

See `docs/data-sources.md` for detailed trust/failure notes.

## Structure

- `SKILL.md` — core skill instructions
- `references/` — scoring framework, output template, attribution rules
- `scripts/check_launchpads.py` — classify CA across launchpad sources
- `scripts/credibility_graph.py` — build lightweight identity/credibility graph
- `scripts/analyze_narrative.py` — one-command narrative draft report
- `tests/` — attribution logic tests

## Quick usage

### Launchpad attribution

```bash
python3 scripts/check_launchpads.py <CA>
```

### Credibility graph

```bash
python3 scripts/credibility_graph.py --handles <x_handle1> <x_handle2> --github <gh_user1>
```

### One-command narrative draft

```bash
python3 scripts/analyze_narrative.py --ca <CA> --x-handle <key_handle>
```

## Quality controls

- CI: `.github/workflows/ci.yml`
- Tests: `python -m unittest discover -s tests -v`
- Security policy: `SECURITY.md`
- Contribution guide: `CONTRIBUTING.md`
- License: `LICENSE` (MIT)

## Maintainer

- X: [@solgoodman](https://x.com/solgoodman)

## Versioning / releases

Use semantic versioning tags:

- `v0.1.0` initial stable milestone
- `v0.1.1` bugfix-only release
- `v0.2.0` new capability release (e.g., new launchpad support)

Recommended flow:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Then create a GitHub Release with a short changelog.

## Package skill

```bash
python3 ~/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py . ./dist
```
