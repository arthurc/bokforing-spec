# bokforing

Bokför underlag — fakturor, kvitton, lönespecifikationer, kontoutdrag — som
verifikationer i en [Accounting Knowledge Bundle](reference/SPEC.md), en
OKF-profil för svensk bokföring.

## Skills

- **bokfor-underlag** — klassificerar underlaget mot spec:ens koncepttyper,
  härleder konteringen ur bundlens egen tidigare bokföring, och lägger fram
  ett förslag för bekräftelse innan något skrivs. Frågar hellre än gissar:
  kund- eller leverantörsfaktura, utlägg eller företagsbetalning, konto,
  momssats och räkenskapsår är alla saker den vägrar anta.
- **bokio-import** — hämtar bokföring, kontoplan, motparter och
  fakturor ur Bokios Company API och skriver dem som koncept. Redovisar
  luckorna i stället för att fylla dem: fem koncepttyper (`Employee`,
  `Payslip`, `Expense`, och båda deklarationstyperna) och några
  obligatoriska fält har ingen källa i Bokios API alls. Kompletterar
  företagsuppgifter ur allabolag.se där Bokio saknar dem. Fältmappningen ligger
  i [`skills/bokio-import/reference/faltmappning.md`](skills/bokio-import/reference/faltmappning.md).

## Evals

`skills/bokio-import/evals/` innehåller en fixture-server som svarar
som Bokios Company API, med bokföring som balanserar och fällor i det API:et
*inte* kan berätta. Den följer inte med i den paketerade skillen.

```bash
cd plugins/bokforing/skills/bokio-import/evals
python3 make_fixtures.py && python3 serve_fixtures.py 8731 &
export BOKIO_API_BASE=http://127.0.0.1:8731/v1 BOKIO_TOKEN=fixture \
       BOKIO_COMPANY_ID=ea9ee4dd-fae3-4aec-a7db-6fc9cc1f8135
```

Testfallen och deras assertions ligger i `evals/evals.json`, resultaten från
fyra iterationer i [`evals/results/`](skills/bokio-import/evals/results/README.md).
Själva körningarna committas inte — de är stora och genererade.

Två skript analyserar en körning i efterhand, båda tar iterationskatalogen som
argument: `evals/check_bundle.py` visar vad varje körning skrev jämfört med
startbundlen, och `evals/verify_bundle.py` kontrollerar om det som skrevs
stämmer mot API:et — konteringarna rad för rad, plus de fält där körningar
brukar gissa.

## Installation

```bash
/plugin marketplace add arthurc/bokforing-spec
```

Sedan `/plugin install bokforing@accounting-spec`.

Under utveckling går det snabbare att ladda pluginen direkt:

```bash
claude --plugin-dir plugins/bokforing
```

## Specifikationen

Skillen läser `spec/SPEC.md` från projektet när den finns — det är den
levande versionen — och faller annars tillbaka på `reference/SPEC.md` här i
pluginen, så att den fungerar i projekt som inte har spec:en själva.

Kopian speglar hela `spec/` (inklusive `reference/okf-spec-v01.md` som
SPEC.md länkar till) och uppdateras med:

```bash
rm -rf plugins/bokforing/reference && cp -R spec plugins/bokforing/reference
```

En pre-commit-hook kontrollerar att kopian är i synk. Aktivera den en gång
per klon:

```bash
git config core.hooksPath .githooks
```

## Referensbundles

Skillen använder OKF-referensbundles under `.okf/` (konteringshandbok,
lagtextsamling) när projektet har dem, men klarar sig utan. De ingår inte i
pluginen — de är upphovsrättsskyddat material som var och en får hålla
själv.
