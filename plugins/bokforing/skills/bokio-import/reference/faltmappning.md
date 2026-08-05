# Fältmappning Bokio Company API → Accounting Knowledge Bundle Specification

Läst mot [docs.bokio.se](https://docs.bokio.se/reference/introduction-to-companyapi)
2026-08-02. Bas-URL `https://api.bokio.se/v1/companies/{companyId}/`.

Legend: **✓** direkt · **≈** härleds/kräver tolkning · **✗** finns inte i
Bokios API — måste hämtas någon annanstans ifrån eller lämnas som lucka.

Endpoints märkta *[Preview]* kan ändras eller försvinna utan varning
(Bokios versioneringspolicy). Kontrollera svaret mot tabellen innan du
litar på ett fält.

## Innehåll

- [§4.1 Organization](#41-organization) · [§4.2 Verification](#42-verification) ·
  [§4.3 Fiscal Year](#43-fiscal-year) · [§4.4 Supplier](#44-supplier) ·
  [§4.5 Supplier Invoice](#45-supplier-invoice) · [§4.6 Customer](#46-customer) ·
  [§4.7 Customer Invoice](#47-customer-invoice) ·
  [§4.10 Chart of Accounts](#410-chart-of-accounts)
- [Koncepttyper utan motsvarighet i Bokios API](#koncepttyper-utan-motsvarighet-i-bokios-api)
- [Bokio-data utan motsvarighet i spec:en](#bokio-data-utan-motsvarighet-i-specen)
- [SIE-filen som komplement](#sie-filen-som-komplement)

---

## §4.1 Organization

`GET /company-information` — scope `company-information:read`. Ett objekt
per bundle, skrivs som `organization.md`.

Kolumnen **allabolag** är [allabolag.se](https://allabolag.se/) —
`GET https://allabolag.se/<orgnr, 10 siffror>`, fälten ur sidans
`__NEXT_DATA__`. Se [Komplettering ur allabolag](#komplettering-ur-allabolag).

| Spec-fält | Bokio | allabolag | |
| --- | --- | --- | --- |
| `title` | `companyInformation.name` | `legalName` | ✓ |
| `organization_number` | `organizationNumber` | `orgnr` | ✓ |
| `vat_number` | — | `registeredForVat` (bool) → `SE`+orgnr+`01` | ≈ |
| `workplace_number` | — | `businessUnitId` (= CFAR-nr), men inte på landningssidan | ✗ |
| `f_tax_status` | — | `registryStatusEntries.registeredForPrepayment` | ✓ |
| `accounting_method` | `fiscalYear.accountingMethod` (`cash`→`kontantmetoden`, `accrual`→`fakturametoden`) | — | ≈ |
| `registered_office` | — | — (`location.municipality` är belägenhet, inte säte) | ✗ |
| `postal_address` | `address.*` | `legalPostalAddress` | ✓ |
| `workplace_address` | — | `legalVisitorAddress` | ✓ |
| `technical_contact` | — | — (`roles` ger styrelse, inte deklarationsombud) | ✗ |
| `technical_contact_email` | `email` | — | ≈ |
| `technical_contact_phone` | `phone` | `legalPhone` | ≈ |
| `# Arbetsställen` | — | `businessUnits[].name`, utan adress och CFAR-nr | ≈ |

**Att veta:**

- **`vat_number` är en härledning, inte en hämtning.** allabolag svarar på
  *om* bolaget är momsregistrerat, inte på vilket nummer det har.
  `SE` + organisationsnumret utan bindestreck + `01` är konventionen och
  stämmer för de allra flesta svenska bolag, men inte för ett bolag i en
  momsgrupp eller med flera registreringar. Skriv det som ett antagande och
  hänvisa till Skatteverkets momsregisterkontroll för att fastställa det.
- **`workplace_number` (CFAR) närmar sig men når inte fram.** allabolag har
  numret — sidan etiketterar `businessUnitId` som "CFAR-nr" — men
  landningssidans JSON ger bara arbetsställenas *namn*; numret och adressen
  ligger i arbetsställevyn. Huvudkontorets `businessUnitId` är dessutom
  `None`. Källan för CFAR är SCB:s företagsregister.
- `registered_office` (bolagets säte enligt bolagsordningen) finns i
  varken Bokio eller allabolag. `location.municipality` är var bolaget
  ligger, vilket ofta men inte alltid sammanfaller med sätet — använd den
  inte som säte. Källan är Bolagsverket.
- `accounting_method` ligger i spec:en bundle-brett men i Bokio per
  räkenskapsår. Skiljer sig metoden mellan åren går den inte att skriva som
  ett enda värde — flagga det i stället för att välja ett av dem.
- `email`/`phone` är bolagets kontaktuppgifter, inte den *tekniska
  kontaktpersonen* §4.1.1 beskriver — den är någon bolaget utser, och står
  i inget register. Skriv dem som kandidater, inte som fastställda.
- Utan spec-fält, men värt brödtext: `companyType` (Bokios
  `limitedCompany` / allabolags `Aktiebolag`), `naceIndustries` (SNI),
  `registrationDate`, `numberOfEmployees`, `status`, `roles`
  (styrelse, revisor, firmatecknare → `# Contact`), och
  `registeredForPayrollTax` — det sista säger om bolaget alls ska lämna
  arbetsgivardeklaration (§4.12).

---

## §4.2 Verification

`GET /journal-entries` — scope `journal-entries:read`. Ett koncept per
journal entry, under `verifications/<räkenskapsår>/`.

| Spec-fält | Bokio | |
| --- | --- | --- |
| `verification_number` | `journalEntryNumber` | ✓ |
| `transaction_date` | `date` | ✓ |
| `recorded_date` | — | ✗ |
| `description` | `title` | ≈ |
| `amount` | summan av `items[].debit` — men se varningen nedan | ≈ |
| `counterparty` | `journalEntryRef` från fakturor **och betalningsposter**, se nedan | ≈ |
| `supporting_documents` | `GET /uploads?query=journalEntryId==<id>` | ✓ |
| `resource` | `GET /uploads/{uploadId}/download` → `archive/` | ✓ |
| `retention_until` | `recorded_date` + 7 år — alltså inte `date` | ✗ |
| `# Postings` | `items[].account`, `.debit`, `.credit` | ✓ |
| kontonamn i `# Postings` | join mot `chart-of-accounts` på `account` | ≈ |
| `tags` (`external`/`internal`/`bokforingsorder`) | — | ✗ |

**De två allvarliga luckorna** — och en tredje som följer av den första:

- **`recorded_date` finns inte.** Bokio har ett enda `date`. BFL 5 kap.
  6–7 §§ kräver både datum då affärshändelsen inträffade och datum då
  verifikationen upprättades, och spec:en gör båda obligatoriska. Sätt inte
  `recorded_date = transaction_date` tyst — då påstår bundlen att allt
  bokfördes samma dag det hände, vilket är fel för i stort sett varje
  verifikation. Fråga användaren vad som ska stå, eller skriv importdatum
  och notera antagandet i `log.md`.
- **`counterparty` finns inte på en journal entry.** Motparten går att nå
  bara indirekt, via `journalEntryRef` från tre håll: `supplierInvoice`,
  `invoice`, och `GET /invoices/{id}/payments`. Det tredje är lätt att
  missa och är det som ger motpart till betalnings­verifikationerna. Bygg
  det omvända indexet journalEntryId → motpart ur alla tre.

  För verifikationer som inget av dem pekar på — bankavgifter, löner,
  bokföringsorder, och betalningar av *leverantörs*fakturor, eftersom de
  saknar betalningsposter i API:et — finns ingen motpart alls. `title`
  innehåller den ofta i klartext; att läsa ut den därifrån är en gissning
  och ska redovisas som en sådan, också när den uppenbart stämmer.
  "Betalning KV-88213" identifierar fakturan, men kopplingen till
  leverantören gör du, inte datat.

- **`amount` som debetsumma går sönder på sammansatta verifikationer.**
  Regeln fungerar för en verifikation som bokför en affärshändelse: ett
  inköp på 1 250 ger debetsumman 1 250. En löneverifikation bokför flera
  saker på en gång — bruttolön, skatteavdrag, arbetsgivaravgifter — och
  debetsumman blir bruttolön *plus* avgifter. För en lön på 45 000 med
  14 139 i avgifter ger regeln 59 139, vilket varken är lönen, det
  utbetalda beloppet eller något annat en läsare känner igen. Spec §4.2.1
  vill ha "uppgift om belopp" för affärshändelsen; 59 139 är inte den
  uppgiften. Räkna om debet- och kreditsidan skiljer sig i antal poster på
  ett sätt som antyder flera händelser, och fråga vilket belopp som avses
  i stället för att låta summan stå — den ser exakt ut och är fel just där
  det är svårast att upptäcka.

- **`retention_until` ärver luckan.** Spec §4.2.1 räknar den som
  `recorded_date` + 7 år, inte transaktionsdatum + 7 år. Eftersom
  `recorded_date` inte har någon källa har inte `retention_until` det
  heller — den kan inte räknas fram ur Bokios `date` utan att arkiveringstiden
  blir fel, oftast för kort. Den avgörs alltså av samma svar som
  `recorded_date`, inte separat.

**Övrigt:** `reversingJournalEntryId` / `reversedByJournalEntryId` (rättade
och rättande verifikationer) har inget spec-fält — skriv relationen som en
länk i brödtexten. Bokios `tags` är dimensioner (projekt, kostnadsställe)
och betyder något helt annat än spec:ens `tags`; blanda inte ihop dem.

---

## §4.3 Fiscal Year

`GET /fiscal-years` — scope `fiscal-years:read`.

| Spec-fält | Bokio | |
| --- | --- | --- |
| `fiscal_year_id` | härleds ur `startDate`/`endDate` (Bokios `id` är en UUID) | ≈ |
| `start_date` / `end_date` | `startDate` / `endDate` | ✓ |
| `status` | `status` (`open` \| `closed`) | ✓ |
| `closing_date` | — | ✗ |
| `closing_method` | — | ✗ |
| `previous_fiscal_year` | sortera åren på `startDate` | ≈ |
| `verification_number_range` | första/sista `journalEntryNumber` i året | ≈ |
| `# Opening Balances` | — i REST-API:et; se [SIE](#sie-filen-som-komplement) | ✗ |
| `# Closing Balances` | — i REST-API:et; se [SIE](#sie-filen-som-komplement) | ✗ |

**Att veta:** balanserna är obligatoriska i spec:en (§4.3.1) — `# Opening
Balances` alltid, `# Closing Balances` så snart året är `closed` — och
finns inte i något JSON-endpoint. Enda vägen ur Bokio är SIE-filen. Utan
den kan ett `Fiscal Year`-koncept inte skrivas spec-enligt; skriv då inte
konceptet halvfärdigt utan säg att SIE-hämtning krävs.

Bokios `accountingMethod` per år hör hemma på `Organization` (§4.1), inte
här — `Fiscal Year` har inget sådant fält.

---

## §4.4 Supplier

`GET /suppliers` *[Preview]* — scope `suppliers:read`.

| Spec-fält | Bokio | |
| --- | --- | --- |
| `title` | `name` | ✓ |
| `company_number` | `orgNumber` | ✓ |
| `vat_number` | `vatNumber` | ✓ |
| `bankgiro` | `paymentDetails.bankgiroNumber` (`type: bankgiro`) | ✓ |
| `plusgiro` | `paymentDetails.plusgiroNumber` (`type: plusgiro`) | ✓ |
| `bank_account` | `clearingNumber`+`accountNumber` (`type: transfer`) eller `iban`+`bic` (`type: internationalPayment`) | ✓ |
| `address` | `address.*` | ✓ |
| `country` | `address.country` | ✓ |
| `f_tax_status` | — i Bokio; **allabolag** `registeredForPrepayment` | ✓ |
| `payment_terms` | — | ✗ |
| `reference_person` | — | ✗ |

**Att veta:** Bokio har *ett* `paymentDetails`-objekt per leverantör medan
spec:ens `bankgiro`/`plusgiro`/`bank_account` är listor — mappa till en
lista med ett element, inte till en sträng.

`f_tax_status` är det fält allabolag gör störst nytta för: saknar en
tjänsteleverantör F-skatt kan Skatteförfarandelagen kräva att *du* gör
skatteavdrag vid betalning (§4.4.1), och Bokio svarar inte på det. Slå upp
leverantören på `orgNumber` — men bara svenska leverantörer, och bara de
som faktiskt fakturerar tjänster; en utländsk leverantör som identifieras
via `vatNumber` finns inte på allabolag alls. Se
[anropsbudgeten](#komplettering-ur-allabolag) innan du slår upp trettio
leverantörer i rad.

Bokios `currency` (leverantörens standardvaluta) har inget spec-fält.

---

## §4.5 Supplier Invoice

`GET /supplier-invoices` *[Preview]* — scope `supplier-invoices:read`.

| Spec-fält | Bokio | |
| --- | --- | --- |
| `supplier` | `supplierRef.id` → `Supplier`-konceptets Concept ID | ✓ |
| `invoice_number` | `invoiceNumber` | ✓ |
| `invoice_date` | `invoiceDate` | ✓ |
| `due_date` | `dueDate` | ✓ |
| `received_date` | — | ✗ |
| `sequence_number` | — | ✗ |
| `amount` | `totalAmount` + `currency` | ✓ |
| `payment_status` | `remainingAmount == 0` → `paid`, annars `unpaid` | ≈ |
| `vat_amount` | Σ `rows[].quantity × unitPrice × taxRate` | ≈ |
| `payment_date` | — | ✗ |
| `currency` / `exchange_rate` | `currency` / `currencyRate` | ✓ |
| `verification` | `journalEntryRef.id` | ✓ |
| `payment_terms` | — | ✗ |
| `resource` | `uploadRefs[].id` → `GET /uploads/{id}/download` | ✓ |
| `# Line Items` | `rows[]` (`description`, `quantity`, `unitPrice`, `unitType`, `taxRate`) | ✓ |

**De tre luckorna som spec:en gör obligatoriska:**

- **`received_date`** — ankomstdatum. Spec §4.5.1 pekar ut det som det
  datum som styr *när fakturan måste bokföras*: "Fakturadatum är således av
  underordnad betydelse." Bokio sparar det inte. Att sätta det till
  `invoiceDate` gör en importerad bundle till en osann utsaga om när
  bokföringsskyldigheten inträdde.
- **`sequence_number`** — löpnumret fakturan får vid ankomst, spec:ens
  andra identifieringskedja vid sidan av `invoice_number`. Finns inte i
  Bokio. Ett internt löpnummer kan tilldelas vid importen, men det är då
  importens nummer och inte reskontrans — säg det.
- **`payment_date`** — det finns inga betalningsposter för
  leverantörsfakturor i API:et (till skillnad från kundfakturor, som har
  `/invoices/{id}/payments`). `remainingAmount` säger *att* fakturan är
  betald, inte *när*. Betalningsdatumet går att hitta i verifikationen som
  bokför betalningen, om den kan identifieras.

`vat_amount` är en summering du gör själv och kan avvika från vad Bokio
faktiskt bokförde vid öresavrundning — stäm av mot verifikationens
momskonton i stället för att lita på summeringen.

---

## §4.6 Customer

`GET /customers` — scope `customers:read`.

| Spec-fält | Bokio | |
| --- | --- | --- |
| `title` | `name` | ✓ |
| `customer_number` | — (Bokios `id` är en UUID, inte ett kundnummer) | ✗ |
| `company_number` | `orgNumber` | ✓ |
| `vat_number` | `vatNumber` | ✓ |
| `address` | `address.*` (inkl. `countrySubdivision`) | ✓ |
| `country` | `address.country` | ✓ |
| `payment_terms` | `paymentTerms` | ✓ |
| `reference_person` | `contactsDetails[]` där `isDefault` | ✓ |

**Att veta:** spec §4.6.1 vill se minst ett av `customer_number`,
`company_number` eller `vat_number`. För en privatkund (`type: private`)
utan `orgNumber` och `vatNumber` blir alla tre tomma — då krävs `address`
för att motparten alls ska vara identifierad. Bokios UUID är inget
kundnummer i BFNAR 2013:2:s mening och ska inte skrivas som ett. Bokios
`type` (`company`/`private`) och `language` har inga spec-fält.

---

## §4.7 Customer Invoice

`GET /invoices` — scope `invoices:read`.

| Spec-fält | Bokio | |
| --- | --- | --- |
| `customer` | `customerRef.id` → `Customer`-konceptets Concept ID | ✓ |
| `invoice_number` | `invoiceNumber` | ✓ |
| `invoice_date` | `invoiceDate` | ✓ |
| `due_date` | `dueDate` | ✓ |
| `amount` | `totalAmount` | ✓ |
| `vat_amount` | `totalTax` | ✓ |
| `payment_status` | `status` → `paid` \| `unpaid` | ≈ |
| `payment_date` | `GET /invoices/{id}/payments` → `date` | ✓ |
| `currency` / `exchange_rate` | `currency` / `currencyRate` | ✓ |
| `verification` | `journalEntryRef.id` | ✓ |
| `payment_terms` | — (finns bara på kunden) | ✗ |
| `resource` | `GET /invoices/{id}/download` (endast publicerade) | ✓ |
| `# Line Items` | `lineItems[]` | ✓ |

**Att veta:** Bokios `status` har åtta värden (`draft`, `published`,
`paid`, `overPaid`, `underPaid`, `overdue`, `credited`, `credit`) mot
spec:ens två. `paid`/`overPaid` → `paid`; `published`/`overdue` →
`unpaid`. `underPaid` (delbetald) och `credited` har ingen spec-motsvarighet
— fråga hur de ska skrivas i stället för att runda av dem till `paid` eller
`unpaid`. Ett `draft` är ingen utställd faktura och ska inte importeras
som ett `Customer Invoice`-koncept alls.

`payment_date` kostar **en request per faktura** — den enskilt dyraste
raden i hela importen. Hoppa över den för fakturor vars `status` är
`published` eller `overdue`; de är obetalda och har ingen betalningspost.
Se anropsbudgeten i SKILL.md steg 2b.

---

## §4.10 Chart of Accounts

`GET /chart-of-accounts` — scope `chart-of-accounts:read`. Ett koncept per
bundle, `chart-of-accounts.md`.

| Spec-fält | Bokio | |
| --- | --- | --- |
| `# Accounts` → kontonummer | `account` | ✓ |
| `# Accounts` → kontonamn | `name` | ✓ |
| `# Accounts` → VAT Declaration Field | — | ✗ |
| `account_standard` | `accountType` (`basePlanAccount`/`customAccount`) antyder BAS men inte vilken årgång | ≈ |

**Att veta:** kopplingen konto → ruta i momsdeklarationen finns inte i
Bokios API. Spec §4.10.1 gör kolumnen obligatorisk för varje konto vars
poster ska summeras in i en ruta, och utan den går ingen `VAT Declaration`
(§4.13) att härleda ur bundlen. Mappningen får hämtas ur BAS-kontoplanens
egen momsrapportkoppling eller Skatteverkets blankettanvisning — den är
inte en importerad uppgift utan något som läggs till efter importen, och
ska redovisas som ett kvarstående arbete och inte gissas konto för konto.

---

## Komplettering ur allabolag

`https://allabolag.se/<orgnr>` — tio siffror utan bindestreck. Sidan
redirectar till en slug-URL; uppgifterna ligger i `__NEXT_DATA__` som JSON.
`scripts/allabolag_fetch.py` gör hämtningen och plockar ut de spec-relevanta
fälten.

**Vad det är.** allabolag drivs av UC Affärsinformation och är deras
återgivning av Bolagsverkets och SCB:s uppgifter — inte registret självt.
Uppgifterna kan släpa. För något som ska skrivas in som ett faktum i sju
års räkenskapsinformation är det en indikation, inte ett fastställande:
Skatteverkets momsregisterkontroll gäller för moms och F-skatt,
Bolagsverket för säte och firma, SCB för CFAR-nummer.

**Var det hjälper.** `Organization` (§4.1), och för svenska motparter även
`Supplier.f_tax_status` (§4.4). `Customer` (§4.6) får ingenting av
betydelse — namn, orgnr och adress finns redan i Bokio, och
`customer_number` är bolagets eget.

**Anropsbudget.** Sidan har botskydd och svarar **202** på täta anrop —
skriptet backar av och ger upp efter tre försök. En uppslagning per
organisationsnummer, spara svaret, och kör aldrig en loop över alla
leverantörer på en gång. Trettio leverantörer är trettio hämtningar av
360 kB HTML från någon annans sajt; slå bara upp dem du faktiskt behöver
`f_tax_status` för.

## Koncepttyper utan motsvarighet i Bokios API

Detta är svaret på "vad går inte att matcha": fem av spec:ens tretton
koncepttyper har inget endpoint alls. Company API täcker bokföring,
fakturering och reskontra — inte löner och inte deklarationer.

| Koncepttyp | Läge |
| --- | --- |
| `Employee` §4.8 | ✗ Bokios löneadministration exponeras inte i Company API. Ingen anställd, inget personnummer, ingen skattetabell. |
| `Payslip` §4.9 | ✗ Inga lönespecifikationer. Löneverifikationerna syns som journal entries, men utan mottagare, bruttolön, skatteavdrag eller nettolön uppdelat. |
| `Expense` §4.11 | ✗ Utlägg finns i Bokio-appen men inte i API:et. Ett utlägg dyker upp som en journal entry (ofta mot 2890) med kvittot som en upload — koncepttypen kräver `employee` och ett `resource` som pekar på kvittot, och kopplingen till *vilken* anställd finns inte. |
| `Employer Tax Declaration` §4.12 | ✗ Ingen arbetsgivardeklaration, varken huvuduppgift eller individuppgifter. |
| `VAT Declaration` §4.13 | ✗ Ingen momsdeklaration. Den *kan* härledas ur journal entries + kontoplan, men bara efter att momsrutemappningen (§4.10) lagts till för hand, och Bokios egen inlämnade deklaration går ändå inte att hämta för avstämning. |

allabolag ändrar inget här: det är ett företagsregister. Det vet vem
bolaget är, inte vad det bokfört, betalat i lön eller deklarerat.

### Fält som återstår efter både Bokio och allabolag

Obligatoriska i spec:en, utan källa i någondera:

| Fält | Var uppgiften finns i stället |
| --- | --- |
| `Verification.recorded_date` §4.2 | Möjligen SIE-filens `#VER` (registreringsdatum), annars ingenstans |
| `Verification.counterparty` §4.2 för poster utan faktura | Ingenstans; bara i verifikationens fritext |
| `Supplier Invoice.received_date` §4.5 | Ankomststämpeln på fakturan; sparas inte digitalt |
| `Supplier Invoice.sequence_number` §4.5 | Reskontrans egen numrering; existerar inte i Bokio |
| `Fiscal Year` `# Opening/Closing Balances` §4.3 | SIE-filens `#IB`/`#UB` |
| Momsruta per konto §4.10 | BAS-kontoplanens momsrapportkoppling / Skatteverkets blankettanvisning |

Rekommenderade, som får lämnas tomma men bör redovisas:

| Fält | Källa |
| --- | --- |
| `Organization.registered_office` §4.1 | Bolagsverket (bolagsordningens säte) |
| `Organization.workplace_number` §4.1 + `# Arbetsställen` | SCB:s företagsregister; allabolags arbetsställevy har CFAR-numret men inte landningssidan |
| `Organization.technical_contact` + e-post/telefon §4.1 | Utses av bolaget; står i inget register — fråga |
| `Fiscal Year.closing_date`, `.closing_method` §4.3 | Årsredovisningen/årsbokslutet |
| `Customer.customer_number` §4.6 | Bolagets eget kundregister |
| `Supplier.payment_terms`, `.reference_person` §4.4 | Avtalet med leverantören |
| `Supplier Invoice.payment_date` §4.5 | Betalningsverifikationen, om den går att identifiera |
| `Supplier Invoice.payment_terms` §4.5, `Customer Invoice.payment_terms` §4.7 | Fakturan respektive kundens standardvillkor |

## Bokio-data utan motsvarighet i spec:en

Åt andra hållet: data som finns i Bokio men inte har någon plats i
profilen. Det är inte en brist i importen — men gå inte förlorat med det
tyst, skriv det i brödtexten eller flagga det.

| Bokio | Kommentar |
| --- | --- |
| **Credit notes** (`/credit-notes`) | Spec:en har ingen `Credit Note`-typ. En kreditfaktura är en egen affärshändelse med en egen verifikation; den kan skrivas som ett `Customer Invoice` med negativa belopp och en länk till den krediterade fakturan, men det är en tolkning — fråga. |
| **Invoice settlements** (`/invoices/{id}/settlements`) | Valutakursdifferens, bankavgift, betalväxelavgift. Bokförs som egna poster i verifikationen; inget fakturafält. |
| **Items** (`/items`) | Produkt- och tjänsteregister. Ingen spec-typ; syns bara som `# Line Items`-rader. |
| **Tags / projects / cost centers** | Bokios dimensioner (dimension 6 = projekt). Spec:en har ingen dimensionsmodell. Krockar med spec:ens `tags`, som betyder verifikationens *art*. |
| **Bank payments** (`/bank-payments`) | Betalningsuppdrag, inte bokföring. Ingen motsvarighet. |
| **Journal entry comments** | Kommentarer på verifikationer. Kan skrivas som brödtext. |
| `companyType`, `customer.language`, `supplier.currency`, `hasBBA` | Har inga fält; brödtext om de är värda att behålla. |

## SIE-filen som komplement

`GET /sie/{fiscalYearId}/download` — scope `sie:read` — ger hela
räkenskapsåret som SIE-fil. Den innehåller det REST-API:et saknar:

- `#IB` / `#UB` — ingående och utgående balans per konto, dvs. §4.3:s
  obligatoriska `# Opening Balances` och `# Closing Balances`.
- `#KONTO` — kontoplanen som den såg ut i det året.
- `#VER` / `#TRANS` — verifikationerna med både verifikationsdatum och
  registreringsdatum, vilket i vissa SIE-varianter ger `recorded_date`.

Spec §5 har redan en plats för filen: `archive/import/<år>-sie4.se`.
Lägg den där och peka på den, oavsett om du också parsar den — då bär
bundlen sitt eget importunderlag i stället för att bara påstå att det
funnits.
