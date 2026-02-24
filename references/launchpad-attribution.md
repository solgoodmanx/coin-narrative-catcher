# Launchpad Attribution (Virtuals / Clanker / Bankr / Flaunch)

Run this before narrative scoring for Base/EVM tokens.

## Why

Launchpad identity often explains narrative source and audience:
- Virtuals -> agent economy / ACP narratives
- Clanker -> clanker-native builder and fee mechanics narratives
- Bankr -> Bankr launch and fee sharing narratives
- Flaunch -> flETH-quoted launch flow, fee/buyback game-theory narratives

## Rule

Treat attribution as mutually exclusive in practice once one exact source matches.

## Exact-match logic

1. Normalize CA to lowercase.
2. Check Virtuals preToken exact match.
3. Check Clanker exact `contract_address` match from API dataset.
4. Check Bankr launch endpoint exact hit.
5. Check Flaunch heuristic: DexScreener pairs quote the CA in `flETH` (`0x000000000d564d5be76f7f0d28fe52605afc7cf8`).
6. First confident match wins (exact matches preferred; Flaunch currently heuristic).

## Script

Use:

```bash
python3 scripts/check_launchpads.py <CA>
```

Output includes:
- `classification`: virtuals | clanker | bankr | flaunch | unattributed
- source-specific metadata (creator socials, factory, acpAgentId, etc.)

## aGDP link rule

For Virtuals agents, prefer ID-based aGDP links:
- `https://agdp.io/agent/<acpAgentId>`

Do not assume CA-based aGDP links will always resolve reliably.

## API endpoints

- Virtuals:
  - `https://api2.virtuals.io/api/virtuals?filters[preToken]={CA}&populate=creator`
- Clanker:
  - `https://www.clanker.world/api/tokens?q={CA}&includeUser=true&includeMarket=true`
- Bankr:
  - `https://api.bankr.bot/token-launches/{CA}`
- Flaunch heuristic inputs:
  - DexScreener token endpoint: `https://api.dexscreener.com/latest/dex/tokens/{CA}`
  - Confirm at least one pair has quote token `flETH` address `0x000000000d564d5be76f7f0d28fe52605afc7cf8`
