#!/usr/bin/env python3
"""Bygger fixture-svar för Bokios Company API under fixtures/.

Datat är påhittat men formen följer OpenAPI-schemana i docs.bokio.se, och
innehållet är valt för att träffa spec:ens svåra fall: en verifikation utan
motpart, ett utlägg utan känd anställd, en lön vars koncepttyper saknar
endpoint, en betald leverantörsfaktura utan betalningsdatum, en delbetald
kundfaktura, en utkastfaktura som inte ska importeras, och ett stängt
räkenskapsår vars balanser bara finns i SIE.

Bokföringen ska däremot gå ihop. Groparna ska ligga i vad Bokios API inte
kan berätta, inte i att fixturens siffror är fel — ett fel som inte är
avsiktligt drar körningarnas uppmärksamhet dit i stället för till det som
testas. IB/UB räknas därför fram ur verifikationerna, och varje reskontra-
post har sin motsvarande betalningsverifikation.

Organisationsnumren har giltig Luhn-kontrollsiffra och är kontrollerade mot
allabolag.se: samtliga ger 404, dvs. de tillhör inget verkligt bolag.

    python3 make_fixtures.py && python3 serve_fixtures.py
"""
import collections, json, pathlib

OUT = pathlib.Path(__file__).parent / "fixtures"
CID = "ea9ee4dd-fae3-4aec-a7db-6fc9cc1f8135"

ORGNR = "5599999009"          # Company AB
ORGNR_KONTOR = "5599999017"   # Kontorsvaruhuset AB
ORGNR_KONSULT = "5599999025"  # Nordisk Konsult AB
ORGNR_KUND = "5599999033"     # Storkund AB

SUP_A = "11111111-1111-1111-1111-111111111111"
SUP_B = "22222222-2222-2222-2222-222222222222"
CUS_A = "33333333-3333-3333-3333-333333333333"
CUS_B = "44444444-4444-4444-4444-444444444444"
FY_PREV = "55555555-5555-5555-5555-555555555550"  # 2025, closed
FY_CUR = "55555555-5555-5555-5555-555555555555"   # 2026, open

# Ingående balans 2026-01-01. Summerar till noll: en bokföring som inte
# balanserar vid årets ingång är ett fixturfel, inte en fälla.
IB = {1930: 45231.00, 1510: 0.00, 2440: -12000.00, 2081: -50000.00,
      2091: 16769.00}


def je(n, num, title, date, items):
    return dict(
        id=f"{n:08d}-0000-0000-0000-000000000000",
        journalEntryNumber=num, title=title, date=date,
        items=[dict(id=i, account=a, debit=d, credit=c)
               for i, (a, d, c) in enumerate(items, 1)],
        tags=[], reversingJournalEntryId=None, reversedByJournalEntryId=None)


JOURNAL = [
    je(1, "V1", "Leverantörsfaktura KV-88213 Kontorsvaruhuset", "2026-03-04",
       [(6110, 1000.0, 0.0), (2641, 250.0, 0.0), (2440, 0.0, 1250.0)]),
    je(2, "V2", "Kundfaktura 2026-001 Storkund AB", "2026-03-10",
       [(1510, 12500.0, 0.0), (3041, 0.0, 10000.0), (2611, 0.0, 2500.0)]),
    # Ingen faktura pekar hit: counterparty finns ingenstans i API:et.
    je(3, "V3", "Bankavgift mars", "2026-03-31",
       [(6570, 65.0, 0.0), (1930, 0.0, 65.0)]),
    # Frestar till Expense §4.11 — men vem som lagt ut står ingenstans.
    # Tågbiljett: 6 % moms, inte 25. Fällan ska vara att motparten saknas,
    # inte att momsen är felräknad.
    je(4, "V4", "Utlägg resa Anna", "2026-04-02",
       [(5810, 849.06, 0.0), (2641, 50.94, 0.0), (2890, 0.0, 900.0)]),
    # Frestar till Payslip §4.9 / Employee §4.8 — inga sådana endpoints.
    je(5, "V5", "Lön april", "2026-04-25",
       [(7210, 45000.0, 0.0), (2710, 0.0, 13500.0), (1930, 0.0, 31500.0),
        (7510, 14139.0, 0.0), (2731, 0.0, 14139.0)]),
    je(6, "V6", "Betalning leverantörsskuld ingående balans", "2026-04-28",
       [(2440, 12000.0, 0.0), (1930, 0.0, 12000.0)]),
    je(7, "V7", "Betalning KV-88213", "2026-03-31",
       [(2440, 1250.0, 0.0), (1930, 0.0, 1250.0)]),
    je(8, "V8", "Inbetalning kundfaktura 2026-001", "2026-04-08",
       [(1930, 12500.0, 0.0), (1510, 0.0, 12500.0)]),
    je(9, "V9", "Konsultarvode Nordisk Konsult NK-4412", "2026-05-12",
       [(6530, 24000.0, 0.0), (2641, 6000.0, 0.0), (2440, 0.0, 30000.0)]),
    je(10, "V10", "Kundfaktura 2026-002 Johan Persson", "2026-06-01",
       [(1510, 8000.0, 0.0), (3041, 0.0, 6400.0), (2611, 0.0, 1600.0)]),
    je(11, "V11", "Delbetalning kundfaktura 2026-002", "2026-06-15",
       [(1930, 5000.0, 0.0), (1510, 0.0, 5000.0)]),
    # Utlägget regleras: 2890 nollas, annars ser den kvar som en skuld.
    je(12, "V12", "Utbetalning utlägg", "2026-05-25",
       [(2890, 900.0, 0.0), (1930, 0.0, 900.0)]),
]

