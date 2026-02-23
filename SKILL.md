---
name: coin-narrative-catcher
description: CT-first memecoin narrative analysis for fast-moving token calls. Use when a user asks whether a coin is bullish/bearish, asks for "alpha," shares a contract address, asks what people on X are saying, or wants deeper catalyst/credibility analysis. Prioritize who launched/shilled, why their identity matters, what event triggered attention, and what narrative the market is buying; use volume/price data only as confirmation.
---

# Coin Narrative Catcher

Run memecoin analysis with a narrative-first lens.

## Workflow

1. **Identify token + chain quickly**
   - If user gives a CA only, pull DexScreener token endpoint first.
   - Extract token name/symbol, chain, and linked socials/websites.

2. **Run launchpad attribution (Base/EVM)**
   - Mandatory check: Virtuals / Clanker / Bankr attribution.
   - Use `scripts/check_launchpads.py <CA>`.
   - Apply exact-match rules from `references/launchpad-attribution.md`.

3. **Find the catalyst origin**
   - Pull linked X post(s) from DexScreener metadata when present.
   - Search X for:
     - CA exact string
     - `$TICKER`
     - project/account names
     - key people handles tied to launch
   - Use `x-research` skill for broad and ranked signal scans.

4. **Build credibility graph (most important)**
   - Map: creator → prior roles/projects → known ecosystem relationships.
   - Use `scripts/credibility_graph.py` for quick node/edge skeleton, then enrich manually.
   - Separate:
     - **High-credibility builders/accounts** (industry proof, track record)
     - **Mid-signal amplifiers** (CT traders/KOLs)
     - **Low-signal noise** (generic shill/repost spam)

5. **Decode the narrative payload**
   - Answer explicitly:
     - Why are people buying this *story*?
     - What belief could re-rate demand?
     - What would invalidate that belief?

6. **Use tape as confirmation (secondary)**
   - Check volume/liquidity/tx flow/price expansion only after narrative.
   - Mark whether tape confirms or contradicts current narrative strength.

7. **Return a decision-grade output**
   - Use the output template in `references/output-template.md`.
   - Include a confidence score and invalidation triggers.

## Rules

- Do **not** lead with generic buy/sell counts.
- Do **not** treat ticker mentions alone as bullish signal.
- Prefer exact CA mentions and primary-source tweets over repost chains.
- Always distinguish:
  - **Catalyst** (what happened)
  - **Narrative** (what market believes)
  - **Confirmation** (what tape is doing)

## Quick command patterns

- Dex snapshot:
  - `web_fetch https://api.dexscreener.com/latest/dex/tokens/<CA>`
- Single tweet resolve:
  - `web_fetch https://api.fxtwitter.com/<user>/status/<id>`
- X scan:
  - `x-research search "<CA> OR $TICKER" --quick --markdown`
  - `x-research search "(<topic>) (from:<key_account>)" --quick --markdown`

## References

- Use `references/signal-framework.md` for scoring and disqualifiers.
- Use `references/output-template.md` for response structure.
- Use `references/launchpad-attribution.md` for Virtuals/Clanker/Bankr checks.
