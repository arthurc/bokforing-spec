---
name: bokfor-underlag
description: Use when a bokföringsunderlag ska bokföras i en accounting-bundle — "bokför den här fakturan", "boka upp kvittot", "lägg in underlaget i bokföringen", eller när en faktura, kvitto, lönespecifikation, kontoutdrag eller avtal lämnas över utan närmare instruktion. Använd även när ett redan arkiverat underlag saknar Verification, när en underlag-fil ska arkiveras i bundlen, eller när ett underlag ska periodiseras ("periodisera fakturan", "boka upp förutbetald kostnad").
---

# Bokför underlag

Bokför ett mottaget underlag som en `Verification` enligt Accounting
Knowledge Bundle Specification och arkivera underlaget i bundlens
`archive/` (SPEC §5).

Specifikationen läses från `spec/SPEC.md` i projektet när den finns —
det är den levande versionen — annars från
`${CLAUDE_PLUGIN_ROOT}/reference/SPEC.md`, som följer med pluginen.
Paragrafhänvisningarna nedan (§4.2, §5, …) syftar på den.

## Kärnprincip

**Gissa aldrig. Fråga.** Ett underlag som klassificeras fel eller konteras
på gissning blir felaktig räkenskapsinformation som ligger kvar i sju år
(BFL 7 kap. 1–2 §§). Osäkerhet är inte något som ska lösas med en rimlig
tolkning — den ska ställas som en fråga till användaren.

**Inget skrivs i bundlen innan användaren bekräftat.** Steg 4 är en grind,
inte en avstämning i efterhand. Går användaren inte att nå är förslaget
leveransen — se steg 4.

## Steg

### 0. Hitta bundlen

```bash
grep -rl "^type: Chart of Accounts" --include='*.md' . | head
```

Katalogen som innehåller träffen är bundle-roten. Läs där: `index.md`,
`organization.md` (bl.a. `redovisningsmetod` — fakturametod eller
kontantmetod avgör vilken period momsen hamnar i), `chart-of-accounts.md`,
`fiscal-years/` och `log.md`. Finns ingen bundle — fråga var den ligger.

### 1. Läs underlaget

Läs hela dokumentet, inte bara totalbeloppet. Notera utställare,
mottagare, fakturanummer, fakturadatum, förfallodatum, tjänste-/leveransperiod,
nettobelopp, momsbelopp, momssats, valuta, betalningsvillkor och referenser.
Skriv ner vad som **saknas** i dokumentet — det blir antaganden i steg 4.

Sträcker sig tjänste-/leveransperioden utanför den period beloppet
betalas eller faktureras i — särskilt över ett räkenskapsårsskifte — så
utlöser det periodiseringsfrågan i steg 3.

### 2. Klassificera

| Underlaget är | Koncepttyp | SPEC |
| --- | --- | --- |
| Faktura företaget **mottagit** för ett inköp | `Supplier Invoice` | §4.5 |
| Faktura företaget **ställt ut** för en försäljning | `Customer Invoice` | §4.7 |
| Lönespecifikation för en anställd | `Payslip` | §4.9 |
| Kvitto på kostnad som en anställd/närstående lagt ut privat | `Expense` | §4.11 |
| Kontoutdrag, bokföringsorder, övrigt | inget underlagskoncept — enbart `Verification` | §4.2 |

**Är det oklart vilken rad som gäller — fråga.** Vanliga fall där det inte
går att läsa ut ur dokumentet:

- **Kundfaktura eller leverantörsfaktura?** Vid självfakturering ställer
  motparten ut fakturan i företagets namn — dokumentet ser då ut som en
  mottagen faktura men är en kundfaktura. Leta efter "self billed" på
  dokumentet och kolla vems momsnummer som står som säljarens.
- **Utlägg eller leverantörsfaktura?** Avgörs av vem som betalade, inte av
  hur kvittot ser ut. Företagets kort ≠ utlägg.
- **Anställd eller uppdragstagare?** Avgör om det blir `Payslip` eller
  `Supplier Invoice`.
- **Ett underlag eller flera affärshändelser?** En faktura som både
  fakturerar och kvitterar en betalning är två verifikationer.

Motparten kan behöva ett eget koncept (`Supplier` §4.4, `Customer` §4.6,
`Employee` §4.8). Kolla om det redan finns innan du föreslår ett nytt.

### 3. Slå upp konteringen — i denna ordning