ACCOUNTS = [
    (1510, "Kundfordringar"), (1930, "Företagskonto"),
    (2081, "Aktiekapital"), (2091, "Balanserad vinst eller förlust"),
    (2440, "Leverantörsskulder"), (2611, "Utgående moms 25 %"),
    (2641, "Ingående moms"), (2710, "Personalskatt"),
    (2731, "Avräkning lagstadgade sociala avgifter"),
    (2890, "Övriga kortfristiga skulder"),
    (3041, "Försäljning tjänster 25 % moms"), (5810, "Biljetter"),
    (6110, "Kontorsmaterial"), (6530, "Redovisningstjänster"),
    (6570, "Bankkostnader"), (7210, "Löner till tjänstemän"),
    (7510, "Lagstadgade sociala avgifter"),
]

DATA = {
    "company-information": {"companyInformation": dict(
        id=CID, companyType="limitedCompany", name="Company AB",
        organizationNumber=ORGNR, phone="+46 8 123 45 67",
        email="info@company.example", hasBBA=True,
        address=dict(line1="Storgatan 1", line2=None, city="Storstad",
                     postalCode="111 22", country="SE"))},

    # Två år: 2025 stängt (kräver utgående balanser), 2026 öppet (kräver
    # ingående balanser). Båda kraven pekar på SIE-filen.
    "fiscal-years": [
        dict(id=FY_PREV, startDate="2025-01-01", endDate="2025-12-31",
             accountingMethod="accrual", status="closed"),
        dict(id=FY_CUR, startDate="2026-01-01", endDate="2026-12-31",
             accountingMethod="accrual", status="open"),
    ],

    # Ingen rutmappning per konto — den finns inte i Bokio.
    "chart-of-accounts": [dict(account=a, name=n, accountType="basePlanAccount")
                          for a, n in ACCOUNTS],

    "suppliers": [
        dict(id=SUP_A, name="Kontorsvaruhuset AB", orgNumber=ORGNR_KONTOR,
             vatNumber=f"SE{ORGNR_KONTOR}01", currency="SEK",
             address=dict(line1="Lagergatan 4", line2=None, city="Storstad",
                          postalCode="123 45", country="SE"),
             paymentDetails=dict(type="bankgiro", bankgiroNumber="123-4567")),
        # Tjänsteleverantör: f_tax_status avgör skatteavdrag, saknas i Bokio.
        dict(id=SUP_B, name="Nordisk Konsult AB", orgNumber=ORGNR_KONSULT,
             vatNumber=f"SE{ORGNR_KONSULT}01", currency="SEK",
             address=dict(line1="Konsultvägen 9", line2=None, city="Storstad",
                          postalCode="111 44", country="SE"),
             paymentDetails=dict(type="transfer", clearingNumber="8327",
                                 accountNumber="9441234567")),
    ],

    "customers": [
        dict(id=CUS_A, name="Storkund AB", type="company",
             orgNumber=ORGNR_KUND, vatNumber=f"SE{ORGNR_KUND}01",
             paymentTerms="30", language="sv",
             modifiedDateTime="2026-01-08T09:00:00Z",
             contactsDetails=[dict(id="aaaa1111-0000-0000-0000-000000000000",
                                   name="Karin Ek", email="karin@storkund.example",
                                   phone="+46 70 111 22 33", isDefault=True)],
             address=dict(line1="Kundgatan 12", line2=None, city="Storstad",
                          postalCode="111 33", country="SE",
                          countrySubdivision=None)),
        # Privatperson: inget av spec:ens tre identifierande fält går att fylla.
        dict(id=CUS_B, name="Johan Persson", type="private", orgNumber=None,
             vatNumber=None, paymentTerms="15", language="sv",
             modifiedDateTime="2026-02-01T09:00:00Z", contactsDetails=[],
             address=dict(line1="Villagatan 3", line2=None, city="Småstad",
                          postalCode="222 11", country="SE",
                          countrySubdivision=None)),
    ],

    "supplier-invoices": [
        # Betald, men API:et har inget betalningsdatum för leverantörsfakturor.
        dict(id="66666666-0000-0000-0000-000000000001",
             supplierRef=dict(id=SUP_A, name="Kontorsvaruhuset AB"),
             invoiceNumber="KV-88213", invoiceDate="2026-03-01",
             dueDate="2026-03-31", totalAmount=1250.0, remainingAmount=0.0,
             currency="SEK", currencyRate=1.0,
             journalEntryRef=dict(id="00000001-0000-0000-0000-000000000000"),
             rows=[dict(id="r1", description="Kontorsmaterial", quantity=1.0,
                        unitPrice=1000.0, unitType="piece", taxRate=0.25,
                        projectRef=None, costCenterRef=None)],
             uploadRefs=[dict(id="77777777-0000-0000-0000-000000000001")]),
        dict(id="66666666-0000-0000-0000-000000000002",
             supplierRef=dict(id=SUP_B, name="Nordisk Konsult AB"),
             invoiceNumber="NK-4412", invoiceDate="2026-05-02",
             dueDate="2026-06-01", totalAmount=30000.0, remainingAmount=30000.0,
             currency="SEK", currencyRate=1.0,
             journalEntryRef=dict(id="00000009-0000-0000-0000-000000000000"),
             rows=[dict(id="r2", description="Redovisningskonsult april",
                        quantity=20.0, unitPrice=1200.0, unitType="hour",
                        taxRate=0.25, projectRef=None, costCenterRef=None)],
             uploadRefs=[]),
    ],

    "invoices": [
        dict(id="88888888-0000-0000-0000-000000000001", type="invoice",
             customerRef=dict(id=CUS_A, name="Storkund AB"),
             contactDetailRef=None, invoiceNumber="2026-001",
             paymentReference="20260011", currency="SEK", currencyRate=1.0,
             totalAmount=12500.0, totalTax=2500.0, paidAmount=12500.0,
             status="paid", invoiceDate="2026-03-10", dueDate="2026-04-09",
             publishedDateTime="2026-03-10T10:00:00Z",
             lineItems=[dict(id=1, description="Utvecklingstjänster mars",
                             itemType="salesItem", productType="services",
                             quantity=20.0, unitPrice=500.0, taxRate=0.25,
                             unitType="hour", bookkeepingAccountNumber=3041)],
             attachmentRefs=[], creditNoteRefs=[],
             journalEntryRef=dict(id="00000002-0000-0000-0000-000000000000")),
        # underPaid: Bokios åttonde status, spec:en har två.
        dict(id="88888888-0000-0000-0000-000000000002", type="invoice",
             customerRef=dict(id=CUS_B, name="Johan Persson"),
             contactDetailRef=None, invoiceNumber="2026-002",
             paymentReference="20260022", currency="SEK", currencyRate=1.0,
             totalAmount=8000.0, totalTax=1600.0, paidAmount=5000.0,
             status="underPaid", invoiceDate="2026-06-01", dueDate="2026-06-15",
             publishedDateTime="2026-06-01T10:00:00Z",
             lineItems=[dict(id=1, description="Installation", itemType="salesItem",
                             productType="services", quantity=1.0,
                             unitPrice=6400.0, taxRate=0.25, unitType="piece",
                             bookkeepingAccountNumber=3041)],
             attachmentRefs=[], creditNoteRefs=[],
             journalEntryRef=dict(id="00000010-0000-0000-0000-000000000000")),
        # Utkast: ingen utställd faktura, ska inte importeras alls.
        dict(id="88888888-0000-0000-0000-000000000003", type="invoice",
             customerRef=dict(id=CUS_A, name="Storkund AB"),
             contactDetailRef=None, invoiceNumber=None, paymentReference=None,
             currency="SEK", currencyRate=1.0, totalAmount=4000.0,
             totalTax=800.0, paidAmount=0.0, status="draft",
             invoiceDate="2026-07-01", dueDate=None, publishedDateTime=None,
             lineItems=[dict(id=1, description="Preliminärt uppdrag",
                             itemType="salesItem", productType="services",
                             quantity=1.0, unitPrice=3200.0, taxRate=0.25,
                             unitType="piece", bookkeepingAccountNumber=3041)],
             attachmentRefs=[], creditNoteRefs=[], journalEntryRef=None),
    ],

    "journal-entries": JOURNAL,

    "uploads": [
        dict(id="77777777-0000-0000-0000-000000000001",
             description="Faktura KV-88213", contentType="application/pdf",
             journalEntryId="00000001-0000-0000-0000-000000000000"),
        # Kvittot till utlägget finns — men inte vem som lagt ut.
        dict(id="77777777-0000-0000-0000-000000000002",
             description="Kvitto tågbiljett", contentType="image/jpeg",
             journalEntryId="00000004-0000-0000-0000-000000000000"),
    ],
}

