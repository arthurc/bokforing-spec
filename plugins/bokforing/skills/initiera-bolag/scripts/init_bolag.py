#!/usr/bin/env python3
"""Initiera en Accounting Knowledge Bundle för ett bolag.

    allabolag_fetch.py 5599999991 > ab.json
    init_bolag.py --allabolag ab.json --out ./bokforing            # plan
    init_bolag.py --allabolag ab.json --out ./bokforing --write    # skriv

Skriver index.md, log.md, organization.md (§4.1), chart-of-accounts.md
(§4.10) med BAS-kontoplanen ur reference/kontoplan.tsv, och — om
--fiscal-year-start/--end anges — fiscal-years/<label>.md (§4.3) med en
nollställd ingående balans.

Utan --write skrivs ingenting: då är utskriften den plan som ska bekräftas
med användaren. Fält som varken allabolag eller en flagga ger lämnas ute ur
frontmatter och redovisas som luckor. De gissas aldrig.
"""
import argparse, datetime, json, pathlib, re, sys, textwrap

HERE = pathlib.Path(__file__).resolve().parent
KONTOPLAN = HERE.parent / "reference" / "kontoplan.tsv"

# Fält spec:en har men ingen källa fyller automatiskt. Flaggan sätter dem;
# utan flagga blir de en lucka i planen. Se SKILL.md.
GAPS = {
    "vat_number": "Momsregistreringsnumret. allabolag svarar på *om* bolaget är"
    " momsregistrerat, inte på numret — kontrollera mot Skatteverkets"
    " momsregisterkontroll och sätt --vat-number.",
    "workplace_number": "Arbetsställenummer (CFAR). Källan är SCB:s"
    " företagsregister; obligatoriskt först när bolaget har fler än ett"
    " arbetsställe.",
    "accounting_method": "Redovisningsmetod för moms — fakturametoden eller"
    " kontantmetoden. Står i inget register; bolaget vet själv.",
    "registered_office": "Bolagets säte enligt bolagsordningen. Registrerad"
    " uppgift hos Bolagsverket — allabolags kommun är där bolaget ligger,"
    " vilket inte alltid är samma sak.",
    "technical_contact": "Teknisk kontaktperson för deklarationer och"
    " e-tjänster. Utses av bolaget, står i inget register.",
    "technical_contact_email": "Den kontaktpersonens e-postadress.",
    "technical_contact_phone": "Den kontaktpersonens telefonnummer.",
}


def accounts():
    rows = []
    for line in KONTOPLAN.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        rows.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return rows


ISO = re.compile(r"\d{4}-\d{2}-\d{2}(T[\d:]+Z)?")


def yaml_str(v):
    """Citera det som annars läses som något annat än en sträng.

    Datum och tidsstämplar lämnas ociterade — YAML läser dem som datum,
    vilket är vad de är. Organisationsnummer och telefonnummer måste
    citeras: 556036-0793 blir annars inget alls, och +46… blir ett tal.
    """
    s = str(v)
    if ISO.fullmatch(s):
        return s
    return f'"{s}"' if re.search(r"^[\d+]|:", s) else s


def para(text):
    """Bryt ett stycke till 76 tecken. Interpolerade namn varierar i längd."""
    return textwrap.fill(" ".join(text.split()), 76)


def frontmatter(pairs):
    body = "\n".join(f"{k}: {yaml_str(v)}" for k, v in pairs if v)
    return f"---\n{body}\n---\n"


