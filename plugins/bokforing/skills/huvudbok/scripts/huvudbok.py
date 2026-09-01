#!/usr/bin/env python3
"""Bygg en huvudbok för en period som fristående HTML ur en accounting bundle.

    python3 huvudbok.py <bundle-rot> --from 2026-01-01 --to 2026-12-31 [--out fil.html]

Läser kontoplanen, räkenskapsårens ingående balanser och samtliga
verifikationers `# Postings` och skriver ut varje konto som har belopp med
namn, ingående balans, utgående balans och de verifikationer som ligger bakom.

Teckenkonvention: debet positivt, kredit negativt — samma som `# Opening
Balances` i SPEC §4.3, där ett kreditsaldo (t.ex. eget kapital) står negativt.

    python3 huvudbok.py --selftest    kör en inbyggd kontroll
"""

import argparse
import datetime
import html
import re
import sys
from decimal import Decimal
from pathlib import Path

ZERO = Decimal("0")


# --- inläsning ---------------------------------------------------------------


def read_concept(path):
    """Returnera (frontmatter-dict, body) för en markdown-fil med YAML-header."""
    text = path.read_text(encoding="utf-8")
    fm = {}
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
                if m:
                    fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
            body = text[text.find("\n", end + 1) + 1 :]
    return fm, body


