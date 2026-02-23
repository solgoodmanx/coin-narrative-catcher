#!/usr/bin/env python3
"""Quick launchpad attribution checker for Base/EVM CAs.
Checks Virtuals, Clanker, Bankr and prints compact JSON summary.
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
        "virtuals": {"match": False},
        "clanker": {"match": False},
        "bankr": {"match": False},
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
        out["bankr"] = {"match": True, "data": b}

    # classify (mutually exclusive in practice)
    if out["virtuals"]["match"]:
        out["classification"] = "virtuals"
    elif out["clanker"]["match"]:
        out["classification"] = "clanker"
    elif out["bankr"]["match"]:
        out["classification"] = "bankr"
    else:
        out["classification"] = "unattributed"

    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