1. **Tidigare bokföring i bundlen är den starkaste källan.** Samma motpart
   eller samma slags affärshändelse har med största sannolikhet bokförts
   förut; följ den konteringen och hänvisa till den.
   ```bash
   grep -rl "<motpartens namn>" bundle/verifications/
   ```
   Läs `# Postings`-tabellen i träffarna. Finns ingen träff på motparten,
   sök på kostnadsslaget ("Billeasing", "Mjukvara licens", "Utlägg").
2. **`chart-of-accounts.md`** — kontot måste finnas i kontoplanen, och dess
   `VAT Declaration Field` avgör vilken ruta momsen hamnar i.
3. **Referensbundles under `.okf/`, om projektet har några.** Kolla vad som
   finns (`ls .okf/`) innan du förlitar dig på dem — de är inte del av
   pluginen och saknas i många projekt.
   - En konteringshandbok har konteringsexempel per ämne under
     `chapters/`: `forsaljning`, `inkop`, `fakturorna`, `momsen`,
     `anstallda`, `formaner`, `bilen`, `leasing-och-avbetalningskop`,
     `inventarier`, `interimsposter`, `representation`, `utlandsk-valuta`,
     `skatter`, `banken`, `kontokort`, `semester`, `avstamning`.
   - En lagtextsamling (BFL, ÅRL, ABL, BFN:s allmänna råd) svarar på
     principfrågor snarare än konteringsfrågor.

Går konteringen inte att härleda ur någon av dessa — **fråga, kontera inte
på egen bedömning.**

#### Periodisering — hör hela beloppet till den här perioden?

Avser underlaget en period som sträcker sig utanför den period det
betalas eller faktureras i, ska intäkten eller kostnaden hamna i den
period den är hänförlig till (ÅRL 2 kap. 4 §). Typfall: försäkringspremier,
hyror, abonnemang, licens- och supportavtal, förskottsfakturor, årsavgifter,
upplupna räntor och löner. Det blir ett `Accrual`-koncept (SPEC §4.14)
vid sidan av underlagskonceptet — inte i stället för det.

| Läget | `accrual_kind` | Balanskonto |
| --- | --- | --- |
| Betald nu, avser senare period | `prepaid_expense` | 1700-serien |
| Avser denna period, betalas senare | `accrued_expense` | 2900-serien |
| Erhållen nu, intjänas senare | `deferred_income` | 2900-serien |
| Intjänad nu, erhålls senare | `accrued_income` | 1700-serien |

Tre saker som **inte** går att läsa ut ur dokumentet och alltså ska frågas:

- **Ska det periodiseras alls?** K2:s femtusenkronorsregel (BFNAR 2016:10
  p. 2.4) och regeln om årligen återkommande utgifter (p. 7.9) låter ett
  mindre företag låta bli. Vilken regel företaget tillämpar, och
  väsentlighetsbedömningen, är användarens — inte din. Åberopas en
  förenklingsregel skapas inget `Accrual`; bedömningen dokumenteras då i
  verifikationens beskrivning i stället.
- **Nu eller vid bokslutet?** Uppbokningen kan göras direkt när underlaget
  bokförs eller samlat vid bokslutet. Skjuts den upp: skriv det i `log.md`,
  annars tappas den bort.
- **Hur delas beloppet upp?** Linjärt per månad (`release_method:
  straight_line`) är vanligast men inte givet — förbrukningen kan vara ojämn.

**Momsen periodiseras aldrig.** Den följer redovisningsmetoden och
redovisas i sin helhet i den period fakturan hör till. `amount` på
`Accrual` är exklusive moms.

Handboken under `.okf/` har kapitlet `interimsposter` om det finns.

### 4. Bekräfta med användaren — GRIND

Grinden omfattar **varje skrivning inne i bundlen**: verifikationen,
underlagskonceptet, motpartskonceptet, arkivfilen, index- och
logguppdateringar. Inte bara verifikationen, och inte bara det som ändrar
saldon. Att kopiera in en fil i `archive/` och peka om ett `resource` är
också en ändring i någons räkenskapsinformation.

Visa, innan någon fil skrivs:

- koncepttyp och motpart
- `verification_number` (nästa lediga i räkenskapsåret) och räkenskapsår
- `transaction_date`, `recorded_date`, `amount`
- hela `# Postings`-tabellen med kontonummer, kontonamn, debet, kredit —
  och vilken tidigare verifikation eller handbokskälla konteringen följer