def organization(c, a, ts):
    fm = [
        ("type", "Organization"),
        ("title", c["title"]),
        ("organization_number", c["organization_number"]),
        ("vat_number", a.vat_number),
        ("workplace_number", a.workplace_number),
        ("f_tax_status", c.get("f_tax_status")),
        ("accounting_method", a.accounting_method),
        ("registered_office", a.registered_office),
        ("postal_address", c.get("postal_address")),
        ("workplace_address", c.get("workplace_address")),
        ("technical_contact", a.technical_contact),
        ("technical_contact_email", a.technical_contact_email),
        ("technical_contact_phone", a.technical_contact_phone),
        ("timestamp", ts),
    ]
    roles = c.get("roles") or []
    contact = "\n".join(f"- {r['role']}: {r['name']}" for r in roles) or (
        "Inga roller hämtade."
    )
    momsrad = (
        "Bolaget är momsregistrerat enligt allabolag."
        if c.get("registered_for_vat")
        else "Bolaget är inte momsregistrerat enligt allabolag."
    )
    saknas = ", ".join(k for k in GAPS if not getattr(a, k, None)) or "inga"
    digits = re.sub(r"\D", "", c["organization_number"])
    return frontmatter(fm) + "\n" + para(f"""
{c['title']}, org.nr {c['organization_number']}. Bolagets egen masterdata:
identitet, skatteregistreringar, redovisningsmetod för moms, teknisk
kontaktperson för deklarationer, och arbetsställen.
""") + "\n\n" + para(f"""
Uppgifterna nedan är hämtade från allabolag.se {ts[:10]} — UC
Affärsinformations återgivning av Bolagsverkets och SCB:s register, inte
registren själva. {momsrad} Bolagsform: {c.get('company_type') or 'okänd'}.
Registrerat {c.get('registration_date') or 'okänt datum'}, säte enligt
allabolag i {c.get('municipality') or 'okänd kommun'}.
""") + "\n\n" + para(f"""
Fält som ännu saknas i frontmatter: {saknas}. De har ingen källa i allabolag
och ska fyllas i från Skatteverket, Bolagsverket, SCB eller av bolaget självt.
""") + f"""

# Contact

Styrelse och firmatecknare enligt allabolag:

{contact}

Teknisk kontaktperson för deklarationer och e-tjänster:
{a.technical_contact or "**ej angiven**"}.

# Citations

[1] allabolag.se/{digits} — hämtad {ts[:10]}.
[2] Skatteförfarandelagen (SFL) 26 kap. — arbetsgivardeklarationens
    organisationsnummer (FK201) och individuppgiftens arbetsställenummer
    (FK060).
[3] Statistiska centralbyrån (SCB), Företagsregistret — arbetsställenummer
    (CFAR-nummer) per arbetsställe.
"""


def chart_of_accounts(c, a, ts, rows):
    fm = [
        ("type", "Chart of Accounts"),
        ("account_standard", a.account_standard),
        ("title", f"Kontoplan — {c['title']}"),
        ("description", f"Kontoplan för {c['title']} med momskoppling per konto."),
        ("timestamp", ts),
    ]
    table = "\n".join(f"| {n} | {name} | {vat} |" for n, name, vat in rows)
    with_vat = sum(1 for _, _, v in rows if v)
    return frontmatter(fm) + "\n" + para(f"""
Kontoplan för {c['title']}, baserad på {a.account_standard}. {len(rows)}
konton, varav {with_vat} med mappning mot ett fält i
mervärdesskattedeklarationen. Konton utan momsrelevans — bankkonton,
lagerkonton — har tom VAT Declaration Field.
""") + "\n\n" + para("""
Kontoplanen är initierad som en fullständig baskontoplan, inte som en
förteckning över konton bolaget faktiskt använder. Den uppfyller därmed BFL
5 kap. 1 § med marginal, men säger inget om vilka konton som är i bruk.
""") + f"""

# Accounts

| Account | Account Name | VAT Declaration Field |
| ------- | ------------ | --------------------- |
{table}

# Citations

[1] Bokföringslagen (BFL) 5 kap. 1 § — systemdokumentation.
[2] Mervärdesskattelagen (ML); Skatteförfarandelagen (SFL) 26 kap. —
    Skatteverkets blankett för mervärdesskattedeklaration.
"""


