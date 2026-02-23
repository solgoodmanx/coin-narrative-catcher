# coin-narrative-catcher

CT-first memecoin narrative analysis skill for OpenClaw.

## What it does
- Prioritizes catalyst origin + credibility graph + narrative payload
- Uses tape/flow as secondary confirmation
- Includes launchpad attribution checks for Virtuals / Clanker / Bankr

## Structure
- `SKILL.md` — core skill instructions
- `references/` — scoring framework, output template, attribution rules
- `scripts/check_launchpads.py` — classify CA across Virtuals/Clanker/Bankr
- `scripts/credibility_graph.py` — build lightweight identity/credibility graph
- `scripts/analyze_narrative.py` — one-command narrative draft report (attribution + catalyst stub + score)

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

## Package skill
```bash
python3 ~/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py . ./dist
```
