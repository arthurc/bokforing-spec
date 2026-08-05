#!/usr/bin/env python3
"""Kontrollerar en skriven bundle mot fixturens sanning.

Båda baslinjerna i iteration 2 betygsatte sin egen import med sina egna
skript. Det här skriptet är oberoende: det läser konteringarna ur bundlens
`# Postings`-tabeller och jämför dem med journal entries som fixturen
faktiskt levererade, och kontrollerar de fält där körningarna gissat.

    python3 verify_bundle.py <sökväg till iteration-N>

Jämför mot fixturen som den ser ut NU. Körningar gjorda mot en äldre
fixture ger falska avvikelser — kontrollera bara den iteration som
kördes mot nuvarande make_fixtures.py.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_fixtures as fx  # noqa: E402

TRUTH = {e["journalEntryNumber"]: sorted(
    (i["account"], round(i["debit"], 2), round(i["credit"], 2)) for i in e["items"])
    for e in fx.JOURNAL}
DATES = {e["journalEntryNumber"]: e["date"] for e in fx.JOURNAL}
# Verifikationer som ingen faktura pekar på: motparten finns inte i API:et,
# så varje ifyllt värde är härlett ur fritext.
NO_COUNTERPARTY = {"V3", "V4", "V5", "V6", "V7", "V12"}
ROW = re.compile(r"^\|\s*(\d{4})\b[^|]*\|\s*([\d\s.,]*)\|\s*([\d\s.,]*)\|", re.M)


def num(s):
    s = s.replace(" ", "").replace(" ", "").replace(",", ".").strip()
    return round(float(s), 2) if s else 0.0


def parse(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = re.match(r"^---\n(.*?)\n---", text, re.S)
    front = {k: re.sub(r"\s+#.*$", "", v).strip()
             for k, v in re.findall(r"^([a-z_]+):\s*(.*)$", fm.group(1), re.M)} if fm else {}
    body = text[fm.end():] if fm else text
    section = re.search(r"^#+ *Postings\s*$(.*?)(?=^#+ |\Z)", body, re.S | re.M)
    rows = sorted((int(a), num(d), num(c))
                  for a, d, c in ROW.findall(section.group(1))) if section else []
    return front, rows


def check(bundle):
    problems, checked = [], 0
    for p in sorted((bundle / "verifications").rglob("*.md")):
        if p.name == "index.md":
            continue
        front, rows = parse(p)
        vn = front.get("verification_number", "").strip('"')
        if vn not in TRUTH:
            problems.append(f"{p.name}: okänt verifikationsnummer {vn!r}")
            continue
        checked += 1
        if rows != TRUTH[vn]:
            problems.append(f"{vn}: kontering avviker\n    bundle: {rows}\n    Bokio:  {TRUTH[vn]}")
        cp = front.get("counterparty", "").strip().strip('"')
        # 'Anna (efternamn framgår ej av Bokios API)' är en gissning med
        # brasklapp, inte ett okänt-värde: läs bara huvudledet.
        # Fältet ska antingen identifiera en motpart eller säga att den inte
        # går att identifiera. 'Okänd bank' är det senare; 'Anna' det förra.
        head = re.split(r"[(—-]", cp, 1)[0].strip()
        if vn in NO_COUNTERPARTY and head and not re.search(
                r"okänd|saknas|unknown|n/a|framgår inte|ingen |ej ", head, re.I):
            problems.append(f"{vn}: counterparty {cp!r} — ingen faktura pekar på "
                            f"verifikationen, värdet kan bara komma ur fritexten")
        rd = front.get("recorded_date", "").strip()
        if rd and rd == DATES[vn]:
            problems.append(f"{vn}: recorded_date == transaktionsdatum ({rd})")
        if not rd:
            problems.append(f"{vn}: recorded_date saknas — obligatoriskt (spec §4.2.1)")
    return checked, problems


def main(iteration):
    for bundle in sorted(pathlib.Path(iteration).glob("eval-*/*/outputs/bundle")):
        run = "/".join(bundle.parts[-4:-2])
        if not (bundle / "verifications").is_dir():
            print(f"{run}: inga verifikationer skrivna")
            continue
        n, problems = check(bundle)
        print(f"{run}: {n} verifikationer kontrollerade, {len(problems)} anmärkningar")
        for x in problems:
            print("  -", x)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