- **periodisering**, när perioden sträcker sig utanför bokföringsperioden:
  antingen `accrual_kind`, balanskonto, `period_start`/`period_end` och hela
  `# Schedule`-tabellen — eller, om ingen periodisering föreslås, vilken
  förenklingsregel som åberopas och varför
- varje **antagande** (saknat förfallodatum, antagen momssats, antagen
  tjänsteperiod) explicit som antagande
- listan över filer som skapas och ändras

Vänta på ett tydligt ja. Ändrar användaren något — visa om hela förslaget.

#### När ingen kan svara

Kör du utan någon som kan svara — schemalagt, i en batch, som subagent,
eller för att användaren lämnat körningen — så är **förslaget din
leverans**. Det är inte att misslyckas med uppgiften; det är uppgiften.
En kontering som ingen godkänt är inte bokförd, den är påhittad, och en
bundle som fylls med påhittade verifikationer är sämre än en bundle som
saknar dem: den ser färdig ut.

Leverera hela steg 4-underlaget, med de obesvarade frågorna som en
numrerad lista överst, och skriv ingenting i bundlen. Gör förslaget
komplett nog att bokföras rakt av när svaret kommer — konton, belopp,
datum, filnamn, sökvägar. Nästa körning eller nästa människa ska inte
behöva göra om utredningen.

Att flagga ett antagande i efterhand är inte samma sak som att fråga i
förväg. Står antagandet i en bokförd verifikation är det bokfört; noten
intill ändrar inte det, den dokumenterar bara att du visste. Frågan ska
ställas medan svaret fortfarande kan ändra vad som skrivs.

### 5. Skriv

Endast efter ett ja i steg 4. Kom du hit utan ett ja är steg 4 din
slutpunkt.

1. **Arkivera underlaget först** — kopiera filen i mottaget skick till
   `archive/<typ>/<år>/<filnamn>`, t.ex.
   `archive/leverantorsfakturor/2026/KV-88213.pdf`. Aldrig `.md` under
   `archive/` (SPEC §5). Filnamnet återanvänder underlagets affärsidentitet.
2. **Underlagskonceptet** enligt tabellen i steg 2, med `resource` som
   bundle-relativ sökväg till arkivfilen och `verification:` tillbaka till
   verifikationen.
3. **Motpartskonceptet** om det saknades.
4. **Verifikationen** i `verifications/<räkenskapsår>/V###.md` enligt
   SPEC §4.2: alla obligatoriska fält, `supporting_documents` med sökväg
   till arkivfilen, `retention_until` = `recorded_date` + 7 år,
   `# Postings`, `# Supporting Documents`, `# Citations`.
5. **`Accrual`-konceptet** om periodisering beslutades i steg 3, i
   `accruals/<år>/<vad-som-periodiseras>-<startperiod>.md` enligt SPEC
   §4.14: `source_verification` till uppbokningsverifikationen,
   `source_document` till underlagskonceptet, `status: open` så länge någon
   rad i `# Schedule` saknar verifikation, och `# Basis` med
   väsentlighetsbedömningen. Upplösningen i varje period är en egen
   verifikation som fylls i på sin `# Schedule`-rad när den bokförs.
   Skjuts uppbokningen till bokslutet finns inget `Accrual` ännu — då är
   `log.md`-posten det enda som bär beslutet vidare.
6. **Uppdatera**: `fiscal-years/<år>.md` (`verification_number_range`),
   `verifications/<år>/index.md`, berörda `index.md` i underlags-,
   motparts- och `accruals/`-katalogerna, och `log.md` med en
   `**Addition**`-post som anger vad som bokfördes, konteringen, vilken
   tidigare verifikation den följer, periodiseringsbeslutet (inklusive ett
   uppskjutet sådant) och kvarstående antaganden.
7. **Härledda sammanställningar** (`huvudbok.md`, momsdeklarationer) —
   uppdatera dem, eller notera uttryckligen i dem att de inte omfattar den
   nya verifikationen. Lämna dem inte tyst inaktuella.

## Får aldrig gissas — fråga i stället

