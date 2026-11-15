"""The donations API of Ghilal Food Bank Network, as a small local server. Standard library only.

    uv run python donations_api.py            # serves on http://127.0.0.1:8765 until Ctrl+C

    GET /v1/donations?page=1&per_page=200     # {"page", "per_page", "total", "next", "data": [...]}

It behaves like the real thing in three ways the labs rely on:
- records are served in pages, oldest first, and `total` is the number of distinct donations;
- donations kept arriving while the extract was paged, so some pages begin with records the page
  before already ended with (the same donation_id twice);
- the first request for page 5 answers 503 once: the service was busy.
"""

from __future__ import annotations

import gzip
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

OVERLAP = {9: 3, 14: 2, 17: 4, 22: 3}   # page number: how many records of the page before it repeats


def make_server(path: Path, port: int = 0) -> ThreadingHTTPServer:
    rows = [json.loads(line) for line in gzip.open(path, "rt", encoding="utf-8")]
    state = {"busy_once": True}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):   # quiet
            pass

        def _send(self, code: int, body: dict):
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            u = urlparse(self.path)
            if u.path != "/v1/donations":
                return self._send(404, {"error": "not found"})
            q = parse_qs(u.query)
            page = int(q.get("page", ["1"])[0])
            per = min(int(q.get("per_page", ["200"])[0]), 200)
            if page == 5 and state["busy_once"]:
                state["busy_once"] = False
                return self._send(503, {"error": "busy, try again"})
            start = max(0, (page - 1) * per - (OVERLAP.get(page, 0) if per == 200 else 0))
            data = rows[start:page * per]
            nxt = f"/v1/donations?page={page + 1}&per_page={per}" if page * per < len(rows) else None
            self._send(200, {"page": page, "per_page": per, "total": len(rows), "next": nxt, "data": data})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    server = make_server(here / "data" / "raw" / "donations" / "donations.jsonl.gz", 8765)
    print("donations API on http://127.0.0.1:8765/v1/donations (Ctrl+C stops it)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
