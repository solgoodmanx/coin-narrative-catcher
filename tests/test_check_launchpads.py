import importlib.util
import unittest
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = repo_root / "scripts" / "check_launchpads.py"
    spec = importlib.util.spec_from_file_location("check_launchpads", mod_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class TestCheckLaunchpads(unittest.TestCase):
    def test_bankr_primary_with_doppler_secondary(self):
        mod = _load_module()
        ca = "0xabc"

        def fake_json(url):
            if "api2.virtuals.io" in url:
                return 200, {"data": []}
            if "clanker.world" in url:
                return 200, {"data": []}
            if "api.bankr.bot" in url:
                return 200, {
                    "launch": {
                        "tokenName": "Test",
                        "tokenSymbol": "TST",
                        "deployer": {"walletAddress": "0x1", "xUsername": "dev"},
                        "feeRecipient": {"walletAddress": "0x2", "xUsername": "fees"},
                    }
                }
            if "api.dexscreener.com" in url:
                return 200, {"pairs": []}
            if "app.doppler.lol/api/search" in url:
                return 200, [{"address": ca}]
            raise AssertionError(f"Unexpected URL: {url}")

        def fake_text(url):
            return 200, "<title>$TST | Doppler</title>"

        out = mod.classify_launchpad(ca, json_fetcher=fake_json, text_fetcher=fake_text)
        self.assertEqual(out["classification"], "bankr")
        self.assertEqual(out["confidenceTier"], "exact")
        self.assertTrue(out["bankr"]["match"])
        self.assertTrue(out["doppler"]["match"])
        self.assertIn("doppler", out["alsoIndexedOn"])

    def test_flaunch_heuristic_when_only_fleth_pair_matches(self):
        mod = _load_module()

        def fake_json(url):
            if "api2.virtuals.io" in url:
                return 200, {"data": []}
            if "clanker.world" in url:
                return 200, {"data": []}
            if "api.bankr.bot" in url:
                return 404, {"error": "Token not found"}
            if "api.dexscreener.com" in url:
                return 200, {
                    "pairs": [
                        {
                            "pairAddress": "0xp",
                            "dexId": "uniswap",
                            "chainId": "base",
                            "quoteToken": {"address": "0x000000000d564d5be76f7f0d28fe52605afc7cf8"},
                        }
                    ]
                }
            if "app.doppler.lol/api/search" in url:
                return 200, []
            raise AssertionError(f"Unexpected URL: {url}")

        def fake_text(url):
            return 404, "not found"

        out = mod.classify_launchpad("0xdef", json_fetcher=fake_json, text_fetcher=fake_text)
        self.assertEqual(out["classification"], "flaunch")
        self.assertEqual(out["confidenceTier"], "heuristic")
        self.assertTrue(out["flaunch"]["match"])
        self.assertEqual(out["flaunch"]["flETH"], "0x000000000d564d5be76f7f0d28fe52605afc7cf8")

    def test_unattributed_when_no_signals(self):
        mod = _load_module()

        def fake_json(url):
            if "app.doppler.lol/api/search" in url:
                return 200, []
            if "api.bankr.bot" in url:
                return 404, {"error": "Token not found"}
            return 200, {"data": []}

        def fake_text(url):
            return 404, ""

        out = mod.classify_launchpad("0x123", json_fetcher=fake_json, text_fetcher=fake_text)
        self.assertEqual(out["classification"], "unattributed")
        self.assertEqual(out["confidenceTier"], "none")


if __name__ == "__main__":
    unittest.main()
