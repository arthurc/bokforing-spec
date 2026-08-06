#!/usr/bin/env python3
"""Självtest för init_bolag: kontoplanens integritet och att luckor lämnas tomma.

    python3 test_init_bolag.py
"""
import argparse, re
import init_bolag as ib

# --- Kontoplanen ------------------------------------------------------------
rows = ib.accounts()
nums = [n for n, _, _ in rows]
assert len(rows) > 1000, f"kontoplanen ser stympad ut: {len(rows)} rader"
assert len(set(nums)) == len(nums), "dubblerade kontonummer i kontoplan.tsv"
assert nums == sorted(nums), "kontoplan.tsv är inte sorterad på kontonummer"
assert all(re.fullmatch(r"\d{4}", n) for n in nums), "kontonummer som inte är 4 siffror"
assert all(name.strip() for _, name, _ in rows), "konto utan namn"
assert dict((n, v) for n, _, v in rows)["2641"] == "F48", "momskoppling tappad"
assert dict((n, v) for n, _, v in rows)["1930"] == "", "1930 ska sakna momskoppling"

# --- YAML-citering ----------------------------------------------------------
assert ib.yaml_str("556036-0793") == '"556036-0793"'   # annars inte en sträng
assert ib.yaml_str("+46 8 123 45 67") == '"+46 8 123 45 67"'
assert ib.yaml_str("2026") == '"2026"'                 # fiscal_year_id
assert ib.yaml_str("2026-01-01") == "2026-01-01"       # datum är datum
assert ib.yaml_str("2026-08-06T06:47:30Z") == "2026-08-06T06:47:30Z"
assert ib.yaml_str("Kontoplan — Company AB") == "Kontoplan — Company AB"

# --- Rendering: luckor gissas aldrig ----------------------------------------
company = {
    "title": "Company AB",
    "organization_number": "559999-9991",
    "registered_for_vat": True,
    "vat_number_derived": "SE559999999101",
    "f_tax_status": "approved",
    "postal_address": "Storgatan 1, 111 22 Storstad",
    "roles": [{"name": "Anna Andersson", "role": "Ledamot"}],
}
blank = argparse.Namespace(account_standard="BAS 2026", fiscal_year_start=None,
                           fiscal_year_end=None, **{k: None for k in ib.GAPS})
files = ib.render(company, blank, "2026-08-06T09:00:00Z", rows, None)

org = files["organization.md"]
assert "vat_number:" not in org, "momsnumret härleddes trots att det inte angavs"
assert "SE559999999101" not in org, "det härledda momsnumret läckte in i konceptet"
assert "accounting_method:" not in org, "redovisningsmetoden gissades"
assert "registered_office:" not in org, "sätet gissades"
assert "f_tax_status: approved" in org, "f_tax_status från allabolag tappades"
assert "fiscal-years" not in files, "räkenskapsår skrevs utan datum"
# Radbrytningen är ombruten, så jämför på normaliserat mellanrum.
flat = " ".join(files["log.md"].split())
assert "Inget räkenskapsår är registrerat" in flat, "log.md redovisar inte luckan"
assert "vat_number, workplace_number" in flat, "log.md listar inte luckorna"

# Angivna värden ska däremot skrivas.
filled = argparse.Namespace(account_standard="BAS 2026",
                            fiscal_year_start="2026-01-01",
                            fiscal_year_end="2026-12-31",
                            **{k: f"v-{k}" for k in ib.GAPS})
filled.vat_number = "SE559999999101"
filled.accounting_method = "kontantmetoden"
files = ib.render(company, filled, "2026-08-06T09:00:00Z", rows, "2026")
assert "vat_number: SE559999999101" in files["organization.md"]
assert "accounting_method: kontantmetoden" in files["organization.md"]
fy = files["fiscal-years/2026.md"]
assert "status: open" in fy and "start_date: 2026-01-01" in fy
assert "# Opening Balances" in fy, "spec §4.3 kräver sektionen även vid noll"
assert "verifications/2026/index.md" in files, "länken i # Verifications dinglar"

# Kontoplanen ska bli hela tabellen, inte ett urval.
coa = files["chart-of-accounts.md"]
assert coa.count("\n| ") == len(rows) + 2, "rader tappade i # Accounts"  # + rubrik och avdelare
assert "| 2611 | Utgående moms på försäljning inom Sverige, 25 % | B10 |" in coa

print(f"OK — {len(rows)} konton, {sum(1 for _, _, v in rows if v)} med momskoppling")
