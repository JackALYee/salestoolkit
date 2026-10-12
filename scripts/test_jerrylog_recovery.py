"""Jerry Log reconnects after idle/disrupted DB sessions and reports real outages.

Run: python3 scripts/test_jerrylog_recovery.py (no network or live data required).
"""
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["AUTH_SECRET"] = "jerrylog-recovery-test-only"
import server as S
import chat_history as H
from fastapi.testclient import TestClient


def healthy_connection(query):
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    if query == "log_stats":
        cur.fetchone.return_value = (1, 1, 1, None, None, 0, 0)
        cur.fetchall.return_value = []
    elif query == "log_filters":
        cur.fetchall.side_effect = [[("review-test@streamax.com",)], [("test-model",)]]
    else:
        cur.fetchone.return_value = (1,)
        cur.fetchall.return_value = [
            (1, datetime(2026, 10, 12, tzinfo=timezone.utc), "review-test@streamax.com",
             "test-session", "Test question", "Test answer", "test-model", False, False, 0)
        ]
    return conn


class RecoveryTests(unittest.TestCase):
    def test_closed_and_dropped_connections_retry_every_portal_read(self):
        for name in ("log_search", "log_stats", "log_filters"):
            for failure in (H.psycopg2.InterfaceError, H.psycopg2.OperationalError):
                for stage in ("cursor", "execute"):
                    with self.subTest(query=name, failure=failure.__name__, stage=stage):
                        stale = MagicMock()
                        if stage == "cursor":
                            stale.cursor.side_effect = failure("connection closed")
                        else:
                            stale.cursor.return_value.__enter__.return_value.execute.side_effect = failure("connection dropped")
                        fresh = healthy_connection(name)
                        with patch.object(H, "_get_connection", return_value=stale), \
                             patch.object(H, "_retry_get_connection", return_value=fresh) as retry:
                            result = getattr(H, name)()
                        retry.assert_called_once()
                        if name == "log_search":
                            self.assertEqual(result["rows"][0]["answer"], "Test answer")
                        elif name == "log_stats":
                            self.assertEqual(result["questions"], 1)
                        else:
                            self.assertEqual(result["users"], ["review-test@streamax.com"])

    def test_cached_failed_connection_is_retried(self):
        with patch.object(H, "_get_connection", return_value=None), \
             patch.object(H, "_retry_get_connection", return_value=healthy_connection("log_search")):
            self.assertEqual(H.log_search()["total"], 1)

    def test_reconnect_clears_a_cached_none(self):
        # Use the real cache and reconnect helper: a transient connection
        # failure must not remain cached for the lifetime of the server.
        H._get_connection.clear()
        fresh = healthy_connection("log_search")
        with patch.object(H, "_get_db_url", return_value="postgresql://test-only"), \
             patch.object(H, "_init_schema"), \
             patch.object(H.psycopg2, "connect", side_effect=[H.psycopg2.OperationalError("offline"), fresh]) as connect:
            try:
                self.assertEqual(H.log_search()["total"], 1)
                self.assertEqual(connect.call_count, 2)
            finally:
                H._get_connection.clear()

    def test_failed_retry_never_returns_an_empty_success(self):
        for name in ("log_search", "log_stats", "log_filters"):
            for failure in (None, H.psycopg2.InterfaceError, H.psycopg2.OperationalError):
                with self.subTest(query=name, failure=failure):
                    conn = None
                    if failure:
                        conn = MagicMock()
                        conn.cursor.side_effect = failure("offline")
                    with patch.object(H, "_get_connection", return_value=conn), \
                         patch.object(H, "_retry_get_connection", return_value=conn) as retry:
                        with self.assertRaises(H.LogUnavailable):
                            getattr(H, name)()
                        retry.assert_called_once()

    def test_non_connection_errors_are_not_retried_or_leaked(self):
        broken = MagicMock()
        broken.cursor.side_effect = H.psycopg2.ProgrammingError("private database details")
        with patch.object(H, "_get_connection", return_value=broken), \
             patch.object(H, "_retry_get_connection") as retry:
            with self.assertRaises(H.LogUnavailable) as error:
                H.log_search()
            self.assertNotIn("private", str(error.exception))
            retry.assert_not_called()

    def test_all_data_routes_return_json_503_on_outage(self):
        with TestClient(S.app) as client, \
             patch.object(S, "_history_on", return_value=True), \
             patch.object(H, "_get_connection", return_value=None), \
             patch.object(H, "_retry_get_connection", return_value=None):
            client.cookies.set(S.COOKIE_NAME, S.make_token("jimmy@streamax.com"))
            for route in ("/api/jerrylog", "/api/jerrylog/meta", "/api/jerrylog/export"):
                with self.subTest(route=route):
                    result = client.get(route)
                    self.assertEqual(result.status_code, 503)
                    self.assertIn("temporarily unavailable", result.json()["error"])
                    self.assertEqual(result.headers["retry-after"], "5")

    def test_search_filters_survive_retry(self):
        fresh = healthy_connection("log_search")
        with patch.object(H, "_get_connection", return_value=None), \
             patch.object(H, "_retry_get_connection", return_value=fresh):
            H.log_search(q="fleet", user="review-test@streamax.com", since="2026-10-12",
                         until="2026-10-12", only_sensitive=True, limit=10, offset=20)
        cur = fresh.cursor.return_value.__enter__.return_value
        args = cur.execute.call_args.args[1]
        self.assertEqual(args, ["%fleet%", "%fleet%", "review-test@streamax.com",
                                "2026-10-12", "2026-10-12", 10, 20])


if __name__ == "__main__":
    unittest.main(verbosity=2)
