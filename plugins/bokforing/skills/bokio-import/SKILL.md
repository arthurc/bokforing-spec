---
name: bokio-import
description: Använd när bokföring ska hämtas ur Bokio och skrivas in i en accounting-bundle — "importera från Bokio", "hämta verifikationerna ur Bokio", "synka kontoplanen/kunderna/leverantörerna från Bokio", "bygg en bundle av vårt Bokio-konto", eller när användaren nämner Bokios API, en integrationstoken, companyId, journal entries eller en SIE-fil från Bokio. Använd även när en befintlig bundle ska uppdateras med nya verifikationer eller fakturor från Bokio, och när frågan är vad i Bokio som går respektive inte går att representera enligt spec:en.
---

# Importera från Bokio

Hämta räkenskapsinformation ur Bokios Company API och skriv den som koncept
i en Accounting Knowledge Bundle enligt spec:en.

Specifikationen läses från `spec/SPEC.md` i projektet när den finns — det är
den levande versionen — annars från `${CLAUDE_PLUGIN_ROOT}/reference/SPEC.md`.
Paragrafhänvisningarna nedan (§4.2, §5, …) syftar på den.

Den fullständiga fält-för-fält-mappningen ligger i
[`reference/faltmappning.md`](reference/faltmappning.md). **Läs den innan du
mappar något** — den säger vilket Bokio-fält som blir vilket spec-fält, och,
viktigare, vilka spec-fält som inte har någon källa i Bokio alls.

## Kärnprincip

**En import är en översättning, inte en kopia.** Bokios datamodell och
spec:ens koncepttyper överlappar men sammanfaller inte. Fem koncepttyper har
ingen källa i API:et över huvud taget, och några obligatoriska fält —
`Verification.recorded_date`, `Supplier Invoice.received_date` — finns inte
heller. Ett fält som fylls med närmaste tillgängliga värde för att raden ska
bli ifylld är inte importerad räkenskapsinformation, det är påhittad sådan
som ser importerad ut.

**Luckan ska synas.** Ett fält utan källa lämnas tomt och redovisas, eller
fylls efter att användaren svarat. Aldrig tyst.

**Skriv aldrig till Bokio.** Importen är enkelriktad. Company API kan skapa
verifikationer, fakturor och betalningar — den här skillen gör inget av det.
Använd bara `:read`-scopes.

**Inget skrivs i bundlen innan användaren bekräftat.** Steg 4 är en grind.

## Steg

### 0. Förutsättningar

```bash
export BOKIO_TOKEN=<integrationstoken>
export BOKIO_COMPANY_ID=<uuid ur app.bokio.se-URL:en>
```

Token skapas i Bokio-appen under Integrationer (privat integration). Be
användaren sätta variablerna själv — läs, echo:a eller skriv aldrig ut
token, och lägg den inte i en fil i repot.

