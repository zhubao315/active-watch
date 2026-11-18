"""Automated tests for the shared COROS quota ledger (reserve / reconcile).

Run: python3 -m unittest discover -s tests -p 'test_quota_lease.py' -v

No network and no GitHub token are used: the HTTP layer is replaced with an
in-memory fake that models the contents API's SHA-based optimistic locking.
"""

import argparse
import base64
import importlib.util
import io
import json
import os
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "tools" / "quota_lease.py"
)
spec = importlib.util.spec_from_file_location("quota_lease", MODULE_PATH)
quota = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quota)


class FakeGitHub:
    """Minimal in-memory stand-in for the GitHub contents API."""

    def __init__(self, ledger=None, conflicts=0, fail_put=False):
        self.ledger = ledger or {"days": {}}
        self.sha = "sha-0"
        self.conflicts = conflicts
        self.fail_put = fail_put
        self.puts = 0

    def __call__(self, url, payload=None, method="GET"):
        if method == "GET":
            return {
                "content": base64.b64encode(
                    json.dumps(self.ledger).encode()
                ).decode(),
                "sha": self.sha,
            }
        self.puts += 1
        if self.fail_put:
            raise OSError("network down")
        if self.conflicts > 0:
            self.conflicts -= 1
            raise urllib.error.HTTPError(url, 409, "conflict", {}, None)
        if payload.get("sha") != self.sha:
            raise urllib.error.HTTPError(url, 409, "sha mismatch", {}, None)
        self.ledger = json.loads(base64.b64decode(payload["content"]))
        self.sha = f"sha-{self.puts}"
        return {}


class QuotaLedgerTests(unittest.TestCase):
    def setUp(self):
        self.real_token = quota.token
        self.real_gh = quota.gh_json
        quota.token = lambda: "fake-token"
        self.fake = FakeGitHub()
        quota.gh_json = self.fake
        self.today = quota.utc_today()

    def tearDown(self):
        quota.token = self.real_token
        quota.gh_json = self.real_gh

    def reserve(self, repo, want=10, cap=45):
        args = argparse.Namespace(repo=repo, want=want, cap=cap)
        out = io.StringIO()
        with redirect_stdout(out):
            quota.cmd_reserve(args)
        return out.getvalue().strip()

    def reconcile(self, repo, used):
        args = argparse.Namespace(repo=repo, used=used)
        with redirect_stdout(io.StringIO()):
            quota.cmd_reconcile(args)

    def day(self):
        return self.fake.ledger["days"].get(self.today, {})

    def test_three_sites_reserve_without_double_allocating(self):
        self.reserve("running", 10)
        self.reserve("cycling", 10)
        self.reserve("hiking", 10)
        day = self.day()
        self.assertEqual(day["running"], 10)
        self.assertEqual(day["cycling"], 10)
        self.assertEqual(day["hiking"], 10)
        self.assertLessEqual(sum(day.values()), quota.DAILY_TOTAL)

    def test_late_site_is_converged_to_remaining_allowance(self):
        self.fake.ledger = {"days": {self.today: {"running": 20, "cycling": 20}}}
        self.reserve("hiking", 10)
        self.assertEqual(self.day()["hiking"], 10)  # 50 - 40 = 10

        self.fake.ledger = {"days": {self.today: {"running": 30, "cycling": 15}}}
        self.reserve("hiking", 10)
        self.assertEqual(self.day()["hiking"], 5)  # 50 - 45 = 5, capped by want

    def test_reconcile_hands_unused_share_back(self):
        self.reserve("running", 10)
        self.reconcile("running", 3)
        self.assertEqual(self.day()["running"], 3)

    def test_sha_conflict_is_retried_not_double_counted(self):
        self.fake.conflicts = 2
        self.reserve("running", 10)
        self.assertEqual(self.day()["running"], 10)
        self.assertEqual(self.fake.puts, 3)  # two conflicts + one success

    def test_network_failure_falls_back_without_corrupting_ledger(self):
        self.fake.fail_put = True
        allow = self.reserve("running", 10)
        self.assertEqual(allow, str(quota.FALLBACK_ALLOW))
        self.assertEqual(self.day(), {})  # nothing was recorded

    def test_without_token_ledger_is_read_only(self):
        quota.token = lambda: None
        allow = self.reserve("running", 10)
        self.assertEqual(allow, str(quota.FALLBACK_ALLOW))
        self.assertEqual(self.fake.puts, 0)
        self.assertEqual(self.day(), {})

    def test_reconcile_never_inflates_reservation(self):
        self.fake.ledger = {"days": {self.today: {"running": 4}}}
        self.reconcile("running", 9)
        self.assertEqual(self.day()["running"], 4)

    def test_reconcile_on_empty_day_records_actual_use(self):
        self.reconcile("hiking", 6)
        self.assertEqual(self.day()["hiking"], 6)

    def test_ledger_prunes_old_days(self):
        old = quota.utc_today(-10)
        self.fake.ledger = {"days": {old: {"running": 5}}}
        self.reserve("running", 10)
        self.assertNotIn(old, self.fake.ledger["days"])
        self.assertIn(self.today, self.fake.ledger["days"])


if __name__ == "__main__":
    unittest.main()
