---
name: initiera-bolag
description: Använd när en ny accounting-bundle ska sättas upp för ett bolag utifrån dess organisationsnummer — "initiera bolaget", "skapa en bundle för 559999-9991", "sätt upp bokföringen för vårt AB", "lägg upp kontoplanen", "starta bokföring för ett nytt bolag". Använd även när en befintlig bundle saknar organization.md, chart-of-accounts.md eller ett räkenskapsår, och när frågan är vilka företagsuppgifter som går att hämta ur allabolag.se och vilka som måste komma från Skatteverket, Bolagsverket eller SCB.
---

# Initiera bolag

Skapa en tom Accounting Knowledge Bundle för ett bolag: `organization.md`
(§4.1), `chart-of-accounts.md` (§4.10) med en fullständig BAS-kontoplan,
och ett första `Fiscal Year` (§4.3). Enda indata är organisationsnumret;
resten hämtas från [allabolag.se](https://allabolag.se/) eller frågas fram.

Specifikationen läses från `spec/SPEC.md` i projektet när den finns — det är
den levande versionen — annars från `${CLAUDE_PLUGIN_ROOT}/reference/SPEC.md`.
Paragrafhänvisningarna nedan (§4.1, §4.10, …) syftar på den.

Skriptet `scripts/init_bolag.py` gör hela renderingen. Kör det, visa planen,
och skriv först efter ett ja.

## Kärnprincip

**En initiering är inte ofarlig för att bundlen är tom.** Det som skrivs här
— organisationsnummer, momsnummer, redovisningsmetod, räkenskapsårets datum,
ingående balans — är det varje senare verifikation vilar på. Ett fel i
`accounting_method` flyttar momsen till fel period för hela året. En
nollställd ingående balans i ett bolag som redan har historik är inte en tom
bundle, det är en felaktig.

**Gissa aldrig ett fält som inget register svarar på.** Sju av spec:ens fält
har ingen källa i allabolag (se tabellen i steg 2). Skriptet lämnar dem ute
ur frontmatter och listar dem som luckor. Fyll dem med flaggor när användaren
svarat — fyll dem aldrig med det som "brukar stämma".

**allabolag är UC:s återgivning, inte registret.** Bolagsverket gäller för
firma och säte, Skatteverket för moms och F-skatt, SCB för CFAR-nummer. För
uppgifter som ska ligga i sju års räkenskapsinformation är allabolag en
indikation.

**Inget skrivs innan användaren bekräftat.** Steg 3 är en grind. Utan
`--write` skriver skriptet ingenting — det är avsiktligt, inte en
säkerhetsspärr att kringgå.

## Steg

### 0. Kolla att bundlen inte redan finns

```bash
grep -rl "^type: Chart of Accounts" --include='*.md' . | head
```

Träff betyder att bundlen redan är initierad. **Initiera inte om.** Fråga
vad som saknas och komplettera den filen i stället — `organization.md` och
`chart-of-accounts.md` ska uppdateras på plats med bumpad `timestamp`
(§4.1, §4.10), inte skrivas över med en nyinitierad.

### 1. Hämta företagsuppgifterna

Organisationsnumret, tio siffror. Bindestreck går bra — skriptet strippar dem.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/allabolag_fetch.py" 5599999991 > /tmp/bolag.json
```

Läs svaret innan du går vidare. Stämmer `title`, `company_type` och
`status: ACTIVE` med vad användaren tror sig ha? Ett organisationsnummer med
en felslagen siffra ger oftast ett *annat bolag*, inte ett felmeddelande —
`404 för <orgnr>` får du bara när numret inte finns alls.

**Botskydd.** Sajten svarar 202 på täta anrop och skriptet ger upp efter tre
försök. En hämtning per organisationsnummer, spara svaret, kör inte om i
onödan.

### 2. Ta reda på det allabolag inte vet

Sju fält och räkenskapsåret. Fråga dem i ett svep — de blockerar alla samma
sak, och en fråga i taget döljer att hela initieringen hänger på dem.

| Vad | Varför allabolag inte svarar | Flagga |
| --- | --- | --- |
| Momsregistreringsnummer | allabolag säger *om* bolaget är momsregistrerat, inte numret. `SE`+orgnr+`01` är konventionen och brister vid momsgrupp. Kontrollera mot [Skatteverkets momsregisterkontroll](https://skatteverket.se/). | `--vat-number` |
| Redovisningsmetod | Fakturametoden eller kontantmetoden står i inget register. Avgör vilken period momsen hamnar i för allt som sedan bokförs. | `--accounting-method` |
| Säte | Registrerad uppgift hos Bolagsverket. allabolags `municipality` är där bolaget *ligger* — inte alltid detsamma. | `--registered-office` |
| Arbetsställenummer (CFAR) | Källan är SCB. Obligatoriskt först när bolaget har fler än ett arbetsställe (§4.1.1). | `--workplace-number` |
| Teknisk kontaktperson + e-post och telefon | Utses av bolaget, står i inget register alls. | `--technical-contact`, `--technical-contact-email`, `--technical-contact-phone` |
| Räkenskapsårets start och slut | Finns inte på allabolags landningssida. Brutet räkenskapsår är vanligt och syns inte utifrån. | `--fiscal-year-start`, `--fiscal-year-end` |

**Den fråga som gör mest skada obesvarad:** *är detta bolagets första
räkenskapsår?* Är det inte det har bundlen en ingående balans som ska hämtas
från föregående års utgående balans — SIE-fil, årsredovisning eller det
tidigare systemet. Skriptet skriver noll för samtliga konton och säger det
rakt ut i konceptet, men noll är ett påstående om bolagets ställning, inte
ett tomt fält.

Har bolaget bokföring i ett annat system är det förmodligen `bokio-import`
som ska köras efter det här steget, inte en handpåläggning av balanser.

### 3. Visa planen — GRIND

Utan `--write` skriver skriptet ingenting, bara planen:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/initiera-bolag/scripts/init_bolag.py" \
  --allabolag /tmp/bolag.json --out ./bokforing \
  --fiscal-year-start 2026-01-01 --fiscal-year-end 2026-12-31 \
  --accounting-method fakturametoden
```

```
Bolag:      Company AB (559999-9991)
Bundle:     bokforing
Kontoplan:  1242 konton, 99 med momskoppling (BAS 2026)
Räkenskapsår: 2026

Filer:
  chart-of-accounts.md                 65013 B
  fiscal-years/2026.md                  1122 B
  index.md                               283 B
  log.md                                 682 B
  organization.md                       1506 B
  verifications/2026/index.md             60 B

Luckor (6) — lämnas ute ur frontmatter, gissas inte:
  vat_number
      Momsregistreringsnumret. allabolag svarar på *om* bolaget är …
```

Visa för användaren, innan `--write`:

- **Bolaget** som allabolag svarade med — firma, orgnr, bolagsform, status.
  Det är den kontrollen som fångar ett felslaget organisationsnummer.
- **Räkenskapsåret** och att den ingående balansen blir noll, med frågan om
  det är bolagets första år.
- **Luckorna** som skriptet listar, var och en med vad du föreslår: fråga,
  lämna tomt, eller hämta från Skatteverket/Bolagsverket/SCB.
- **Det härledda momsnumret** som ett antagande, aldrig som en uppgift.
  Skriptet skriver det inte utan `--vat-number` — skriv det inte åt det.
- **Filerna** som skapas, och att `chart-of-accounts.md` blir hela BAS-planen
  om 1242 konton, inte de konton bolaget faktiskt använder.

Vänta på ett tydligt ja. Ändrar användaren något — kör om utan `--write` och
visa den nya planen.

**När ingen kan svara** — schemalagt, i en batch, som subagent — är planen
din leverans. Kör inte `--write`. En bundle med gissad redovisningsmetod och
gissad ingående balans ser initierad ut, och varje verifikation som sedan
bokförs ärver felet.

### 4. Skriv

Endast efter ett ja. Samma kommando plus svaren och `--write`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/initiera-bolag/scripts/init_bolag.py" \
  --allabolag /tmp/bolag.json --out ./bokforing \
  --fiscal-year-start 2026-01-01 --fiscal-year-end 2026-12-31 \
  --accounting-method fakturametoden \
  --vat-number SE559999999101 --registered-office Storstad \
  --technical-contact "Erik Karlsson" \
  --technical-contact-email erik.karlsson@company.example \
  --technical-contact-phone "+46 8 123 45 67" \
  --write
```

Skriptet vägrar skriva i en katalog som inte är tom. Får du det felet:
läs vad som ligger där innan du når efter `--force` — det är sannolikt en
bundle som redan finns (se steg 0).

Resultatet:

```
bokforing/
├── index.md
├── log.md
├── organization.md              # §4.1
├── chart-of-accounts.md         # §4.10, 1242 konton
├── fiscal-years/2026.md         # §4.3, nollställd ingående balans
├── verifications/2026/index.md
└── archive/                     # tom, för underlag (§5)
```

### 5. Säg vad som återstår

Bundlen är initierad, inte färdig. Tala om:

- vilka luckor som står kvar i `organization.md` och var uppgiften finns,
- att ingående balansen är noll och vad det förutsätter,
- att `chart-of-accounts.md` är hela baskontoplanen — momskopplingarna följer
  BAS men ska stämmas av mot Skatteverkets blankett innan första
  momsdeklarationen härleds ur dem (§4.13),
- att nästa steg är `bokfor-underlag` för enskilda underlag, eller
  `bokio-import` om bolaget har historik i Bokio.

## Röda flaggor — tanken betyder att du är på väg att gissa

| Tanken | Vad som faktiskt gäller |
| --- | --- |
| "Momsnumret är SE + orgnr + 01, det stämmer alltid." | Bara om bolaget är momsregistrerat, och inte vid momsgrupp. Skriptet skriver det inte utan `--vat-number` — det är avsiktligt. |
| "Fakturametoden är vanligast, jag sätter den." | Metoden avgör vilken period momsen hamnar i för allt som sedan bokförs. Fråga. |
| "`municipality` från allabolag är ju sätet." | Sätet är en registrerad uppgift hos Bolagsverket. De sammanfaller ofta men inte alltid. |
| "Bundlen är tom, ingående balans noll är trivialt sant." | Bara om det är bolagets första räkenskapsår. Annars är noll ett felaktigt påstående om bolagets ställning. |
| "Jag tar innevarande kalenderår som räkenskapsår." | Brutet räkenskapsår är vanligt och syns inte på allabolags landningssida. Fråga. |
| "Katalogen var inte tom, jag kör `--force`." | Läs vad som ligger där först. Ett `--force` över en befintlig bundle skriver över någons räkenskapsinformation. |
| "Kontoplanen har 1242 konton, jag trimmar den till de som behövs." | Trimma inte vid initieringen — vilka konton som behövs vet ingen ännu. Ett oanvänt konto är ofarligt; ett saknat stoppar en kontering. |
| "Jag skriver kontoplanen för hand, den är ju bara en tabell." | 1242 rader för hand blir tappade rader och tappade momskopplingar. Källan är `reference/kontoplan.tsv`. |
| "Användaren är inte tillgänglig, jag kör `--write` och flaggar i efterhand." | Otillgänglig användare betyder att planen är leveransen. Ett flaggat antagande i en skriven bundle är fortfarande skrivet. |

## Vanliga misstag

- Initiera en ny bundle ovanpå en befintlig i stället för att komplettera
  den — kör steg 0 först.
- Skriva `vat_number` med det härledda numret för att fältet såg tomt ut.
- Ange bara `--fiscal-year-start`. Skriptet stoppar, men tanken bakom —
  att slutdatumet är självklart — är fel: brutet räkenskapsår finns.
- Låta `# Contact` stå kvar med enbart allabolags styrelselista. Den
  tekniska kontaktpersonen är någon bolaget utser, inte en styrelseledamot
  som råkar stå överst.
- Lägga rå JSON från allabolag i bundlen. `archive/` är för underlag i
  mottaget skick, och `.md` där är förbjudet (§5) — men en API-dump är
  inte heller ett underlag.
- Redigera `reference/kontoplan.tsv` för ett enskilt bolag. Filen är
  skillens standardkontoplan; bolagsspecifika konton läggs till i
  `chart-of-accounts.md` efter initieringen.

## Filer

| Fil | Vad |
| --- | --- |
| `scripts/init_bolag.py` | Renderar bundlen. `--help` för alla flaggor. Utan `--write` skrivs ingenting. |
| `scripts/test_init_bolag.py` | Självtest: kontoplanens integritet, YAML-citering, och att luckor lämnas tomma. `python3 test_init_bolag.py` från `scripts/`. |
| `reference/kontoplan.tsv` | Kontonummer, namn, momskoppling. 1242 konton, 99 med momskoppling. Tabbseparerad; tredje kolumnen utelämnas när momskoppling saknas. |
