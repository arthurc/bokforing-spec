#!/usr/bin/env python3
"""Hämta företagsuppgifter från allabolag.se som Bokios API saknar.

    allabolag_fetch.py 5567037485            # 10 siffror, utan bindestreck
    allabolag_fetch.py 556703-7485 --raw     # hela company-objektet

Skriver ett JSON-objekt med de fält som är relevanta för spec:ens
Organization (§4.1), Supplier (§4.4) och Customer (§4.6).

allabolag är UC Affärsinformations återgivning av Bolagsverkets och SCB:s
uppgifter, inte registret självt, och sidan har botskydd: den svarar 202 på
täta anrop. Hämta en gång per organisationsnummer, spara svaret, och kör
inte en loop över alla leverantörer på en gång.
"""
import json, re, sys, time, urllib.error, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def fetch(orgnr):
    orgnr = re.sub(r"\D", "", orgnr)
    if len(orgnr) != 10:
        sys.exit(f"Organisationsnumret ska vara 10 siffror, fick {orgnr!r}.")
    req = urllib.request.Request(f"https://allabolag.se/{orgnr}", headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as r:
                if r.status == 202:  # botskydd, inte ett svar
                    time.sleep(5 * (attempt + 1))
                    continue
                html = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            sys.exit(f"{e.code} för {orgnr}")
        m = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if not m:
            sys.exit(f"Ingen __NEXT_DATA__ för {orgnr} — sidlayouten kan ha ändrats.")
        return json.loads(m.group(1))["props"]["pageProps"]["company"], orgnr
    sys.exit(f"allabolag svarade 202 (botskydd) för {orgnr}. Vänta och försök igen.")


def addr(a):
    if not a:
        return None
    parts = [a.get("addressLine") or a.get("boxAddressLine"), a.get("zipCode"), a.get("postPlace")]
    return " ".join(p for p in parts if p) or None


def extract(c, orgnr):
    reg = {e["label"]: e["value"] for e in (c.get("registryStatusEntries") or [])}
    vat = reg.get("registeredForVat", c.get("registeredForVat"))
    return {
        # Direkt användbart för spec:ens fält.
        "title": c.get("legalName") or c.get("name"),
        "organization_number": f"{orgnr[:6]}-{orgnr[6:]}",
        # Momsnumret står inte i registret; SE+orgnr+01 är konventionen och
        # gäller bara om bolaget faktiskt är momsregistrerat. Bekräfta mot
        # Skatteverkets momsregisterkontroll innan det skrivs som ett faktum.
        "registered_for_vat": vat,
        "vat_number_derived": f"SE{orgnr}01" if vat else None,
        "f_tax_status": {True: "approved", False: "not_approved"}.get(
            reg.get("registeredForPrepayment")
        ),
        "postal_address": addr(c.get("legalPostalAddress") or c.get("postalAddress")),
        "workplace_address": addr(c.get("legalVisitorAddress") or c.get("visitorAddress")),
        # Kontext utan eget spec-fält — hör hemma i brödtexten.
        "registered_for_payroll_tax": reg.get("registeredForPayrollTax"),
        "company_type": (c.get("companyType") or {}).get("name"),
        "municipality": (c.get("location") or {}).get("municipality"),
        "nace": c.get("naceIndustries"),
        "registration_date": c.get("registrationDate"),
        "number_of_employees": c.get("numberOfEmployees"),
        "status": (c.get("status") or {}).get("status"),
        "phone": c.get("legalPhone") or c.get("phone"),
        "roles": [
            {"name": r.get("name"), "role": r.get("role")}
            for g in ((c.get("roles") or {}).get("roleGroups") or [])
            for r in (g.get("roles") or [])
        ],
        # Namn på arbetsställena finns; CFAR-numret gör det inte på den här
        # sidan (allabolag kallar det businessUnitId och visar det först i
        # arbetsställevyn). Se SKILL.md.
        "business_unit_names": [u.get("name") for u in (c.get("businessUnits") or [])],
    }


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--raw"]
    if not args:
        sys.exit(__doc__)
    company, orgnr = fetch(args[0])
    out = company if "--raw" in sys.argv else extract(company, orgnr)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()
