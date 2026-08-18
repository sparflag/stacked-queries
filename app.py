#!/usr/bin/env python3
"""Stacked Queries — real mini-challenge (stacked-queries)."""
import base64, hashlib, hmac, json, os, re, sqlite3, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote, quote

sys.path.insert(0, "/challenge/_shared")
from fetch_material import fetch_material

CHALLENGE_KEY = os.environ.get("CHALLENGE_KEY", 'stack-then-select')
_MAT = {}

DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.execute("CREATE TABLE products(name TEXT)")
DB.execute("INSERT INTO products VALUES('apple')")
DB.execute("CREATE TABLE vault(k TEXT)")
DB.execute("INSERT INTO vault VALUES(?)", (CHALLENGE_KEY,))
DB.execute("CREATE TABLE secrets(k TEXT)")
DB.commit()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/plain", headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        data = body if isinstance(body, bytes) else body.encode()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


    def do_GET(self):
        p = urlparse(self.path); qs = parse_qs(p.query)
        if p.path == "/flag":
            return self._send(200, _MAT.get("delivery_blob", "") + "\n")
        if p.path == "/q":
            name = qs.get("name", ["apple"])[0]
            # sqlite3 default allows only one statement — emulate stacked via split
            parts = [x.strip() for x in name.split(";") if x.strip()]
            out = []
            for part in parts:
                if part.upper().startswith("SELECT"):
                    q = part
                else:
                    q = f"SELECT name FROM products WHERE name='{part}'"
                try:
                    if q.upper().startswith("INSERT") or q.upper().startswith("UPDATE"):
                        DB.execute(q); DB.commit(); out.append("ok")
                    else:
                        rows = DB.execute(q).fetchall(); out.append(str(rows))
                except Exception as exc:
                    out.append(f"err:{exc}")
            return self._send(200, "\n".join(out) + "\n")
        if p.path == "/secrets":
            rows = DB.execute("SELECT k FROM secrets").fetchall()
            return self._send(200, str(rows) + "\n")
        self._send(200, "Stacked: /q?name=apple  /secrets  /flag\n")


def main():
    _MAT.update(fetch_material())
    print('Stacked Queries on :8080')
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

if __name__ == "__main__":
    main()
