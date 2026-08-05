#!/usr/bin/env python3
"""Självtest för bokio_fetch: sidbrytning och rate limit-hantering.

    python3 test_bokio_fetch.py
"""
import email.message, json, os, urllib.error, urllib.request

os.environ.setdefault("BOKIO_TOKEN", "x")
os.environ.setdefault("BOKIO_COMPANY_ID", "c")
import bokio_fetch as b

b.MIN_INTERVAL = 0
slept = []
b.time.sleep = lambda s: slept.append(round(s, 2))


def hdrs(d):
    m = email.message.Message()
    for k, v in d.items():
        m[k] = v
    return m


class Resp:
    def __init__(self, data, headers=None):
        self.d, self.headers = json.dumps(data).encode(), hdrs(headers or {})

    def read(self):
        return self.d

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


def serve(seq):
    def fake(req):
        assert req.headers["Authorization"] == "Bearer x"
        x = seq.pop(0)
        if isinstance(x, Exception):
            raise x
        return x

    urllib.request.urlopen = fake


def err(code, headers=None):
    return urllib.error.HTTPError("u", code, "m", hdrs(headers or {}), None)


# Sidbrytningen följs och slås ihop.
serve([Resp({"result": [1, 2], "totalPages": 2}), Resp({"result": [3], "totalPages": 2})])
assert b.get_all("journal-entries") == [1, 2, 3]

# Opaginerad resurs returneras som den är.
serve([Resp([{"account": 1930}])])
assert b.get_all("chart-of-accounts") == [{"account": 1930}]

# 429 med RetryAfter: vänta precis så länge huvudet säger.
slept.clear()
serve([err(429, {"Bokio-RateLimit-RetryAfter": "7"}), Resp({"ok": 1})])
assert b.get("p") == {"ok": 1} and 7 in slept, slept

# 429/409 utan huvuden är samtidighetsspärren: exponentiell backoff.
slept.clear()
serve([err(429), err(409), Resp({"ok": 2})])
assert b.get("p") == {"ok": 2} and [s for s in slept if s] == [1, 2], slept

# Nära taket: vänta ut fönstret innan nästa anrop.
slept.clear()
serve([Resp({"ok": 3}, {"Bokio-RateLimit-Remaining": "3", "Bokio-RateLimit-RetryAfter": "42"})])
assert b.get("p") == {"ok": 3} and 42 in slept, slept

print("ok")
