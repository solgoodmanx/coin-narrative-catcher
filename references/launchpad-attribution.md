# Launchpad Attribution (Virtuals / Clanker / Bankr)

Run this before narrative scoring for Base/EVM tokens.

## Why

Launchpad identity often explains narrative source and audience:
- Virtuals -> agent economy / ACP narratives
- Clanker -> clanker-native builder and fee mechanics narratives
- Bankr -> Bankr launch and fee sharing narratives

## Rule

Treat attribution as mutually exclusive in practice once one exact source matches.

## Exact-match logic

1. Normalize CA to lowercase.
2. Check Virtuals preToken exact match.
3. Check Clanker exact `contract_address` match from API dataset.
4. Check Bankr launch endpoint exact hit.
5. First confident exact match wins.

## Script

Use:

```bash
python3 scripts/check_launchpads.py <CA>
```

Output includes:
- `classification`: virtuals | clanker | bankr | unattributed
- source-specific metadata (creator socials, factory, acpAgentId, etc.)

## API endpoints

- Virtuals:
  - `https://api2.virtuals.io/api/virtuals?filters[preToken]={CA}&populate=creator`
- Clanker:
  - `https://www.clanker.world/api/tokens?q={CA}&includeUser=true&includeMarket=true`
- Bankr:
  - `https://api.bankr.bot/token-launches/{CA}`
