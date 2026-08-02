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

## Installation

```bash
/plugin marketplace add /Users/arthur/src/accounting-spec
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
