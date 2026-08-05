#!/usr/bin/env python3
"""Hämta data ur Bokios Company API. Läser BOKIO_TOKEN och BOKIO_COMPANY_ID
ur miljön; skriver JSON till stdout, eller binärt till --out.

    bokio_fetch.py chart-of-accounts
    bokio_fetch.py journal-entries --query 'date>=2026-01-01'
    bokio_fetch.py uploads/<uploadId>/download --out archive/kvitton/2026/x.pdf
    bokio_fetch.py sie/<fiscalYearId>/download --out archive/import/2026.se

Sidbrytning (result/totalPages) följs automatiskt och slås ihop till en lista.
Anropen strypas till ~3/s och backar av på 429/409/500 — kör inte flera
instanser av skriptet parallellt, då gäller strypningen per process och
budgeten (200 req/60 s) räknas per token.
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

# BOKIO_API_BASE finns för att kunna köra mot en fixture-server i tester.
# Lämna den osatt mot skarpa Bokio.
BASE = os.environ.get("BOKIO_API_BASE", "https://api.bokio.se/v1") + "/companies"
# Bokio tillåter 200 requests per rullande 60 s per token, dvs 3,33/s.
# Vi går medvetet under: en import ska inte äta hela budgeten.
MIN_INTERVAL = 0.35
_last_call = 0.0


def get(path, query=None, raw=False):
    global _last_call
    token, company = os.environ.get("BOKIO_TOKEN"), os.environ.get("BOKIO_COMPANY_ID")
    if not token or not company:
        sys.exit("Sätt BOKIO_TOKEN och BOKIO_COMPANY_ID i miljön.")
    url = f"{BASE}/{company}/{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    for attempt in range(6):
        time.sleep(max(0, _last_call + MIN_INTERVAL - time.time()))
        _last_call = time.time()
        try:
            with urllib.request.urlopen(req) as r:
                body = r.read()
                left = r.headers.get("Bokio-RateLimit-Remaining")
                # Nära taket: vänta ut fönstret hellre än att gå i 429.
                if left is not None and int(left) < 10:
                    wait = int(r.headers.get("Bokio-RateLimit-RetryAfter") or 60)
                    print(f"rate limit: {left} kvar, väntar {wait}s", file=sys.stderr)
                    time.sleep(wait)
                return body if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code in (429, 409, 500) and attempt < 5:
                # 429 med RetryAfter = rate limit. 429 utan, 409 och 500 kommer
                # från samtidighetsspärren, som inte sätter huvudena alls.
                after = e.headers.get("Bokio-RateLimit-RetryAfter")
                wait = int(after) if after else 2**attempt
                print(f"{e.code}, försöker igen om {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            sys.exit(f"{e.code} {url}\n{e.read().decode(errors='replace')}")


def get_all(path, query=None):
    """Följer sidbrytningen och returnerar hela result-listan."""
    q = dict(query or {})
    q["pageSize"] = 100
    page, out = 1, []
    while True:
        q["page"] = page
        data = get(path, q)
        if not isinstance(data, dict) or "result" not in data:
            return data  # opaginerad resurs, t.ex. chart-of-accounts
        out += data["result"]
        if page >= (data.get("totalPages") or 1):
            return out
        page += 1


def main(argv):
    if not argv:
        sys.exit(__doc__)
    path, query, out = argv[0], {}, None
    i = 1
    while i < len(argv):
        if argv[i] == "--query":
            query["query"] = argv[i + 1]
        elif argv[i] == "--out":
            out = argv[i + 1]
        else:
            sys.exit(f"okänd flagga: {argv[i]}")
        i += 2
    if out:
        data = get(path, query, raw=True)
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "wb") as f:
            f.write(data)
        print(f"{out} ({len(data)} bytes)")
    else:
        json.dump(get_all(path, query), sys.stdout, ensure_ascii=False, indent=2)
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
