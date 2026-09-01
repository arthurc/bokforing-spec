---
name: huvudbok
description: Use when någon vill se bokföringen sammanställd per konto för en period — "visa huvudboken", "resultatrapport för 2026", "hur ser saldona ut i juni", "vad ligger på konto 6110", "gör en rapport av bokföringen", "kontoutdrag ur bundlen". Bygger en webbsida med varje konto som har belopp: namn, ingående balans, utgående balans, och verifikationerna bakom, och publicerar den som en artefakt.
---

# Huvudbok

Sammanställ en accounting-bundles verifikationer per konto för en vald period
och publicera resultatet som en artefakt — en webbsida där varje konto visas
med namn, ingående balans och utgående balans, och kan fällas ut för att visa
de ingående verifikationerna med datum, beskrivning, debet och kredit.

Rapporten är **härledd**, inte bokförd. Den skriver ingenting i bundlen och
ändrar ingenting i den. Den är heller inte ett bokslut — en obalans eller ett
konto som ser fel ut ska rapporteras, inte justeras bort.

## Steg

### 1. Hitta bundlen

```bash
grep -rl "^type: Chart of Accounts" --include='*.md' . | head
```

Katalogen som innehåller träffen är bundle-roten. Hittas ingen — fråga var
bundlen ligger. Skriptet läser kontoplanen, `organization.md` (för
bolagsnamnet), `fiscal-years/` och alla `Verification`-koncept den hittar
under roten; `archive/` hoppas över.

### 2. Bestäm perioden — fråga hellre än anta

Perioden avgör vad som hamnar i ingående balans och vad som blir periodens
rader. Är den inte angiven, **fråga**. Ett rimligt förslag att fråga om är
det räkenskapsår som är `status: open` i `fiscal-years/`:

```bash
grep -l "^status: open" bundle/fiscal-years/*.md | xargs grep -h "_date:"
```

Ett halvår, en månad eller ett kvartal är lika giltiga perioder — men de är
användarens val, inte ditt.

### 3. Kör skriptet

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/huvudbok/scripts/huvudbok.py" <bundle-rot> \
  --from 2026-01-01 --to 2026-12-31 --out huvudbok-2026.html
```

Skriptet skriver HTML-filen och en rad om hur många konton och
konteringsrader som kom med. Lägg filen utanför bundlen — den är en
sammanställning, inte räkenskapsinformation, och ska inte ligga bland
koncepten.

Så räknas det, och så ska det förklaras om någon frågar:

- **Ingående balans** = räkenskapsårets `# Opening Balances` för det år som
  omsluter periodstarten, plus alla konteringar från räkenskapsårets början
  fram till dagen före periodstart. Resultatkonton saknar normalt post i
  `# Opening Balances` och börjar därför på noll vid årets början.
- **Utgående balans** = ingående balans plus periodens konteringar.
- **Debet räknas positivt, kredit negativt** — samma teckenkonvention som
  `# Opening Balances` i SPEC §4.3, där ett kreditsaldo står med minustecken.
- Ett konto kommer med om det har ingående balans, utgående balans eller
  konteringar i perioden.

### 4. Läs varningarna innan du visar rapporten

| Varning | Vad den betyder |
| --- | --- |
| `utgående balanser summerar till X, inte noll` | Bokföringen balanserar inte. Antingen är en verifikation obalanserad, eller så saknar räkenskapsårets `# Opening Balances` konton. Rapportera det — sidan visar det också som "obalans" i balanskontrollen. |
| `inget räkenskapsår täcker periodstarten` | Ingående balans är då summan av alla verifikationer före perioden, utan förankring i ett bokslut. Säg det. |
| Färre konton än väntat | Verifikationer utan `# Postings`-tabell eller med kontonummer skriptet inte känner igen tas inte med. Kontrollera med `grep -L "# Postings" bundle/verifications/*/*.md`. |

Dölj aldrig en obalans genom att välja en annan period.

### 5. Publicera som artefakt

Publicera den genererade filen med `Artifact`-verktyget:

- `file_path` — HTML-filen från steg 3
- `title` — sätts av sidan själv (`Huvudbok <bolagsnamn>`); ingen `title`-parameter behövs
- `description` — en mening: bolag och period, t.ex. "Huvudbok för Company AB, 2026-01-01 – 2026-12-31."
- `favicon` — `"📒"` vid första publiceringen. Uppdateras rapporten senare
  (samma filnamn, eller `url` till samma artefakt) — utelämna `favicon`.

Ska en tidigare publicerad huvudbok uppdateras i stället för att en ny
skapas, skicka artefaktens `url`. Ny period = ny artefakt.

Lämna över länken och nämn perioden, antalet konton och balanskontrollens
utfall. Sidan behöver ingen förklaring i övrigt — den bär sin egen.

## Underhåll

`scripts/huvudbok.py --selftest` bygger en liten bundle i en temp-katalog och
kontrollerar periodavgränsningen, ingående balans, teckenkonventionen och att
dubbel bokföring summerar till noll. Kör det efter varje ändring i skriptet.

## Vanliga misstag

- Perioden gissad i stället för frågad. Fel period ger en rapport som ser rätt ut.
- HTML-filen skriven inne i bundlen. Sammanställningar hör inte hemma bland koncepten.
- Obalansen nämnd i förbifarten, eller inte alls. Den är rapportens viktigaste
  upplysning — en huvudbok som inte summerar till noll säger att bokföringen
  har ett fel, inte att rapporten har det.
- Rapporten beskriven som ett bokslut eller en årsredovisning. Den är en
  sammanställning av löpande bokföring, inget annat.
- Belopp omtolkade för hand efteråt. Stämmer inte en siffra ligger felet i
  verifikationen eller i räkenskapsårets ingående balanser — leta där.
