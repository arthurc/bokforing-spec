#!/usr/bin/env python3
"""Serverar fixtures/ som om det vore Bokios Company API.

    python3 make_fixtures.py
    python3 serve_fixtures.py &        # lyssnar på 8731
    export BOKIO_API_BASE=http://127.0.0.1:8731/v1
    export BOKIO_TOKEN=fixture BOKIO_COMPANY_ID=ea9ee4dd-fae3-4aec-a7db-6fc9cc1f8135

Kräver Authorization-huvudet så att steg 0 i skillen beter sig som skarpt,
och sätter rate limit-huvudena så att strypningen i bokio_fetch går att se.
"""
import http.server, json, pathlib, sys, urllib.parse

ROOT = pathlib.Path(__file__).parent / "fixtures"
PREFIX = "/v1/companies/"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Bokio-RateLimit-Limit", "200")
        self.send_header("Bokio-RateLimit-Remaining", "199")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def fail(self, code, msg):
        self.send(code, json.dumps({"code": msg, "message": msg}).encode())

    def do_GET(self):
        if not self.headers.get("Authorization", "").startswith("Bearer "):
            return self.fail(401, "unauthorized")
        path = urllib.parse.urlparse(self.path).path
        if not path.startswith(PREFIX):
            return self.fail(404, "not-found")
        rest = path[len(PREFIX):].split("/", 1)
        if len(rest) < 2:
            return self.fail(404, "not-found")
        resource = rest[1].strip("/")
        # /uploads/{id}/download och /sie/{id}/download är binära.
        for cand, ctype in ((ROOT / f"{resource}.json", "application/json"),
                            (ROOT / f"{resource}.bin", "application/octet-stream")):
            if cand.is_file():
                return self.send(200, cand.read_bytes(), ctype)
        self.fail(404, "not-found")


if __name__ == "__main__":
    if not ROOT.is_dir():
        sys.exit("Kör make_fixtures.py först.")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8731
    print(f"fixture-API på http://127.0.0.1:{port}/v1", flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
