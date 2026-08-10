# bokforing-spec

Accounting Knowledge Bundle Specification — en [OKF](spec/reference/okf-spec-v01.md)-profil
för svensk bokföring — och en Claude Code-plugin som bokför enligt den.

Bokföringen ligger som vanliga markdown-filer med YAML-frontmatter, en fil per
koncept: verifikationer, räkenskapsår, kontoplan, motparter, underlag,
periodiseringar och deklarationer. Underlagen själva — kvitton, fakturor,
kontoutdrag — arkiveras i bundlens `archive/` i den form de togs emot, så att
bundlen bär sin egen räkenskapsinformation.

## Innehåll

- [`spec/SPEC.md`](spec/SPEC.md) — specifikationen. Fjorton koncepttyper, de
  fält svensk lag kräver per typ, och vilka body-sektioner som bär raddata
  frontmatter inte kan uttrycka. Med [OKF v0.1](spec/reference/okf-spec-v01.md)
  som referens.
- [`plugins/bokforing/`](plugins/bokforing/README.md) — plugin med skills för
  att bokföra underlag (`bokfor-underlag`) och importera befintlig bokföring
  ur Bokio (`bokio-import`).

## Installation

```bash
/plugin marketplace add arthurc/bokforing-spec
```

Sedan `/plugin install bokforing@accounting-spec`. Detaljer, evals och
utvecklingsflöde står i [pluginens README](plugins/bokforing/README.md).

## Utveckling

`plugins/*/reference/` är en exakt kopia av `spec/` så att pluginen fungerar i
projekt som inte har specen själva. En pre-commit-hook kontrollerar synken —
aktivera den en gång per klon:

```bash
git config core.hooksPath .githooks
```

Referensbundles under `.okf/` (konteringshandbok, lagtextsamling) används av
skillen när de finns men versioneras inte — det är upphovsrättsskyddat
material som var och en får hålla själv.
