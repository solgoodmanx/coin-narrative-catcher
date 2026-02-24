#!/usr/bin/env python3
"""Quick launchpad attribution checker for Base/EVM CAs.
Checks Virtuals, Clanker, Bankr, Flaunch, Doppler and prints compact JSON summary.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, Tuple

JsonFetcher = Callable[[str], Tuple[int | None, Any]]
TextFetcher = Callable[[str], Tuple[int | None, str]]


def get_json(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
        "Origin": "https://app.doppler.lol",
        "Referer": "https://app.doppler.lol/",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read().decode("utf-8", errors="replace")
            return r.status, json.loads(data)
    except Exception as e:  # pragma: no cover - network failure path
        return None, {"error": str(e)}


def get_text(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read().decode("utf-8", errors="replace")
            return r.status, data
    except Exception as e:  # pragma: no cover - network failure path
        return None, str(e)


def classify_launchpad(ca: str, json_fetcher: JsonFetcher = get_json, text_fetcher: TextFetcher = get_text) -> Dict[str, Any]:
    """Classify token launch source and return evidence-rich attribution output."""
    ca = ca.strip()
    ca_l = ca.lower()

    out: Dict[str, Any] = {
        "ca": ca,
        "classification": None,
        "confidenceTier": "none",  # exact | heuristic | none
        "alsoIndexedOn": [],
        "virtuals": {"match": False, "confidenceTier": "none"},
        "clanker": {"match": False, "confidenceTier": "none"},
        "bankr": {"match": False, "confidenceTier": "none"},
        "flaunch": {"match": False, "confidenceTier": "none", "heuristic": "flETH quote token on DexScreener"},
        "doppler": {"match": False, "confidenceTier": "none", "heuristic": "token is indexed on app.doppler.lol"},
    }

    # Virtuals
    v_url = (
        "https://api2.virtuals.io/api/virtuals?filters[preToken]="
        + urllib.parse.quote(ca)
        + "&pagination[page]=1&pagination[pageSize]=1&populate=creator"
    )
    s, v = json_fetcher(v_url)
    if s == 200 and isinstance(v, dict) and v.get("data"):
        d0 = v["data"][0]
        out["virtuals"] = {
            "match": True,
            "confidenceTier": "exact",
            "name": d0.get("name"),
            "symbol": d0.get("symbol"),
            "creator": (d0.get("creator") or {}).get("socials"),
            "factory": d0.get("factory"),
            "acpAgentId": d0.get("acpAgentId"),
        }

    # Clanker
    c_url = (
        "https://www.clanker.world/api/tokens?q="
        + urllib.parse.quote(ca)
        + "&includeUser=true&includeMarket=true"
    )
    s, c = json_fetcher(c_url)
    if s == 200 and isinstance(c, dict):
        data = c.get("data") or []
        exact = None
        for row in data:
            if str(row.get("contract_address", "")).lower() == ca_l:
                exact = row
                break
        if exact:
            out["clanker"] = {
                "match": True,
                "confidenceTier": "exact",
                "name": exact.get("name"),
                "symbol": exact.get("symbol"),
                "type": exact.get("type"),
                "admin": exact.get("admin"),
                "msg_sender": exact.get("msg_sender"),
                "market": ((exact.get("related") or {}).get("market")),
            }

    # Bankr
    b_url = "https://api.bankr.bot/token-launches/" + urllib.parse.quote(ca)
    s, b = json_fetcher(b_url)
    if s == 200 and isinstance(b, dict) and not b.get("error"):
        launch = b.get("launch") or {}
        out["bankr"] = {
            "match": True,
            "confidenceTier": "exact",
            "tokenName": launch.get("tokenName"),
            "tokenSymbol": launch.get("tokenSymbol"),
            "deployer": launch.get("deployer"),
            "feeRecipient": launch.get("feeRecipient"),
            "tweetUrl": launch.get("tweetUrl"),
            "websiteUrl": launch.get("websiteUrl"),
            "raw": b,
        }

    # Flaunch (heuristic): token has active DexScreener pair quoted in flETH
    fleth_addr = "0x000000000d564d5be76f7f0d28fe52605afc7cf8"
    d_url = "https://api.dexscreener.com/latest/dex/tokens/" + urllib.parse.quote(ca)
    s, d = json_fetcher(d_url)
    if s == 200 and isinstance(d, dict):
        pairs = d.get("pairs") or []
        fl_pairs = []
        for p in pairs:
            q = (p.get("quoteToken") or {}).get("address", "")
            if str(q).lower() == fleth_addr:
                fl_pairs.append(
                    {
                        "pairAddress": p.get("pairAddress"),
                        "dexId": p.get("dexId"),
                        "chainId": p.get("chainId"),
                    }
                )
        if fl_pairs:
            out["flaunch"] = {
                "match": True,
                "confidenceTier": "heuristic",
                "heuristic": "flETH quote token on DexScreener",
                "flETH": fleth_addr,
                "pairs": fl_pairs,
            }

    # Doppler index check (heuristic): token page + search index hit
    ds_url = "https://app.doppler.lol/api/search?query=" + urllib.parse.quote(ca)
    s, ds = json_fetcher(ds_url)
    indexed = False
    if s == 200 and isinstance(ds, list):
        for row in ds:
            if str(row.get("address", "")).lower() == ca_l:
                indexed = True
                break

    page_url = f"https://app.doppler.lol/tokens/base/{ca_l}"
    sp, html = text_fetcher(page_url)
    has_doppler_title = sp == 200 and bool(re.search(r"\|\s*Doppler", html, re.I))

    if indexed or has_doppler_title:
        out["doppler"] = {
            "match": True,
            "confidenceTier": "heuristic",
            "heuristic": "token is indexed on app.doppler.lol",
            "pageUrl": page_url,
            "searchIndexed": indexed,
        }

    # classify (mutually exclusive primary source; keep secondary index hints)
    if out["virtuals"]["match"]:
        out["classification"] = "virtuals"
        out["confidenceTier"] = out["virtuals"]["confidenceTier"]
    elif out["clanker"]["match"]:
        out["classification"] = "clanker"
        out["confidenceTier"] = out["clanker"]["confidenceTier"]
    elif out["bankr"]["match"]:
        out["classification"] = "bankr"
        out["confidenceTier"] = out["bankr"]["confidenceTier"]
    elif out["flaunch"]["match"]:
        out["classification"] = "flaunch"
        out["confidenceTier"] = out["flaunch"]["confidenceTier"]
    elif out["doppler"]["match"]:
        out["classification"] = "doppler"
        out["confidenceTier"] = out["doppler"]["confidenceTier"]
    else:
        out["classification"] = "unattributed"
        out["confidenceTier"] = "none"

    if out["doppler"]["match"] and out["classification"] != "doppler":
        out["alsoIndexedOn"].append("doppler")

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ca", help="Contract address")
    args = ap.parse_args()

    out = classify_launchpad(args.ca)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