PAYMENTS = {
    "88888888-0000-0000-0000-000000000001": [dict(
        id="99999999-0000-0000-0000-000000000001",
        invoiceId="88888888-0000-0000-0000-000000000001", date="2026-04-08",
        sumBaseCurrency=12500.0, bookkeepingAccountNumber=1930,
        journalEntryRef=dict(id="00000008-0000-0000-0000-000000000000"))],
    "88888888-0000-0000-0000-000000000002": [dict(
        id="99999999-0000-0000-0000-000000000002",
        invoiceId="88888888-0000-0000-0000-000000000002", date="2026-06-15",
        sumBaseCurrency=5000.0, bookkeepingAccountNumber=1930,
        journalEntryRef=dict(id="00000011-0000-0000-0000-000000000000"))],
    "88888888-0000-0000-0000-000000000003": [],
}

PAGED = {"fiscal-years", "suppliers", "customers", "supplier-invoices",
         "invoices", "journal-entries", "uploads"}


def balances():
    """UB per konto = IB + summan av verifikationernas rörelser."""
    ub = collections.defaultdict(float, IB)
    for entry in JOURNAL:
        for it in entry["items"]:
            ub[it["account"]] += it["debit"] - it["credit"]
    return {a: round(v, 2) for a, v in sorted(ub.items())}