def table_rows(body, heading):
    """Raderna i markdown-tabellen under `# <heading>`, som listor av celler."""
    m = re.search(
        r"^#+\s*%s\s*$(.*?)(?=^#+\s|\Z)" % re.escape(heading),
        body,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def columns(rows, *names):
    """Index för namngivna kolumner ur tabellens huvudrad, plus datarader."""
    if not rows:
        return None, []
    header = [c.lower() for c in rows[0]]
    idx = []
    for name in names:
        hits = [i for i, c in enumerate(header) if name in c]
        if not hits:
            return None, []
        idx.append(hits[0])
    return idx, rows[1:]


def parse_amount(cell):
    """'-1 234,56 SEK' -> Decimal('-1234.56'). Tom cell -> None."""
    s = re.sub(r"[^\d,.\-+]", "", cell.replace(" ", "").replace("−", "-"))
    if not s or s in "-+":
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rindex(",") > s.rindex(".") else s.replace(",", "")
    else:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except Exception:
        return None


def parse_account(cell):
    """'1930 Företagskonto' -> ('1930', 'Företagskonto')."""
    m = re.match(r"\s*\[?(\d{3,6})\]?\s*(.*?)\s*$", cell)
    return (m.group(1), m.group(2)) if m else (None, None)


def parse_date(value):
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def load_bundle(root):
    """Läs kontoplan, organisation, räkenskapsår och verifikationer."""
    accounts, org, years, verifications = {}, {}, [], []

    for path in sorted(root.rglob("*.md")):
        if "/archive/" in "/" + str(path.relative_to(root)):
            continue
        fm, body = read_concept(path)
        kind = fm.get("type")

        if kind == "Chart of Accounts":
            idx, rows = columns(table_rows(body, "Accounts"), "account")
            for row in rows:
                number, name = parse_account(row[idx[0]])
                if number:
                    accounts[number] = name or (row[idx[0] + 1] if len(row) > idx[0] + 1 else "")

        elif kind == "Organization":
            org = fm

        elif kind == "Fiscal Year":
            start, end = parse_date(fm.get("start_date")), parse_date(fm.get("end_date"))
            if not (start and end):
                continue
            opening = {}
            idx, rows = columns(table_rows(body, "Opening Balances"), "account", "balance")
            for row in rows:
                number, name = parse_account(row[idx[0]])
                amount = parse_amount(row[idx[1]]) if len(row) > idx[1] else None
                if number and amount is not None:
                    opening[number] = opening.get(number, ZERO) + amount
                    accounts.setdefault(number, name or "")
            years.append({"id": fm.get("fiscal_year_id", path.stem), "start": start,
                          "end": end, "opening": opening})

        elif kind == "Verification":
            date = parse_date(fm.get("transaction_date"))
            if not date:
                continue
            postings = []
            idx, rows = columns(table_rows(body, "Postings"), "account", "debit", "credit")
            for row in rows:
                number, name = parse_account(row[idx[0]])
                if not number:
                    continue
                debit = parse_amount(row[idx[1]]) if len(row) > idx[1] else None
                credit = parse_amount(row[idx[2]]) if len(row) > idx[2] else None
                postings.append({"account": number, "debit": debit or ZERO, "credit": credit or ZERO})
                accounts.setdefault(number, name or "")
            verifications.append({
                "number": fm.get("verification_number", path.stem),
                "date": date,
                "description": fm.get("description") or fm.get("title") or "",
                "path": str(path.relative_to(root)),
                "postings": postings,
            })

    verifications.sort(key=lambda v: (v["date"], v["number"]))
    return accounts, org, years, verifications


# --- beräkning ---------------------------------------------------------------


def build_ledger(accounts, years, verifications, start, end):
    """Ingående balans, periodens rader och utgående balans per konto."""
    fy = next((y for y in years if y["start"] <= start <= y["end"]), None)
    ib_from = fy["start"] if fy else datetime.date.min
    ledger = {}

    def entry(number):
        return ledger.setdefault(
            number,
            {"number": number, "name": accounts.get(number, ""), "ib": ZERO, "rows": [], "ub": ZERO},
        )

    if fy:
        for number, amount in fy["opening"].items():
            entry(number)["ib"] += amount

    for v in verifications:
        for p in v["postings"]:
            net = p["debit"] - p["credit"]
            if ib_from <= v["date"] < start:
                entry(p["account"])["ib"] += net
            elif start <= v["date"] <= end:
                acct = entry(p["account"])
                acct["rows"].append({**v, **p, "net": net})

    for acct in ledger.values():
        acct["ub"] = acct["ib"] + sum(r["net"] for r in acct["rows"])

    return (
        fy,
        sorted(
            (a for a in ledger.values() if a["ib"] or a["ub"] or a["rows"]),
            key=lambda a: a["number"],
        ),
    )


# --- rendering ---------------------------------------------------------------


def kr(amount):
    """Decimal -> '−1 234,56' med tunt mellanslag som tusentalsavskiljare."""
    if amount is None:
        return ""
    sign = "−" if amount < 0 else ""
    whole, _, frac = f"{abs(amount):.2f}".partition(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    return sign + " ".join(groups) + "," + frac


def render(org, fy, accounts, start, end):
    e = html.escape
    company = org.get("title", "Huvudbok")
    period = f"{start.isoformat()} – {end.isoformat()}"
    total_ib = sum(a["ib"] for a in accounts)
    total_ub = sum(a["ub"] for a in accounts)
    verifications = {r["number"] for a in accounts for r in a["rows"]}

    def cell(amount):
        cls = " neg" if amount < 0 else (" nil" if amount == 0 else "")
        return f'<span class="num{cls}">{kr(amount)}</span>'

    rows = []
    for a in accounts:
        change = a["ub"] - a["ib"]
        lines = "".join(
            f'<tr><td class="d">{r["date"].isoformat()}</td>'
            f'<td class="v">{e(str(r["number"]))}</td>'
            f'<td class="t">{e(r["description"])}</td>'
            f'<td class="a">{kr(r["debit"]) if r["debit"] else ""}</td>'
            f'<td class="a">{kr(r["credit"]) if r["credit"] else ""}</td></tr>'
            for r in a["rows"]
        )
        detail = (
            '<table class="lines"><thead><tr><th>Datum</th><th>Ver</th>'
            "<th>Beskrivning</th><th>Debet</th><th>Kredit</th></tr></thead>"
            f"<tbody>{lines}</tbody></table>"
            if lines
            else '<p class="empty">Inga verifikationer i perioden — saldot är oförändrat sedan ingående balans.</p>'
        )
        rows.append(
            '<details class="acct">'
            f'<summary><span class="no">{e(a["number"])}</span>'
            f'<span class="nm">{e(a["name"])}</span>'
            f'<span class="ct">{len(a["rows"]) or ""}</span>'
            f'<span class="ib">{cell(a["ib"])}</span>'
            f'<span class="ub">{cell(a["ub"])}</span>'
            f'<span class="ch">{cell(change)}</span></summary>'
            f'<div class="body">{detail}</div></details>'
        )

    balanced = total_ub == 0 and total_ib == 0
    check = (
        '<span class="ok">balanserar</span>'
        if balanced
        else f'<span class="warn">obalans {kr(total_ub)}</span>'
    )
    fy_note = (
        f'Ingående balans hämtad ur räkenskapsåret {e(str(fy["id"]))} '
        f'({fy["start"].isoformat()} – {fy["end"].isoformat()}) och ackumulerad fram till periodstart.'
        if fy
        else "Inget räkenskapsår täcker periodstarten — ingående balans är summan av alla "
        "verifikationer före perioden."
    )

    return f"""<meta charset="utf-8">
<title>Huvudbok {e(company)}</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{
  --paper: #f7f7f4; --sheet: #fffffd; --rule: #dfe0d8; --rule-soft: #ecece5;
  --ink: #1b1f1a; --ink-soft: #5f665c; --ink-faint: #8e948a;
  --accent: #3f6b52; --accent-soft: #e6efe8; --neg: #9c3b2c; --warn: #9c3b2c;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper: #14171400; --paper: #141714; --sheet: #1b1f1b; --rule: #2f352f; --rule-soft: #242924;
    --ink: #e6e9e3; --ink-soft: #a3aa9f; --ink-faint: #757c72;
    --accent: #8fc0a1; --accent-soft: #23301f; --neg: #dd9382; --warn: #dd9382;
  }}
}}
:root[data-theme="dark"] {{
  --paper: #141714; --sheet: #1b1f1b; --rule: #2f352f; --rule-soft: #242924;
  --ink: #e6e9e3; --ink-soft: #a3aa9f; --ink-faint: #757c72;
  --accent: #8fc0a1; --accent-soft: #23301f; --neg: #dd9382; --warn: #dd9382;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--paper); color: var(--ink);
  font: 400 15px/1.55 "Source Sans 3", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 68rem; margin: 0 auto; padding: 3rem 1.25rem 5rem; }}
header {{ display: flex; flex-direction: column; gap: .35rem; margin-bottom: 2rem; }}
.eyebrow {{
  font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
  letter-spacing: .14em; text-transform: uppercase; color: var(--accent);
}}
h1 {{
  font: 400 clamp(2rem, 4vw, 2.9rem)/1.1 Newsreader, Georgia, serif;
  margin: 0; text-wrap: balance;
}}
.period {{ font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--ink-soft); font-size: .95rem; }}
.facts {{
  display: flex; flex-wrap: wrap; gap: 1.75rem; margin: 1.5rem 0 2rem;
  padding: 1rem 1.25rem; background: var(--sheet); border: 1px solid var(--rule);
  border-radius: 3px;
}}
.fact {{ display: flex; flex-direction: column; gap: .1rem; }}
.fact dt {{
  font-size: .68rem; letter-spacing: .12em; text-transform: uppercase;
  color: var(--ink-faint); font-family: "IBM Plex Mono", ui-monospace, monospace;
}}
.fact dd {{ margin: 0; font-size: 1.15rem; font-variant-numeric: tabular-nums; }}
.ok {{ color: var(--accent); }}
.warn {{ color: var(--warn); font-weight: 600; }}
.note {{ color: var(--ink-soft); font-size: .88rem; max-width: 60ch; margin: 0 0 1.75rem; }}
.toolbar {{ display: flex; justify-content: flex-end; margin-bottom: .5rem; }}
button {{
  font: inherit; font-size: .82rem; color: var(--ink-soft); background: none; cursor: pointer;
  border: 1px solid var(--rule); border-radius: 3px; padding: .3rem .7rem;
}}
button:hover {{ color: var(--ink); border-color: var(--ink-faint); }}
button:focus-visible, summary:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.ledger {{ border: 1px solid var(--rule); border-radius: 3px; background: var(--sheet); overflow-x: auto; }}
.cols, summary, .sum {{
  display: grid; align-items: baseline; min-width: 38rem;
  grid-template-columns: 4.5rem minmax(5rem, 1fr) 2.5rem 7rem 7rem 7rem;
  gap: .75rem; padding: .5rem 1rem;
}}
.cols {{
  font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .68rem;
  letter-spacing: .12em; text-transform: uppercase; color: var(--ink-faint);
  border-bottom: 1px solid var(--rule); background: var(--paper);
}}
.cols span:nth-child(n+4), summary .ib, summary .ub, summary .ch {{ text-align: right; }}
.cols span:nth-child(3) {{ text-align: right; }}
summary {{ cursor: pointer; list-style: none; padding: .55rem 1rem; border-top: 1px solid var(--rule-soft); }}
.acct:first-of-type > summary {{ border-top: none; }}
summary::-webkit-details-marker {{ display: none; }}
summary:hover {{ background: var(--accent-soft); }}
details[open] > summary {{ background: var(--accent-soft); }}
.no {{
  font-family: "IBM Plex Mono", ui-monospace, monospace; font-weight: 500;
  color: var(--accent); position: relative;
}}
.no::before {{
  content: "▸"; position: absolute; left: -.85rem; color: var(--ink-faint); font-size: .7em;
}}
details[open] .no::before {{ content: "▾"; }}
.nm {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.ct {{ font-size: .75rem; color: var(--ink-faint); font-variant-numeric: tabular-nums; }}
.num {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-variant-numeric: tabular-nums; font-size: .9rem; }}
.num.neg {{ color: var(--neg); }}
.num.nil {{ color: var(--ink-faint); }}
.body {{ padding: .25rem 1rem 1rem 3rem; border-left: 2px solid var(--accent-soft); }}
table.lines {{ border-collapse: collapse; width: 100%; font-size: .88rem; }}
table.lines th {{
  text-align: left; font-weight: 400; font-size: .68rem; letter-spacing: .1em;
  text-transform: uppercase; color: var(--ink-faint); padding: .35rem .6rem .35rem 0;
  border-bottom: 1px solid var(--rule-soft);
  font-family: "IBM Plex Mono", ui-monospace, monospace;
}}
table.lines td {{ padding: .3rem .6rem .3rem 0; border-bottom: 1px solid var(--rule-soft); vertical-align: top; }}
table.lines tr:last-child td {{ border-bottom: none; }}
td.d, td.v {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .82rem; color: var(--ink-soft); white-space: nowrap; }}
th:nth-child(4), th:nth-child(5), td.a {{
  text-align: right; font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-variant-numeric: tabular-nums; white-space: nowrap; padding-right: 0;
}}
.empty {{ color: var(--ink-faint); font-size: .88rem; margin: .5rem 0; }}
.sum {{ padding: .7rem 1rem; border-top: 2px solid var(--rule); background: var(--paper); font-weight: 600; }}
.sum span:nth-child(n+4) {{ text-align: right; }}
footer {{ margin-top: 2rem; color: var(--ink-faint); font-size: .8rem; }}
@media (max-width: 760px) {{
  .cols, summary, .sum {{ min-width: 26rem; grid-template-columns: 3.8rem minmax(4rem, 1fr) 7rem 7rem; }}
  .cols span:nth-child(3), .ct, .cols span:nth-child(6), summary .ch,
  .sum span:nth-child(3), .sum span:nth-child(6) {{ display: none; }}
  .body {{ padding-left: 1rem; }}
  .wrap {{ padding-inline: .75rem; }}
}}
</style>
<div class="wrap">
<header>
  <span class="eyebrow">Huvudbok</span>
  <h1>{e(company)}</h1>
  <span class="period">{period}</span>
</header>

<dl class="facts">
  <div class="fact"><dt>Konton med belopp</dt><dd>{len(accounts)}</dd></div>
  <div class="fact"><dt>Verifikationer</dt><dd>{len(verifications)}</dd></div>
  <div class="fact"><dt>Balanskontroll</dt><dd>{check}</dd></div>
</dl>

<p class="note">{fy_note} Debet räknas positivt och kredit negativt, så ett
kreditsaldo står med minustecken. Klicka på ett konto för att se
verifikationerna bakom förändringen.</p>

<div class="toolbar"><button id="toggle" type="button">Expandera alla</button></div>

<div class="ledger">
  <div class="cols"><span>Konto</span><span>Benämning</span><span>Ver</span><span>Ingående</span><span>Utgående</span><span>Förändring</span></div>
  {"".join(rows) or '<p class="empty" style="padding:1rem">Inga konton med belopp i perioden.</p>'}
  <div class="sum"><span></span><span>Summa</span><span></span><span class="num">{kr(total_ib)}</span><span class="num">{kr(total_ub)}</span><span class="num">{kr(total_ub - total_ib)}</span></div>
</div>

<footer>Genererad ur bundlens verifikationer, kontoplan och räkenskapsår enligt
Accounting Knowledge Bundle Specification §4.2, §4.3 och §4.10.</footer>
</div>
<script>
const btn = document.getElementById("toggle");
btn.addEventListener("click", () => {{
  const open = btn.textContent.startsWith("Expandera");
  document.querySelectorAll("details.acct").forEach(d => d.open = open);
  btn.textContent = open ? "Fäll ihop alla" : "Expandera alla";
}});
</script>
"""


# --- kontroll ----------------------------------------------------------------


def selftest():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "verifications" / "2026").mkdir(parents=True)
        (root / "fiscal-years").mkdir()
        (root / "chart-of-accounts.md").write_text(
            "---\ntype: Chart of Accounts\n---\n\n# Accounts\n\n"
            "| Account | Account Name |\n| --- | --- |\n"
            "| 1930 | Företagskonto |\n| 6110 | Kontorsmaterial |\n",
            encoding="utf-8",
        )
        (root / "organization.md").write_text(
            "---\ntype: Organization\ntitle: Testbolaget AB\n---\n", encoding="utf-8"
        )
        (root / "fiscal-years" / "2026.md").write_text(
            "---\ntype: Fiscal Year\nfiscal_year_id: \"2026\"\n"
            "start_date: 2026-01-01\nend_date: 2026-12-31\nstatus: open\n---\n\n"
            "# Opening Balances\n\n| Account | Balance |\n| --- | ---: |\n"
            "| 1930 Företagskonto | 10 000,00 SEK |\n"
            "| 2091 Balanserad vinst | -10 000,00 SEK |\n",
            encoding="utf-8",
        )
        for num, day, amount in [("V1", "2026-02-10", "400.00"), ("V2", "2026-05-20", "1 250,00")]:
            (root / "verifications" / "2026" / f"{num}.md").write_text(
                f"---\ntype: Verification\nverification_number: \"{num}\"\n"
                f"transaction_date: {day}\nrecorded_date: {day}\n"
                f"description: Inköp kontorsmaterial\namount: {amount} SEK\n"
                "counterparty: Kontorsvaruhuset AB\n---\n\n# Postings\n\n"
                "| Account | Debit | Credit |\n| --- | --- | --- |\n"
                f"| 6110 Kontorsmaterial | {amount} | |\n"
                f"| 1930 Företagskonto | | {amount} |\n",
                encoding="utf-8",
            )

        accounts, org, years, vers = load_bundle(root)
        assert accounts["6110"] == "Kontorsmaterial", accounts
        assert org["title"] == "Testbolaget AB"
        assert len(vers) == 2 and vers[0]["number"] == "V1"

        # Perioden april–december: V1 (februari) ska ligga i ingående balans.
        fy, ledger = build_ledger(
            accounts, years, vers, datetime.date(2026, 4, 1), datetime.date(2026, 12, 31)
        )
        by = {a["number"]: a for a in ledger}
        assert fy["id"] == "2026"
        assert by["1930"]["ib"] == Decimal("9600.00"), by["1930"]["ib"]
        assert by["6110"]["ib"] == Decimal("400.00")
        assert by["1930"]["ub"] == Decimal("8350.00"), by["1930"]["ub"]
        assert by["6110"]["ub"] == Decimal("1650.00")
        assert [r["number"] for r in by["6110"]["rows"]] == ["V2"]
        assert by["2091"]["ib"] == by["2091"]["ub"] == Decimal("-10000.00")
        assert sum(a["ub"] for a in ledger) == ZERO, "dubbel bokföring ska summera till noll"

        # Hela året: allt ligger i perioden, ingen ingående kostnad.
        _, ledger = build_ledger(
            accounts, years, vers, datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)
        )
        by = {a["number"]: a for a in ledger}
        assert by["6110"]["ib"] == ZERO and by["6110"]["ub"] == Decimal("1650.00")
        assert len(by["1930"]["rows"]) == 2

        page = render(org, fy, ledger, datetime.date(2026, 1, 1), datetime.date(2026, 12, 31))
        assert "Testbolaget AB" in page and "1 650,00" in page and "balanserar" in page
        assert kr(Decimal("-1234567.5")) == "−1 234 567,50"

    print("selftest ok")


