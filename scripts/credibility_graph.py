#!/usr/bin/env python3
"""Build a lightweight credibility graph from handles + optional linked identities.

Usage:
  python3 credibility_graph.py --handles supernovajunn Andrei_Eternal --github kokoju007
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
        return None, {"error": str(e), "url": url}


def github_profile(user: str):
    s, d = get_json(f"https://api.github.com/users/{urllib.parse.quote(user)}")
    if s != 200 or not isinstance(d, dict) or d.get("message") == "Not Found":
        return None
    return {
        "login": d.get("login"),
        "name": d.get("name"),
        "bio": d.get("bio"),
        "public_repos": d.get("public_repos"),
        "followers": d.get("followers"),
        "created_at": d.get("created_at"),
        "updated_at": d.get("updated_at"),
        "html_url": d.get("html_url"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--handles", nargs="*", default=[], help="X handles without @")
    ap.add_argument("--github", nargs="*", default=[], help="GitHub usernames")
    ap.add_argument("--notes", nargs="*", default=[], help="Optional known credentials/facts")
    args = ap.parse_args()

    nodes = []
    edges = []

    for h in args.handles:
        nodes.append({"id": f"x:{h}", "type": "x_handle", "label": f"@{h}"})

    for g in args.github:
        profile = github_profile(g)
        node = {"id": f"gh:{g}", "type": "github", "label": g, "profile": profile}
        nodes.append(node)

    # naive link heuristic: exact text match handle==github means probable same identity
    handle_set = {h.lower() for h in args.handles}
    for g in args.github:
        if g.lower() in handle_set:
            edges.append({"from": f"x:{g}", "to": f"gh:{g}", "relation": "same-username"})

    for n in args.notes:
        nodes.append({"id": f"note:{len(nodes)+1}", "type": "claim", "label": n})

    out = {
        "summary": {
            "handle_count": len(args.handles),
            "github_count": len(args.github),
            "note_count": len(args.notes),
        },
        "nodes": nodes,
        "edges": edges,
        "next_checks": [
            "Confirm claimed roles from primary sources (official bios, repos, employer pages)",
            "Map catalyst tweet IDs to each identity node",
            "Tag each claim as verified/unverified before final narrative score",
        ],
    }

    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