def check():
    """Fixturen ska balansera. Fel här är fixturfel, inte fällor."""
    for entry in JOURNAL:
        d = sum(i["debit"] for i in entry["items"])
        c = sum(i["credit"] for i in entry["items"])
        assert abs(d - c) < 0.005, f"{entry['journalEntryNumber']}: {d} != {c}"
    assert abs(sum(IB.values())) < 0.005, f"IB summerar till {sum(IB.values())}"
    ub = balances()
    assert abs(sum(ub.values())) < 0.005, f"UB summerar till {sum(ub.values())}"
    known = {a for a, _ in ACCOUNTS}
    used = {i["account"] for e in JOURNAL for i in e["items"]} | set(IB)
    assert used <= known, f"konton utanför kontoplanen: {used - known}"
    # Reskontrornas restbelopp ska stämma mot huvudbokens saldon.
    assert abs(ub[2440] + 30000.0) < 0.005, f"2440 = {ub[2440]}, väntat -30000"
    assert abs(ub[1510] - 3000.0) < 0.005, f"1510 = {ub[1510]}, väntat 3000"
    assert abs(ub[2890]) < 0.005, f"2890 = {ub[2890]}, väntat 0"
    return ub


def write(rel, obj):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def sie(fy_id, start, end, ib, ub, names):
    rows = ['#FLAGGA 0', '#PROGRAM "Bokio" 1.0', '#FORMAT PC8',
            f'#FNAMN "Company AB"', f'#ORGNR {ORGNR[:6]}-{ORGNR[6:]}',
            f'#RAR 0 {start} {end}']
    rows += [f'#KONTO {a} "{names[a]}"' for a, _ in sorted(ib.items())]
    rows += [f"#IB 0 {a} {v:.2f}" for a, v in sorted(ib.items())]
    rows += [f"#UB 0 {a} {v:.2f}" for a, v in sorted(ub.items())]
    p = OUT / "sie" / fy_id / "download.bin"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    ub = check()
    names = dict(ACCOUNTS)
    for name, body in DATA.items():
        if name in PAGED:
            body = {"result": body, "totalItems": len(body), "totalPages": 1,
                    "currentPage": 1}
        write(f"{name}.json", body)
    for inv, pays in PAYMENTS.items():
        write(f"invoices/{inv}/payments.json",
              {"result": pays, "totalItems": len(pays), "totalPages": 1,
               "currentPage": 1})

    for uid, blob in [
        ("77777777-0000-0000-0000-000000000001",
         b"%PDF-1.4\n% fixture: leverantorsfaktura KV-88213\n%%EOF\n"),
        ("77777777-0000-0000-0000-000000000002",
         b"\xff\xd8\xff\xe0 fixture: kvitto tagbiljett \xff\xd9"),
    ]:
        p = OUT / "uploads" / uid / "download.bin"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(blob)

    # 2025 stängdes med samma balanser som 2026 öppnar med.
    zero = {a: 0.0 for a in IB}
    sie(FY_PREV, "20250101", "20251231", zero, IB, names)
    sie(FY_CUR, "20260101", "20261231", IB, ub, names)
    print(f"fixtures skrivna till {OUT} — bokföringen balanserar")


if __name__ == "__main__":
    main()
