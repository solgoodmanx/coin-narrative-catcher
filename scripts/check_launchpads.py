#!/usr/bin/env python3
"""Quick launchpad attribution checker for Base/EVM CAs.
Checks Virtuals, Clanker, Bankr, Flaunch and prints compact JSON summary.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "coin-narrative-catcher/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read().decode("utf-8", errors="replace")
            return r.status, json.loads(data)
    except Exception as e:
        return None, {"error": str(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ca", help="Contract address")
    args = ap.parse_args()

    ca = args.ca.strip()
    ca_l = ca.lower()

    out = {
        "ca": ca,
        "classification": None,
        "confidenceTier": "none",  # exact | heuristic | none
        "virtuals": {"match": False, "confidenceTier": "none"},
        "clanker": {"match": False, "confidenceTier": "none"},
        "bankr": {"match": False, "confidenceTier": "none"},
        "flaunch": {"match": False, "confidenceTier": "none", "heuristic": "flETH quote token on DexScreener"},
    }

    # Virtuals
    v_url = (
        "https://api2.virtuals.io/api/virtuals?filters[preToken]="
        + urllib.parse.quote(ca)
        + "&pagination[page]=1&pagination[pageSize]=1&populate=creator"
    )
    s, v = get_json(v_url)
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
    s, c = get_json(c_url)
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
    s, b = get_json(b_url)
    if s == 200 and isinstance(b, dict) and not b.get("error"):
        out["bankr"] = {"match": True, "confidenceTier": "exact", "data": b}

    # Flaunch (heuristic): token has active DexScreener pair quoted in flETH
    # flETH canonical address from Flaunch contracts/docs
    fleth_addr = "0x000000000d564d5be76f7f0d28fe52605afc7cf8"
    d_url = "https://api.dexscreener.com/latest/dex/tokens/" + urllib.parse.quote(ca)
    s, d = get_json(d_url)
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

    # classify (mutually exclusive in practice)
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
    else:
        out["classification"] = "unattributed"
        out["confidenceTier"] = "none"

    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