Kolla åtkomsten med en liten request innan du planerar en stor import:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/bokio-import/scripts/bokio_fetch.py" company-information
```

401 betyder ogiltig eller utgången token; 403 att integrationen saknar
scopet. Behövda scopes: `company-information:read`, `fiscal-years:read`,
`chart-of-accounts:read`, `journal-entries:read`, `uploads:read`,
`customers:read`, `invoices:read`, `suppliers:read`,
`supplier-invoices:read`, `sie:read`.

### 1. Hitta bundlen och bestäm omfattningen

```bash
grep -rl "^type: Chart of Accounts" --include='*.md' . | head
```

Katalogen med träffen är bundle-roten. Finns ingen — fråga var bundlen ska
ligga; skapa den inte på eget bevåg.

Fråga vad importen omfattar innan du hämtar:

- **Vilket räkenskapsår?** Hela historiken eller ett år. Bokios företag kan
  ha år som ligger före bundlens första.
- **Bygga nytt eller fylla på?** Har bundlen redan verifikationer måste du
  veta vilka `verification_number` som redan finns — annars blir importen
  en dubbelbokföring. Läs `fiscal-years/*.md` och `verifications/`.
- **Bara stamdata eller allt?** Kontoplan, kunder och leverantörer är
  ofarliga att importera först och gör resten läsbar.

### 2. Hämta

`scripts/bokio_fetch.py` sköter auth, sidbrytning (100/sida) och 429-retry.
Skriv svaren till en arbetskatalog utanför bundlen — rådata är inte koncept
och ska inte ligga i bundlen förrän det är arkivmaterial (§5).

```bash
B="python3 ${CLAUDE_PLUGIN_ROOT}/skills/bokio-import/scripts/bokio_fetch.py"
$B company-information            > raw/company.json
$B fiscal-years                   > raw/fiscal-years.json
$B chart-of-accounts              > raw/accounts.json
$B suppliers                      > raw/suppliers.json
$B customers                      > raw/customers.json
$B journal-entries --query 'date>=2026-01-01&&date<=2026-12-31' > raw/journal-entries.json
$B supplier-invoices              > raw/supplier-invoices.json
$B invoices                       > raw/invoices.json
$B uploads                        > raw/uploads.json
```

Hämta i den ordningen: motparter före fakturor, fakturor före
verifikationer. Du behöver dem för att kunna knyta ihop stegen i 3.

**Filtersyntax:** `fält operator värde`, kombinerat med `&&` eller `||` —
`date>=2026-01-01&&date<=2026-12-31`. Skriptet URL-kodar åt dig, så skriv
uttrycket oskyddat innanför enkelfnuttar. Vilka fält som går att filtrera
på skiljer sig per endpoint; `journal-entries` tar `date`, `title` och
`journalEntryNumber`.

**SIE-filen** behövs för `Fiscal Year`s balanser, som inte finns i
JSON-API:et. Hämta den per räkenskapsår och lägg den i arkivet:

```bash
$B "sie/<fiscalYearId>/download" --out <bundle>/archive/import/<år>-sie4.se
```

### 2b. Räkna anropen innan du gör dem

[Bokios rate limit](https://docs.bokio.se/reference/rate-limits) är **200
requests per rullande 60 s per token** — 3,3 per sekund. Det är gott om
utrymme för listhämtningarna i steg 2 (tiotalet requests) och trångt så
snart något görs *per objekt*. Skriptet stryper sig själv till ~3/s och
backar av på 429, men det räddar bara den som räknat: en import som behöver
1 200 anrop tar sex minuter oavsett hur snällt de fördelas, och en som
körs i tre parallella processer slår i taket direkt eftersom budgeten
räknas per token, inte per process.

Räkna alltså ihop budgeten före steg 3 och visa den i steg 4:

| Vad | Requests |
| --- | --- |
| Listorna i steg 2 | ≈ 8 + en per påbörjat 100-tal poster i varje lista |
| `payment_date` per kundfaktura (`invoices/{id}/payments`) | **en per faktura** |
| Nedladdning av varje upload/faktura-PDF till `archive/` | **en per fil** |
| SIE-fil | en per räkenskapsår |

De två feta raderna är de som spränger budgeten. Vid 500 fakturor med
underlag blir det ~1 000 requests, dvs. fem minuters hämtning. Det är
acceptabelt — men det ska vara ett beslut användaren fått se, inte något
som upptäcks halvvägs. Två sätt att krympa den:

- **Hämta inte `payment_date` för fakturor som inte behöver det.** Är
  `status` `published` eller `overdue` är fakturan obetald och det finns
  ingen betalningspost att hämta.
- **Ladda ner underlag bara för de verifikationer importen faktiskt
  skriver.** `GET /uploads` ger hela listan med `journalEntryId` i ett
  fåtal anrop; nedladdningen är det som kostar.

**Serialisera.** Kör aldrig hämtningarna parallellt. Utöver rate limit har
Bokio en separat samtidighetsspärr som ger 429 — och ibland 409 eller 500 —
utan att sätta rate limit-huvudena. Skriptet backar av exponentiellt på
alla tre, men bara om anropen går genom en process i taget.

**Avbrott.** Slår importen ändå i taket mitt i steg 5 står bundlen
halvskriven. Skriv därför arkivfilerna och koncepten i den ordning steg 5
anger, och notera i `log.md` hur långt importen kom — en avbruten import
som går att återuppta är en olägenhet, en avbruten import som ingen vet
omfattningen av är en avstämning.

### 2c. Komplettera ur allabolag

Några av `Organization`s fält (§4.1) finns inte i Bokios API men går att
hämta från [allabolag.se](https://allabolag.se/) — `https://allabolag.se/`
plus organisationsnumret med tio siffror utan bindestreck:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/allabolag_fetch.py" 5567037485
```

Det stänger `f_tax_status`, `workplace_address` och frågan om bolaget alls
är momsregistrerat, och ger styrelse och firmatecknare till `# Contact`.
För **leverantörer** är `f_tax_status` (§4.4.1) det som gör uppslagningen
värd besväret: saknar en tjänsteleverantör F-skatt kan
Skatteförfarandelagen kräva att företaget gör skatteavdrag vid betalning.

Tre saker att hålla isär:

- **`vat_number` är fortfarande en härledning.** allabolag svarar på *om*
  bolaget är momsregistrerat, inte på numret. `SE`+orgnr+`01` stämmer för
  de allra flesta men inte för momsgrupper. Skriv det som ett antagande i
  steg 4 och hänvisa till Skatteverkets momsregisterkontroll.
- **allabolag är UC:s återgivning, inte registret.** För en uppgift som ska
  ligga i sju års räkenskapsinformation är den en indikation. Bolagsverket
  gäller för säte och firma, SCB för CFAR-nummer, Skatteverket för moms och
  F-skatt.
- **Botskydd.** Sajten svarar 202 på täta anrop och skriptet ger upp efter
  tre försök. En hämtning per organisationsnummer, spara svaret, och slå
  bara upp de leverantörer du faktiskt behöver `f_tax_status` för — inte
  hela listan för säkerhets skull. Utländska leverantörer som identifieras
  via `vatNumber` finns inte där alls.

### 3. Mappa

Läs [`reference/faltmappning.md`](reference/faltmappning.md) och gå igenom
koncepttyp för koncepttyp. Tre saker som inte framgår av tabellerna:

1. **Bygg det omvända indexet journalEntryId → motpart.** `Verification`
   har inget `counterparty` i Bokio. Kopplingen finns bara åt andra hållet,
   och från **tre** håll, inte två:
   - `supplierInvoice.journalEntryRef.id` → leverantören
   - `invoice.journalEntryRef.id` → kunden
   - `GET /invoices/{id}/payments` → `journalEntryRef.id` → kunden. Den
     tredje är lätt att missa och ger motparten till *betalnings*­verifika­tio­n­erna,
     som annars ser motpartslösa ut. Ta med den — skillnaden är hämtad
     uppgift i stället för gissad.

   Verifikationer som inget av de tre pekar på — bankavgifter, löner,
   betalningar av leverantörsfakturor (de har inga betalningsposter i
   API:et), bokföringsorder — har ingen motpart i Bokio. `title` innehåller
   den ofta i klartext; att läsa ut den därifrån är en gissning även när
   den är uppenbart riktig. "Betalning KV-88213" säger vem fakturan kom
   från, men kopplingen är gjord av dig, inte av datat.
2. **Kontonamn kommer från kontoplanen.** `journalEntry.items[]` har bara
   kontonummer. `# Postings` ska ha nummer och namn — joina mot
   `chart-of-accounts` på `account`.
3. **Ladda ner uploads och lägg dem i arkivet, inte bara länka.** En
   `Verification`s `resource` ska peka på en fil i bundlen (§5):
   ```bash
   $B "uploads/<uploadId>/download" --out <bundle>/archive/<typ>/<år>/<namn>
   ```
   Filnamnet återanvänder underlagets affärsidentitet (fakturanumret), inte
   Bokios UUID. Aldrig `.md` under `archive/`.

Vad som inte är gissningsbart och alltså ska bli en fråga eller en
redovisad lucka:

| Fält | Varför det inte kan härledas |
| --- | --- |
| `Verification.recorded_date` | Bokio har ett enda `date`. Att sätta bokföringsdatum = affärsdatum påstår att allt bokfördes samma dag det hände. |
| `Verification.counterparty` för icke-fakturaposter | Finns inte. `title` är fritext, inte en motpartsuppgift. |
| `Supplier Invoice.received_date` | Ankomstdatum styr när bokföringsskyldigheten inträdde (§4.5.1); fakturadatum är underordnat. Sparas inte av Bokio. |
| `Supplier Invoice.sequence_number` | Reskontrans löpnummer finns inte. Ett nummer du tilldelar vid importen är importens, inte reskontrans. |
| `Organization.vat_number` | allabolag säger *om* bolaget är momsregistrerat, inte numret. `SE`+orgnr+`01` är en konvention som brister vid momsgrupper. |
| `Organization.registered_office`, `technical_contact` | Sätet står hos Bolagsverket, inte hos Bokio eller allabolag. Kontaktpersonen utses av bolaget och står i inget register alls — fråga. |
| `Organization.workplace_number` (CFAR) | allabolag har numret i arbetsställevyn men inte på landningssidan, och huvudkontorets är tomt. Källan är SCB. |
| Momsruta per konto (§4.10) | Ingen källa i Bokio. Efterarbete, inte import. |
| `payment_status` för `underPaid`/`credited` | Bokios åtta statusvärden mot spec:ens två. Delbetald är varken `paid` eller `unpaid`. |

### 4. Redovisa och bekräfta — GRIND

Visa, innan någon fil skrivs i bundlen:

- **Omfattning:** räkenskapsår, antal per koncepttyp (t.ex. 189
  verifikationer, 34 leverantörer, 12 kunder), och vilka filer som skapas
  respektive ändras.
- **Luckorna, som en numrerad lista.** Varje spec-obligatoriskt fält utan
  källa i Bokio, med vad du föreslår: fråga, lämna tomt, eller härleda —
  och i så fall hur.
- **Antagandena.** Varje ≈-mappning i faltmappning.md som du faktiskt
  använt: härledd `amount`, härledd `payment_status`, härlett
  `fiscal_year_id`. `retention_until` räknas ur `recorded_date` + 7 år
  (spec §4.2.1), inte ur transaktionsdatumet — den hänger alltså på samma
  obesvarade fråga.
- **Dubbelbokföringsrisken.** Vilka `verification_number` som redan finns i
  bundlen och hur du undviker krock.
- **Anropsbudgeten** från steg 2b: hur många requests hämtningen kräver och
  ungefär hur lång tid den tar vid 200/60 s. Tar den mer än några minuter
  ska användaren få välja bort per-objekt-anropen i stället för att sitta
  och vänta på något hen inte bett om.
- **Ett fullständigt exempel** — en verifikation med sin `# Postings`, en
  leverantörsfaktura — så att användaren ser formen och inte bara siffrorna.

Vänta på ett tydligt ja. Ändrar användaren något — visa om.

**Vad `recorded_date` ska bli när frågan ställs.** Rekommendera
importdagen, och skriv ut att Bokios ursprungliga registreringsdatum inte
går att få tag på. Det är sant: importen är en överföring av
räkenskapsinformation till annan form (BFL 7 kap. 6 §), och importdagen är
den dag *den här* representationen upprättades. Rekommendera aldrig
transaktionsdatumet — det är inte ett okänt datum utan ett känt felaktigt,
och det gör dessutom `retention_until` (= `recorded_date` + 7 år) för kort.
Har användaren kvar sitt Bokio-konto kan det riktiga datumet finnas i en
SIE-fil med `#VER`; nämn det, men vänta inte på det.

**Slå ihop frågan när luckan är systematisk.** Saknar ett obligatoriskt
fält källa för *varje* post — `recorded_date` gör det alltid, eftersom
Bokio inte har fältet — är det inte hundra frågor utan en: vad ska stå där,
för hela importen? Ställ den en gång, överst, och säg vad den blockerar.
En lista med en fråga per verifikation ser grundlig ut men är obesvarbar,
och den döljer att hela importen hänger på ett enda beslut.

#### När ingen kan svara

Kör du utan någon som kan svara — schemalagt, i en batch, som subagent — är
**redovisningen din leverans**. Skriv ingenting i bundlen. En importerad
bundle där luckorna fyllts med rimliga värden är sämre än ingen bundle: den
ser komplett ut, och sju års räkenskapsinformation vilar på gissningar som
ingen längre kan skilja från hämtade uppgifter.

Leverera hela steg 4-underlaget med de obesvarade frågorna överst, och gör
det komplett nog att köras rakt av när svaret kommer.

### 5. Skriv

Endast efter ett ja. I den här ordningen, så att varje länk pekar på något
som redan finns:

1. `organization.md` (§4.1) och `chart-of-accounts.md` (§4.10)
2. `fiscal-years/<år>.md` (§4.3) — och om SIE-filen hämtats,
   `# Opening Balances` / `# Closing Balances` ur `#IB`/`#UB`
3. `suppliers/<slug>.md` (§4.4), `customers/<slug>.md` (§4.6)
4. Arkivfilerna: uploads och faktura-PDF:er till `archive/` (§5)
5. `supplier-invoices/<år>/<fakturanr>.md` (§4.5),
   `customer-invoices/<år>/<fakturanr>.md` (§4.7)
6. `verifications/<år>/<nr>.md` (§4.2) med `# Postings`,
   `# Supporting Documents`, `# Citations`
7. `index.md` per katalog, och `log.md` med en `**Addition**`-post som
   anger: att detta är en import från Bokios Company API, vilken
   omfattning, vilka fält som härletts och hur, och vilka som lämnats
   tomma för att Bokio saknar dem.

`log.md`-posten är inte bokföring — den är det enda stället där någon om
tre år kan se vilka uppgifter som kom ur Bokio och vilka som fylldes i
efteråt. Skriv den utförligt.

Koncept som inte kan skrivas spec-enligt skrivs inte alls. Ett `Fiscal
Year` utan balanser eller en `Expense` utan `employee` och kvitto är inte
ett halvfärdigt koncept, det är ett ogiltigt — säg att det saknas i stället.

## Röda flaggor — tanken betyder att du är på väg att gissa

| Tanken | Vad som faktiskt gäller |
| --- | --- |
| "`recorded_date` sätter jag till `date`, det är närmast." | Då påstår bundlen att varje affärshändelse bokfördes samma dag den inträffade. Fråga. |
| "Motparten står ju i `title`." | `title` är fritext som någon skrivit i Bokio. Att parsa fram en motpart ur den är en gissning, inte en hämtad uppgift. |
| "Momsnumret är SE + orgnr + 01." | Bara om bolaget är momsregistrerat, och inte vid momsgrupp. allabolag svarar på om — inte på vilket. |
| "allabolag säger att de har F-skatt, då skriver jag `approved`." | allabolag är UC:s återgivning och kan släpa. För ett fält som avgör om företaget ska göra skatteavdrag: skriv det, men skriv också varifrån det kom. |
| "Jag slår upp alla trettio leverantörer på allabolag." | Botskydd, 202, och 360 kB per sida från någon annans server. Slå upp dem du behöver `f_tax_status` för. |
| "`location.municipality` är ju sätet." | Det är där bolaget ligger. Sätet är en registrerad uppgift hos Bolagsverket och sammanfaller inte alltid. |
| "Jag mappar `underPaid` till `unpaid`, det är närmast." | Delbetald är ett tredje tillstånd. Fråga hur det ska skrivas. |
| "Kontoplanen är BAS, jag fyller i momsrutorna själv." | Momsrutemappningen avgör vad som hamnar i en momsdeklaration. Den är efterarbete med användaren, inte något importen härleder. |
| "Utläggen syns som poster mot 2890, jag skriver `Expense`-koncept." | `Expense` kräver `employee` och kvittot som `resource`. Vem som lagt ut finns inte i API:et. |
| "Den här verifikationen fanns redan, jag skriver över." | En befintlig verifikation kan vara rättad eller kompletterad i bundlen. Fråga innan du skriver över räkenskapsinformation. |
| "Jag hämtar allt först, det är enklast." | Räkna anropen i steg 2b först. En import som hämtar underlag och betalningsposter för varje faktura är tusen requests, inte tio. |
| "Jag parallelliserar hämtningen så går det fortare." | Det gör det inte — budgeten räknas per token. Dessutom finns en samtidighetsspärr som ger 429, 409 eller 500 utan rate limit-huvuden. Kör sekventiellt. |
| "429 betyder att jag ska vänta på `RetryAfter`." | Bara när huvudet finns. Ett 429 utan huvuden kommer från samtidighetsspärren och ska mötas med exponentiell backoff, inte med en fast väntan. |
| "Bokio är ju facit." | Bokio är en källa. Blir en post fel i bundlen är det bundlens innehavare som svarar för den. |

## Vanliga misstag

- Rå JSON eller `.md`-koncept sparade under `archive/` — arkivet är för
  underlag i mottaget skick, och `.md` där är förbjudet (§5).
- `resource` som pekar på en Bokio-URL i stället för på en nedladdad fil i
  arkivet — då bär bundlen inte sin egen räkenskapsinformation.
- Arkivfiler namngivna med Bokios UUID i stället för fakturanumret.
- Verifikationsnummer importerade rakt av i en bundle som redan har egna —
  kolla `verification_number_range` i `fiscal-years/*.md` först.
- `# Postings` utan kontonamn, för att journal entry bara innehöll numret.
- Preview-endpoints (`suppliers`, `supplier-invoices`, `projects`, `tags`)
  som antas stabila — de kan ändra form utan varning. Läs svaret, lita inte
  bara på tabellen.
- Token utskriven i en kommandorad, en logg eller en fil i repot.