| Fråga | Varför den inte kan antas |
| --- | --- |
| Kundfaktura eller leverantörsfaktura? | Självfakturering vänder på rollerna. |
| Utlägg eller företagsbetalning? | Avgör 2890/1610 mot 2440, och om kvittot är obligatoriskt (SPEC §4.11). |
| Vilket kostnadskonto? | Inget entydigt tidigare fall och ingen entydig handboksförebild = fråga. |
| Momssats, omvänd skattskyldighet, EU-/exportmoms? | Framgår ofta inte av dokumentet. |
| `transaction_date` när fakturadatum ≠ leverans/tjänsteperiod? | Redovisningsmetoden avgör; läs `organization.md`. |
| Ska beloppet periodiseras? | Femtusenkronorsregeln och regeln om årligen återkommande utgifter är valfria förenklingar med en väsentlighetsbedömning bakom sig — företagets val, inte ditt (SPEC §4.14). |
| Hur andelarna fördelas över perioderna? | Linjärt är vanligast, inte givet. Ojämn förbrukning ger ojämn `# Schedule`. |
| Vilket räkenskapsår, om datumet ligger utanför de registrerade? | Underlaget kan redan vara bokfört i ett år som inte importerats i bundlen. Att bokföra det i ett öppet år ger både fel period och dubbelbokföring. |
| Verifikationsnummer, om bundlen importerar från ett externt system (SIE4)? | Nummer tilldelat här kan krocka med systemets. Fråga, och notera dubbelbokföringsrisken i både verifikationen och `log.md`. |

## Röda flaggor — tanken betyder att du är på väg att gissa

| Tanken | Vad som faktiskt gäller |
| --- | --- |
| "Användaren är inte tillgänglig, så jag skriver och flaggar i stället." | Otillgänglig användare betyder att förslaget är leveransen, inte att bekräftelsen kan hoppas över. |
| "Konteringen är så väl belagd att bekräftelsen bara är en formalitet." | Grinden gäller själva bokföringen, inte hur säker du är på den. Sex tidigare likadana verifikationer gör konteringen trolig, inte godkänd. |
| "Arkivering är ofarligt, det kan jag göra utan att fråga." | Arkivering ändrar bundlen och binder ett underlag till ett koncept. Den ligger innanför grinden. |
| "Det vore fel att lämna affärshändelsen obokförd." | En obokförd affärshändelse är synlig och lätt att åtgärda. En felbokförd är osynlig och ligger kvar i sju år. |
| "Det är rimligtvis en leverantörsfaktura." | Rimligtvis är en gissning. Fråga. |
| "Jag använder 6110 eftersom det brukar vara det." | Brukar är ingen källa. Sök tidigare bokföring, annars fråga. |
| "Momsen är 25 % — det är standardsatsen." | Omvänd skattskyldighet, EU-handel, export och reducerade satser ser likadana ut på en faktura som inte säger något. |
| "Beloppet är litet, femtusenkronorsregeln täcker det." | Regeln är en möjlighet företaget kan välja, inte en automatik — och väsentligheten bedöms på posterna tillsammans, inte en i taget. Fråga. |
| "Fakturan avser tolv månader, men jag bokför hela kostnaden nu och periodiserar vid bokslutet." | Kan vara helt rätt — men det är ett beslut, inte en default. Fråga, och skriv in det i `log.md` om det skjuts upp. |
| "Förfallodatum saknas, jag antar 30 dagar." | Antagandet kan vara rätt — men det ska stå som antagande i steg 4, inte tyst i en fil. |
| "Verifikationen är klar." | Inte förrän arkivfilen finns på plats och sökvägen löser ut.  |

## Vanliga misstag

- Konceptdokument (`.md`) placerade under `archive/` — förbjudet (SPEC §5).
- `resource` som pekar ut ur bundlen (`../../Downloads/...`) i stället för
  på arkivfilen.
- Kontering som inte balanserar, eller konton som inte finns i
  `chart-of-accounts.md`.
- `log.md` och `index.md` inte uppdaterade — bundlen slutar berätta sin
  egen historik.
- Debet/kredit spegelvända på momskontot: ingående moms (2640/2641) debet
  vid inköp, utgående moms (2611) kredit vid försäljning.
- Momsen periodiserad tillsammans med beloppet. Den följer
  redovisningsmetoden, inte periodiseringsprincipen.
- `Accrual` med balanskonto ur fel serie: 1700 för `prepaid_expense` och
  `accrued_income`, 2900 för `accrued_expense` och `deferred_income`.
- `# Schedule`-andelarna summerar inte till `amount`, eller `status:
  released` med tomma verifikationsrutor kvar.