# --- cli ---------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description="Bygg en huvudbok som HTML ur en accounting bundle.")
    ap.add_argument("bundle", nargs="?", default=".", help="sökväg till bundle-roten")
    ap.add_argument("--from", dest="start", help="periodens första dag, ISO 8601")
    ap.add_argument("--to", dest="end", help="periodens sista dag, ISO 8601")
    ap.add_argument("--out", help="fil att skriva HTML till (default: huvudbok-<från>-<till>.html)")
    ap.add_argument("--selftest", action="store_true", help="kör inbyggd kontroll och avsluta")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return 0
    if not (args.start and args.end):
        ap.error("--from och --to krävs")

    start, end = parse_date(args.start), parse_date(args.end)
    if not (start and end) or end < start:
        ap.error("ogiltig period")

    root = Path(args.bundle).resolve()
    accounts, org, years, verifications = load_bundle(root)
    if not accounts:
        print(f"Ingen kontoplan hittad under {root} — är det bundle-roten?", file=sys.stderr)
        return 1

    fy, ledger = build_ledger(accounts, years, verifications, start, end)
    out = Path(args.out or f"huvudbok-{start.isoformat()}-{end.isoformat()}.html")
    out.write_text(render(org, fy, ledger, start, end), encoding="utf-8")

    total = sum(a["ub"] for a in ledger)
    rows = sum(len(a["rows"]) for a in ledger)
    print(f"{out}: {len(ledger)} konton, {rows} konteringsrader i perioden")
    if total != ZERO:
        print(f"VARNING: utgående balanser summerar till {kr(total)}, inte noll.", file=sys.stderr)
    if not fy:
        print("VARNING: inget räkenskapsår täcker periodstarten.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
