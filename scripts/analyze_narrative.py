#!/usr/bin/env python3
"""One-command narrative report generator.

Focuses on catalyst + credibility + launchpad attribution, with tape as secondary.

Usage:
  python3 scripts/analyze_narrative.py --ca <contract_or_mint>
  python3 scripts/analyze_narrative.py --ca <CA> --x-handle MossYGravel --x-handle Andrei_Eternal
"""

import argparse
import json
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


def get_json(url: str) -> Optional[Dict[str, Any]]:
    req = urllib.request.Request(url, headers={"User-Agent": "coin-narrative-catcher/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except Exception:
        return None


def fetch_dex(ca: str) -> Dict[str, Any]:
    out = {"token": None, "pairs": [], "primary": None, "tweet_links": []}
    d = get_json(f"https://api.dexscreener.com/latest/dex/tokens/{urllib.parse.quote(ca)}") or {}
    pairs = d.get("pairs") or []
    out["pairs"] = pairs
    if pairs:
        primary = sorted(pairs, key=lambda p: (p.get("volume", {}).get("h24") or 0), reverse=True)[0]
        out["primary"] = primary
        bt = primary.get("baseToken") or {}
        out["token"] = {
            "name": bt.get("name"),
            "symbol": bt.get("symbol"),
            "chainId": primary.get("chainId"),
        }

        info = primary.get("info") or {}
        links = []
        for w in info.get("websites") or []:
            u = w.get("url")
            if u:
                links.append(u)
        for s in info.get("socials") or []:
            u = s.get("url")
            if u:
                links.append(u)
        out["tweet_links"] = [u for u in links if "x.com/" in u or "twitter.com/" in u]
    return out


def launchpad_attribution(ca: str) -> Dict[str, Any]:
    # inlined light version of check_launchpads.py for single-command UX
    ca_l = ca.lower()
    out = {
        "classification": "unattributed",
        "virtuals": {"match": False},
        "clanker": {"match": False},
        "bankr": {"match": False},
    }

    v = get_json(
        "https://api2.virtuals.io/api/virtuals?filters[preToken]="
        + urllib.parse.quote(ca)
        + "&pagination[page]=1&pagination[pageSize]=1&populate=creator"
    ) or {}
    if v.get("data"):
        d0 = v["data"][0]
        creator = d0.get("creator") or {}
        socials = creator.get("socials") or {}
        usernames = socials.get("VERIFIED_USERNAMES") or {}
        links = socials.get("VERIFIED_LINKS") or {}
        twitter_handle = usernames.get("TWITTER")
        acp_agent_id = d0.get("acpAgentId")
        creator_email = creator.get("email")

        out["virtuals"] = {
            "match": True,
            "name": d0.get("name"),
            "symbol": d0.get("symbol"),
            "creator": socials,
            "creatorEmailMasked": creator_email,
            "creatorEmailHintIsVirtuals": isinstance(creator_email, str) and creator_email.endswith("v***.io"),
            "linkedHandlesCurrent": {"twitter": twitter_handle},
            "linkedHandleLinks": {"twitter": links.get("TWITTER")},
            "factory": d0.get("factory"),
            "acpAgentId": acp_agent_id,
            "virtualsId": d0.get("id"),
            "links": {
                "virtualsTrading": f"https://app.virtuals.io/virtuals/{d0.get('id')}" if d0.get("id") is not None else None,
                "agdp": f"https://agdp.io/agent/{acp_agent_id}" if acp_agent_id else None,
            },
        }
        out["classification"] = "virtuals"
        return out

    c = get_json(
        "https://www.clanker.world/api/tokens?q="
        + urllib.parse.quote(ca)
        + "&includeUser=true&includeMarket=true"
    ) or {}
    for row in (c.get("data") or []):
        if str(row.get("contract_address", "")).lower() == ca_l:
            out["clanker"] = {
                "match": True,
                "name": row.get("name"),
                "symbol": row.get("symbol"),
                "type": row.get("type"),
            }
            out["classification"] = "clanker"
            return out

    b = get_json("https://api.bankr.bot/token-launches/" + urllib.parse.quote(ca))
    if b and not b.get("error"):
        out["bankr"] = {"match": True}
        out["classification"] = "bankr"

    return out


def score_from_signals(attr: Dict[str, Any], dex: Dict[str, Any], handles: List[str]) -> Dict[str, int]:
    # Heuristic defaults; caller should override with human judgment.
    catalyst = 2
    cred = 2
    narrative = 3
    social = 2
    tape = 2
    attribution_integrity = 1

    if handles:
        catalyst += 1
        cred += 1
        attribution_integrity += 1

    if attr["classification"] in {"virtuals", "clanker", "bankr"}:
        catalyst += 1
        narrative += 1
        attribution_integrity += 2

    p = dex.get("primary") or {}
    v24 = (p.get("volume") or {}).get("h24") or 0
    liq = (p.get("liquidity") or {}).get("usd") or 0
    if v24 > 100000:
        tape += 1
    if liq > 50000:
        tape += 1

    info = p.get("info") or {}
    has_project_x = any((s.get("type") == "twitter" and s.get("url")) for s in (info.get("socials") or []))
    has_website = bool((info.get("websites") or []))
    if has_project_x and has_website:
        attribution_integrity += 1

    def c(v: int) -> int:
        return max(0, min(5, v))

    return {
        "catalyst": c(catalyst),
        "credibility": c(cred),
        "narrative": c(narrative),
        "social_propagation": c(social),
        "tape_confirmation": c(tape),
        "attribution_integrity": c(attribution_integrity),
    }


def parse_tweet_id(url: str) -> Optional[str]:
    m = re.search(r"status/(\d+)", url)
    return m.group(1) if m else None


def resolve_top_tweet(tweet_links: List[str]) -> Optional[Dict[str, Any]]:
    for u in tweet_links:
        tid = parse_tweet_id(u)
        if not tid:
            continue
        fx = get_json(f"https://api.fxtwitter.com/i/status/{tid}") or {}
        tw = fx.get("tweet")
        if tw:
            return {
                "url": tw.get("url") or u,
                "author": (tw.get("author") or {}).get("screen_name"),
                "text": tw.get("text") or "",
                "likes": tw.get("likes"),
                "views": tw.get("views"),
            }
    return None


def fetch_x_profile(handle: str) -> Optional[Dict[str, Any]]:
    h = handle.lstrip("@")
    fx = get_json(f"https://api.fxtwitter.com/{urllib.parse.quote(h)}") or {}
    return fx.get("user")


def linked_handle_crosscheck(
    linked_handle: Optional[str], token_name: Optional[str], token_symbol: Optional[str], top_tweet: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Cross-check linked handle for direct/indirect shill clues with currently available public data."""
    out: Dict[str, Any] = {
        "linkedHandle": linked_handle,
        "directShill": "unknown",
        "indirectClues": [],
        "timingAlignment": "unknown",
        "shillQuality": "unknown",
        "confidence": "unknown",
    }
    if not linked_handle:
        return out

    h = linked_handle.lstrip("@").lower()
    profile = fetch_x_profile(h)
    if profile:
        desc = (profile.get("description") or "").lower()
        website = ((profile.get("website") or {}).get("url") or "").lower()
        n = (token_name or "").lower()
        s = (token_symbol or "").lower()
        if n and n in desc:
            out["indirectClues"].append("token name mentioned in linked-handle bio")
        if s and s and f"${s}" in desc:
            out["indirectClues"].append("ticker appears in linked-handle bio")
        if "virtuals" in desc:
            out["indirectClues"].append("linked handle bio references Virtuals")
        if website:
            out["indirectClues"].append("linked handle has external website configured")

    if top_tweet and top_tweet.get("author"):
        author = str(top_tweet.get("author")).lstrip("@").lower()
        if author == h:
            out["directShill"] = "yes"
            out["timingAlignment"] = "strong"
            out["confidence"] = "confirmed"
        else:
            out["directShill"] = "no"
            out["timingAlignment"] = "weak"
            out["confidence"] = "likely"

    if out["directShill"] == "yes":
        out["shillQuality"] = "manual-review-needed"
    elif out["indirectClues"]:
        out["shillQuality"] = "signal-present"
    else:
        out["shillQuality"] = "low-signal"

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ca", required=True, help="Contract address / token mint")
    ap.add_argument("--x-handle", action="append", default=[], help="Known key handles")
    args = ap.parse_args()

    ca = args.ca.strip()
    handles = [h.lstrip("@") for h in args.x_handle]

    dex = fetch_dex(ca)
    attr = launchpad_attribution(ca)
    top_tweet = resolve_top_tweet(dex.get("tweet_links") or [])
    score = score_from_signals(attr, dex, handles)
    total = sum(score.values())

    token = dex.get("token") or {}
    p = dex.get("primary") or {}

    linked_twitter = None
    if attr.get("classification") == "virtuals":
        linked_twitter = ((attr.get("virtuals") or {}).get("linkedHandlesCurrent") or {}).get("twitter")
    cross = linked_handle_crosscheck(linked_twitter, token.get("name"), token.get("symbol"), top_tweet)

    print(f"## Narrative Read — {token.get('name') or 'Unknown'} ({token.get('symbol') or '?'})")
    print()
    print("### 1) Core Bullish Thesis (Draft)")
    print(f"- Token discovered on {token.get('chainId') or 'unknown chain'}; attribution: **{attr['classification']}**.")
    if handles:
        print(f"- Key handles supplied: {', '.join('@'+h for h in handles)}.")
    if top_tweet:
        print(f"- Catalyst candidate appears linked to tweet by @{top_tweet.get('author')} ({top_tweet.get('url')}).")
    else:
        print("- No clear catalyst tweet auto-resolved; requires manual CT scan.")
    print()

    print("### 2) Catalyst Genealogy")
    print(f"- Origin: {top_tweet.get('url') if top_tweet else 'unknown'}")
    print("- Credible amplifiers: manual enrichment needed")
    print("- Protocol acknowledgment: manual enrichment needed")
    print("- Adoption wave evidence: manual enrichment needed")
    print()

    print("### 3) Credibility Graph")
    print(f"- Builder/Origin handles: {', '.join('@'+h for h in handles) if handles else 'not supplied'}")
    print(f"- Launchpad attribution: {attr['classification']}")
    if attr.get("classification") == "virtuals":
        v = attr.get("virtuals") or {}
        current_twitter = (v.get("linkedHandlesCurrent") or {}).get("twitter")
        print(f"- Linked handles (current): {'@'+current_twitter if current_twitter else 'none'}")
        print("- Linked handles (previous): unavailable from public API")
        print(f"- Creator email (masked): {v.get('creatorEmailMasked')}")
        print(f"- Creator email virtuals-domain hint: {'yes' if v.get('creatorEmailHintIsVirtuals') else 'no'}")
        links = v.get("links") or {}
        print(f"- aGDP link: {links.get('agdp') or 'not provided by API; use manual AGDP agent-name+CA cross-check'}")
        print(f"- Virtuals trading link: {links.get('virtualsTrading')}")
    print("- Trust grade: pending manual verification")
    print()

    print("### 4) Linked Handle Cross-check")
    print(f"- Linked handle: {cross.get('linkedHandle') or 'none'}")
    print(f"- Direct shill detected: {cross.get('directShill')}")
    print(f"- Indirect clues: {', '.join(cross.get('indirectClues') or []) or 'none'}")
    print(f"- Timing alignment: {cross.get('timingAlignment')}")
    print(f"- Shill quality: {cross.get('shillQuality')}")
    print(f"- Confidence: {cross.get('confidence')}")
    print()

    print("### 5) Confirmation Layer (Secondary)")
    v24 = (p.get("volume") or {}).get("h24")
    liq = (p.get("liquidity") or {}).get("usd")
    pc24 = (p.get("priceChange") or {}).get("h24")
    print(f"- 24h volume: {v24}")
    print(f"- liquidity (usd): {liq}")
    print(f"- 24h price change: {pc24}")
    print()

    print("### 6) Score")
    print(f"- Catalyst: {score['catalyst']}/5")
    print(f"- Credibility: {score['credibility']}/5")
    print(f"- Narrative: {score['narrative']}/5")
    print(f"- Social propagation: {score['social_propagation']}/5")
    print(f"- Tape confirmation: {score['tape_confirmation']}/5")
    print(f"- Attribution integrity: {score['attribution_integrity']}/5")
    print(f"- **Total narrative strength: {total}/30**")
    print()

    print("### 7) Next Actions")
    print("1. Run x-research query on CA + ticker + key handles for amplification map.")
    print("2. Verify builder claims from primary sources (official pages/repos).")
    print("3. Confirm whether token capture mechanics are live or only promised.")
    print("4. Directionality check before claims: verify A→B and B→A links separately.")


if __name__ == "__main__":
    main()