def fiscal_year(c, a, ts, label):
    fm = [
        ("type", "Fiscal Year"),
        ("fiscal_year_id", label),
        ("start_date", a.fiscal_year_start),
        ("end_date", a.fiscal_year_end),
        ("status", "open"),
        ("title", f"Räkenskapsår {a.fiscal_year_start} – {a.fiscal_year_end}"),
        ("timestamp", ts),
    ]
    return frontmatter(fm) + "\n" + para(f"""
Räkenskapsår för {c['title']}, {a.fiscal_year_start} – {a.fiscal_year_end}.
Öppet; inga verifikationer bokförda ännu.
""") + "\n\n" + para("""
`previous_fiscal_year` och `verification_number_range` saknas: det finns
inget föregående räkenskapsår i bundlen och ännu ingen verifikation att ange
ett intervall för. Sätt dem när något av dem blir sant.
""") + f"""

# Verifications

Verifikationer för räkenskapsåret läggs under
[verifications/{label}](/verifications/{label}/).

# Opening Balances

""" + para(f"""
Ingående balans {a.fiscal_year_start}. Bundlen har inget föregående
räkenskapsår, så samtliga konton står på noll — tabellen är därför tom.
**Är detta inte bolagets första räkenskapsår är balansen fel**: den ska då
hämtas från föregående års utgående balans (SIE-fil, årsredovisning eller
tidigare system) och skrivas in här innan något bokförs.
""") + """

| Account | Balance |
| ------- | ------: |

# Citations

[1] Bokföringslagen (BFL) 3 kap. 1–3 §§, 6 kap. 1 §.
"""


def render(c, a, ts, rows, label):
    files = {
        "organization.md": organization(c, a, ts),
        "chart-of-accounts.md": chart_of_accounts(c, a, ts, rows),
    }
    fy_line = ""
    if label:
        files[f"fiscal-years/{label}.md"] = fiscal_year(c, a, ts, label)
        files[f"verifications/{label}/index.md"] = (
            f"# Verifikationer {label}\n\nInga verifikationer bokförda ännu.\n"
        )
        fy_line = (
            f"\n# Fiscal Years\n\n- [fiscal-years/{label}.md]"
            f"(/fiscal-years/{label}.md) - räkenskapsår {a.fiscal_year_start}"
            f" – {a.fiscal_year_end}, öppet\n"
        )
    files["index.md"] = f"""# Concepts

- [organization.md](/organization.md) - {c['title']}, org.nr {c['organization_number']}
- [chart-of-accounts.md](/chart-of-accounts.md) - kontoplan, {len(rows)} konton ({a.account_standard})
{fy_line}"""
    saknas = ", ".join(k for k in GAPS if not getattr(a, k, None)) or "inga"
    aret = ("Inget räkenskapsår är registrerat, så inget kan bokföras ännu."
            if not label else
            f"Räkenskapsåret {label} är registrerat med nollställd ingående "
            f"balans; är det inte bolagets första år måste balansen hämtas "
            f"från föregående års utgående balans först.")
    entries = [
        f"""**Initialization**: Bundlen skapad för {c['title']} (org.nr
        {c['organization_number']}) med `initiera-bolag`. Företagsuppgifterna
        är hämtade från allabolag.se {ts[:10]}; kontoplanen är initierad som
        en fullständig {a.account_standard}-baskontoplan om {len(rows)}
        konton, varav {sum(1 for _, _, v in rows if v)} med momskoppling.""",
        f"""**Gap**: Följande fält lämnades tomma för att ingen källa fyller
        dem: {saknas}. {aret}""",
    ]
    bullets = "\n".join("- " + textwrap.indent(para(t), "  ").lstrip()
                        for t in entries)
    files["log.md"] = f"# Log\n\n## {ts[:10]}\n\n{bullets}\n"
    return files


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--allabolag", required=True,
                   help="JSON från allabolag_fetch.py, eller - för stdin")
    p.add_argument("--out", required=True, help="katalog bundlen skrivs till")
    p.add_argument("--write", action="store_true",
                   help="skriv filerna; utan flaggan skrivs bara planen")
    p.add_argument("--force", action="store_true",
                   help="tillåt skrivning i en katalog som inte är tom")
    p.add_argument("--account-standard", default="BAS 2026")
    p.add_argument("--fiscal-year-start", help="ISO-datum, t.ex. 2026-01-01")
    p.add_argument("--fiscal-year-end", help="ISO-datum, t.ex. 2026-12-31")
    p.add_argument("--fiscal-year-id", help="etikett, härleds annars ur datumen")
    p.add_argument("--timestamp", help="ISO 8601, annars nu i UTC")
    for gap in GAPS:
        p.add_argument("--" + gap.replace("_", "-"))
    a = p.parse_args()

    raw = sys.stdin.read() if a.allabolag == "-" else \
        pathlib.Path(a.allabolag).read_text(encoding="utf-8")
    c = json.loads(raw)
    if "organization_number" not in c or "title" not in c:
        sys.exit("Filen ser inte ut som utdata från allabolag_fetch.py "
                 "(saknar title/organization_number). Kör den utan --raw.")

    if bool(a.fiscal_year_start) != bool(a.fiscal_year_end):
        sys.exit("Ange både --fiscal-year-start och --fiscal-year-end, eller "
                 "ingendera. Ett räkenskapsår utan slutdatum är inte ett år.")
    label = None
    if a.fiscal_year_start:
        for d in (a.fiscal_year_start, a.fiscal_year_end):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                sys.exit(f"{d!r} är inte ett ISO 8601-datum (YYYY-MM-DD).")
        if a.fiscal_year_end <= a.fiscal_year_start:
            sys.exit("Räkenskapsårets slutdatum ligger före startdatumet.")
        label = a.fiscal_year_id or (
            a.fiscal_year_start[:4] if a.fiscal_year_start[:4] == a.fiscal_year_end[:4]
            else f"{a.fiscal_year_start[:4]}-{a.fiscal_year_end[:4]}")

    ts = a.timestamp or datetime.datetime.now(
        datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows = accounts()
    files = render(c, a, ts, rows, label)

    out = pathlib.Path(a.out)
    print(f"Bolag:      {c['title']} ({c['organization_number']})")
    print(f"Bundle:     {out}")
    print(f"Kontoplan:  {len(rows)} konton, "
          f"{sum(1 for _, _, v in rows if v)} med momskoppling "
          f"({a.account_standard})")
    print(f"Räkenskapsår: {label or 'inget — ange --fiscal-year-start/--end'}")
    print("\nFiler:")
    for name, text in sorted(files.items()):
        exists = " (SKRIVS ÖVER)" if (out / name).exists() else ""
        print(f"  {name:34} {len(text.encode()):>7} B{exists}")

    missing = [(k, why) for k, why in GAPS.items() if not getattr(a, k, None)]
    print(f"\nLuckor ({len(missing)}) — lämnas ute ur frontmatter, gissas inte:")
    for k, why in missing:
        print(f"  {k}\n      {why}")
    if not a.vat_number and c.get("registered_for_vat"):
        print(f"\n  OBS: allabolag anger bolaget som momsregistrerat. "
              f"Konventionen ger {c.get('vat_number_derived')}, men den "
              f"brister vid momsgrupp — bekräfta mot Skatteverket innan\n"
              f"       --vat-number sätts.")
    if not label:
        print("\n  OBS: inget räkenskapsår skrivs. Utan Fiscal Year kan inget "
              "bokföras i bundlen.")

    if not a.write:
        print("\nInget skrivet. Bekräfta planen med användaren och kör om med "
              "--write.")
        return
    if out.exists() and any(out.iterdir()) and not a.force:
        sys.exit(f"\n{out} är inte tom. Granska innehållet först; --force "
                 f"skriver ändå.")
    for name, text in files.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (out / "archive").mkdir(exist_ok=True)
    print(f"\nSkrev {len(files)} filer till {out} samt en tom archive/.")


if __name__ == "__main__":
    main()
