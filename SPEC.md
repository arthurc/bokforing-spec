# Accounting Knowledge Bundle Specification

**Version 0.1 — Draft**

This document specifies how bookkeeping ("bokföring") knowledge is
represented as an [Open Knowledge Format](./okf-spec-v01.md) (OKF)
bundle. It is a **profile** of OKF v0.1 (see [`okf-spec-v01.md`](./okf-spec-v01.md))
for the accounting domain: every rule in OKF v0.1 applies unless this
document explicitly narrows it. Where this document uses a section
number in parentheses, e.g. "(OKF §4.1)", it refers to the
corresponding section of [`okf-spec-v01.md`](./okf-spec-v01.md).

---

## 1. Purpose

OKF v0.1 deliberately requires only a `type` field (OKF §4.1) and
leaves everything else to the producer. That is correct for a
general-purpose format, but accounting is not general-purpose: Swedish
law dictates exactly what information must accompany every recorded
business event. This profile takes the "producer-defined keys" escape
hatch that OKF explicitly allows (OKF §4.1, "Extensions") and uses it
to promote a small set of legally mandated fields from optional to
**required**, for two concept types: `Verification` and `Fiscal Year`.

The legal source for these requirements is the Bokföringslag (BFL).
See [Citations](#6-citations) for the specific statutory references.

---

## 2. Relationship to OKF v0.1

- A bundle conformant with this profile is, by construction, also
  conformant with OKF v0.1 (OKF §9): every concept still has a
  non-empty `type`, and `index.md`/`log.md` still follow OKF §6/§7.
- Consumers that do not know about this profile MUST still be able to
  read the bundle as plain OKF — they will see `type: Verification`
  as an unrecognized-but-tolerated type (OKF §4.1, "Producers SHOULD
  pick values that are descriptive... consumers MUST tolerate unknown
  types gracefully") and the extra fields defined below as ordinary
  producer-defined keys, which OKF §4.1 says consumers "SHOULD
  preserve... and SHOULD NOT reject."
- Consumers that _do_ know this profile MAY additionally enforce the
  stricter per-type requirements in §4 below, and SHOULD reject a
  `Verification` concept missing a required field the same way they
  would reject an OKF concept missing `type` (OKF §9, rule 2).

---

## 3. Terminology

In addition to the terms defined in OKF §2, this profile uses:

- **Verifikation (Verification)** — "de uppgifter som dokumenterar en
  affärshändelse eller en vidtagen justering i bokföringen" (BFL,
  1 kap. 2 §, 7 p.) — the documentation of a single business
  transaction or bookkeeping adjustment. This is the accounting
  domain's Concept (OKF §2): one verifikation = one concept document.
- **Affärshändelse (business transaction)** — any change in a
  company's assets, liabilities, or equity caused by its economic
  relations with the outside world (BFL, 1 kap. 2 §, 6 p.), e.g. a
  payment, a purchase, a sale.
- **Bokföringsorder** — an internally produced verification used when
  no external document (receipt, invoice) exists to serve as one, for
  example when correcting an earlier bookkeeping error or recording a
  depreciation entry at year-end close.
- **Leverantör (Supplier)** — the counterparty a company purchases
  goods or services from; the "motpart" a `Verification`'s
  `counterparty` field (§4.1.1) names in free text when the
  affärshändelse is a purchase.
- **Leverantörsfaktura (Supplier Invoice)** — an invoice received from
  a leverantör for goods or services purchased; the document a
  `Verification`'s `supporting_documents` (§4.1.1) references when the
  affärshändelse is a purchase, and the accounting purpose this
  profile's `Supplier Invoice` concept type (§4.4) serves.
- **Leverantörsreskontra** — a sidoordnad bokföring (subsidiary
  ledger) recording, per leverantör, the invoices received and amounts
  owed (BFL 5 kap. 4 §); the accounting purpose this profile's
  `Supplier` (§4.3) and `Supplier Invoice` (§4.4) concept types jointly
  serve — `Supplier` holds the leverantör's master data, `Supplier
  Invoice` holds each invoice and amount owed.
- **Kund (Customer)** — the counterparty a company sells goods or
  services to; the "motpart" a `Verification`'s `counterparty` field
  (§4.1.1) names in free text when the affärshändelse is a sale.
- **Kundfaktura (Customer Invoice)** — an invoice issued to a kund for
  goods or services sold; the document a `Verification`'s
  `supporting_documents` (§4.1.1) references when the affärshändelse is
  a sale, and the accounting purpose this profile's `Customer Invoice`
  concept type (§4.6) serves.
- **Kundreskontra** — a sidoordnad bokföring (subsidiary ledger)
  recording, per kund, the invoices issued and amounts owed to the
  company (BFL 5 kap. 4 §); the accounting purpose this profile's
  `Customer` (§4.5) and `Customer Invoice` (§4.6) concept types jointly
  serve — `Customer` holds the kund's master data, `Customer Invoice`
  holds each invoice and amount owed.
- **Anställd (Employee)** — a natural person employed by the company in
  return for lön (salary/wages); the "motpart" a `Verification`'s
  `counterparty` field (§4.1.1) names in free text when the
  affärshändelse is a löneutbetalning (salary payment). The accounting
  purpose this profile's `Employee` concept type (§4.7) serves is the
  per-person identifying and tax-withholding data an arbetsgivare must
  hold to run löpande löneadministration and report each month's
  arbetsgivardeklaration på individnivå (AGI).
- **Lönespecifikation (Payslip)** — the specification an arbetsgivare
  issues an anställd for one löneperiod, breaking down how bruttolön
  (gross pay) becomes nettolön (net pay) through its lönearter: grundlön,
  tillägg, skattefria kostnadsersättningar (e.g. utlägg), avdragen skatt,
  and other avdrag. It sits between `Employee` and `Verification` the
  same way `Supplier Invoice` sits between `Supplier` and `Verification`
  (§4.4): the `Employee` is *who* the anställd is, the `Payslip`
  (§4.8) is *what was paid, for which period, and how it breaks down*,
  and the `Verification` (§4.1) is *how the resulting löneutbetalning
  was booked* — the lönespecifikation is the verifikation's underlying
  document (bokföringsunderlag), not the verifikation itself.
- **Kontoplan (Chart of Accounts)** — a bookkeeping system's complete
  list of accounts, each account's number and name, forming part of
  the systemdokumentation BFL 5 kap. 1 § requires (§7 [13]). This
  profile's `Chart of Accounts` concept type (§4.9) represents the
  kontoplan bundle-wide, one file per bundle rather than per
  räkenskapsår or per account — mirroring how `Supplier` (§4.3),
  `Customer` (§4.5), and `Employee` (§4.7) hold bundle-wide master data
  rather than duplicating it per fiscal year, but unlike them, as a
  single file rather than one file per entity.
- **Momsdeklaration** — the periodic mervärdesskattedeklaration a
  VAT-registered company files with Skatteverket, reporting utgående
  and ingående moms and other VAT-relevant amounts per
  redovisningsperiod into a fixed set of numbered fält (rutor) that
  Skatteverket's blankett defines (SFL 26 kap.). This profile's `Chart
  of Accounts` concept type (§4.9) records, per account, which of
  these fält (if any) the account's postings map into, so that a
  momsdeklaration can be derived by summing `Verification` (§4.1)
  postings per account and rolling them up via that mapping.

---

## 4. Concept Types

### 4.1 `Verification`

A `Verification` concept represents exactly one verifikation: the
grundmaterial ("raw material") of all bookkeeping. Every
affärshändelse must have one (chapter 4, "Verifikationer").

Concept ID convention: place verifications under a `verifications/`
subdirectory, one file per verifikation, e.g.
`verifications/2026/000123.md`. Because BFL requires verifications to
be traceable in registration order via their `verification_number`
(§4.1.1 below), producers SHOULD choose filenames that preserve that
order.

#### 4.1.1 Frontmatter

```yaml
---
type: Verification                 # REQUIRED (OKF §4.1)
verification_number: <string>      # REQUIRED
transaction_date: <ISO 8601 date>  # REQUIRED
recorded_date: <ISO 8601 date>     # REQUIRED
description: <string>              # REQUIRED
amount: <decimal> <ISO 4217 code>  # REQUIRED
counterparty: <string>             # REQUIRED
supporting_documents: [<string>, …]# REQUIRED when applicable
title: <Optional display name>     # Recommended (OKF §4.1)
resource: <Optional URI to source document>  # Recommended (OKF §4.1)
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
retention_until: <ISO 8601 date>   # Recommended
---
```

The generic OKF fields (`type`, `title`, `description`, `resource`,
`tags`, `timestamp`) keep their OKF §4.1 meaning, with one change:
`description` is **required** for `Verification`, not merely
recommended, and its content is constrained as specified below.

**Required**, per BFL 5 kap. 6–7 §§:

- `verification_number` — the verifikationsnummer. A sequential
  number reflecting registration order ("löpande verifikationsnummer
  (= registreringsordning)"), so the chain of verifications can be
  followed.
- `transaction_date` — "datum då affärshändelsen inträffat": the date
  the underlying business event actually took place.
- `recorded_date` — "datum då verifikationen har upprättats": the date
  the verification itself was prepared/entered into the books.
- `description` — "uppgift om vad som avses (köpts, sålts eller
  motsvarande)": what the transaction concerns — what was bought,
  sold, or the equivalent. This is stricter than OKF's generic
  "one-sentence summary" (OKF §4.1): for a `Verification`, the
  sentence must state what was bought/sold/paid, not just describe
  the document.
- `amount` — "uppgift om belopp": the monetary amount, including
  currency.
- `counterparty` — "uppgift om motpart": who the other party to the
  transaction was.

**Required when applicable**:

- `supporting_documents` — "upplysningar om avtal eller andra
  handlingar/upplysningar som legat till grund för affärshändelsen,
  samt var de finns tillgängliga" (BFL, 5 kap. 6 och 7 §§): references
  to any agreement or other document the transaction was based on, and
  where it can be found. Required only "i förekommande fall" —
  when such documents exist; a verification with no underlying
  agreement or referenced document (e.g. some bokföringsorder
  corrections) MAY omit it.

**Recommended**:

- `resource` — a URI to the scanned/original source document (kvitto,
  faktura, kontoutdrag, etc.), when one exists. Omit for a
  bokföringsorder that has no external document.
- `retention_until` — BFL requires every verification to be preserved
  for seven years ("ska bevaras i sju år"). This field is not part
  of the verifikation's own content, so it is recommended rather than
  required, but producers SHOULD populate it (typically
  `recorded_date` + 7 years) to make the archiving duty checkable by
  tooling.
- `tags` — MAY be used to record the verification's kind: an
  externally issued document (`external`, e.g. kvitto,
  leverantörsfaktura, kontoutdrag), an internally issued document
  (`internal`, e.g. kundfaktura, lönebesked), or an internally written
  substitute when no natural verification exists (`bokforingsorder`).

#### 4.1.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Verification`
concepts SHOULD use:

| Heading                  | Purpose                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------ |
| `# Postings`             | The kontering: which accounts are debited/credited and by how much.                  |
| `# Supporting Documents` | Expands on `supporting_documents`: where each referenced handling/avtal is archived. |
| `# Citations`            | As OKF §8 — the legal or documentary basis, if not obvious from context.             |

#### 4.1.3 Example

```markdown
---
type: Verification
verification_number: "2026-000123"
transaction_date: 2026-06-30
recorded_date: 2026-07-01
description: Inköp av kontorsmaterial från Kontorsvaruhuset AB
amount: 1250.00 SEK
counterparty: Kontorsvaruhuset AB
supporting_documents: ["Leverantörsfaktura #KV-88213"]
title: Inköp kontorsmaterial — faktura KV-88213
resource: "file:///arkiv/leverantorsfakturor/2026/KV-88213.pdf"
tags: [external, leverantorsfaktura]
timestamp: 2026-07-01T09:15:00Z
retention_until: 2033-07-01
---

Faktura från [Kontorsvaruhuset AB](/parties/kontorsvaruhuset-ab.md)
avseende kontorsmaterial till kontoret, mottagen 2026-06-30.

# Postings

| Account                 | Debit   | Credit  |
| ----------------------- | ------- | ------- |
| 6110 Kontorsmaterial    | 1000.00 |         |
| 2641 Ingående moms      | 250.00  |         |
| 2440 Leverantörsskulder |         | 1250.00 |

# Supporting Documents

- Leverantörsfaktura #KV-88213, arkiverad under
  `/arkiv/leverantorsfakturor/2026/KV-88213.pdf`.

# Citations

[1] Bokföringslagen (BFL) 5 kap. 6–7 §§
```

---

### 4.2 `Fiscal Year`

A `Fiscal Year` concept represents exactly one räkenskapsår: the period
the löpande bokföring is organized into and, at its end, closed off with
an annual closing (chapter 3, "Räkenskapsår"; chapter 6, "Hur den
löpande bokföringen avslutas"). Every `Verification` belongs to exactly
one fiscal year.

Concept ID convention: place fiscal years under a `fiscal-years/`
subdirectory, one file per räkenskapsår, e.g.
`fiscal-years/2025-2026.md`. Producers SHOULD use the same label for
the fiscal year's file and for its corresponding
`verifications/<label>/` subdirectory (§4.1), so the two can be
correlated without opening either.

#### 4.2.1 Frontmatter

```yaml
---
type: Fiscal Year                  # REQUIRED (OKF §4.1)
fiscal_year_id: <string>           # REQUIRED
start_date: <ISO 8601 date>        # REQUIRED
end_date: <ISO 8601 date>          # REQUIRED
status: open | closed              # REQUIRED
closing_date: <ISO 8601 date>      # REQUIRED when status: closed
closing_method: arsredovisning | arsbokslut  # REQUIRED when status: closed
previous_fiscal_year: <Concept ID> # Recommended
verification_number_range: [<string>, <string>]  # Recommended
title: <Optional display name>     # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
---
```

**Required**, per BFL 3 kap. 1–3 §§ and 6 kap. 1 §:

- `fiscal_year_id` — a label identifying the räkenskapsår, e.g.
  `"2025-2026"`. Not itself a legal requirement, but needed so tooling
  and the `previous_fiscal_year` field below can reference a fiscal
  year unambiguously.
- `start_date` / `end_date` — the period the räkenskapsår spans. Per
  BFL 3 kap. 1 §, a räkenskapsår normally comprises twelve calendar
  months; a brutet räkenskapsår (BFL 3 kap. 2 §) still comprises twelve
  months but MAY end on the last day of any calendar month, not just
  December.
- `status` — whether the räkenskapsår's löpande bokföring is still
  being added to (`open`) or has been closed off (`closed`). BFL 6 kap.
  1 § requires every räkenskapsår to eventually be closed with either
  an annual report (årsredovisning) or annual accounts (årsbokslut),
  depending on which BFL 6 kap. requires for the company.

**Required when applicable**:

- `closing_date` — "datum då bokslutet upprättats": the date the annual
  closing was established. Required once `status` is `closed`.
- `closing_method` — which of the two closing forms BFL 6 kap.
  requires was used: `arsredovisning` (årsredovisning, per ÅRL, for
  companies BFL 6 kap. obliges to prepare one) or `arsbokslut`
  (årsbokslut, the lighter-weight form BFL 6 kap. permits smaller
  companies). Required once `status` is `closed`.

**Recommended**:

- `previous_fiscal_year` — the Concept ID of the immediately preceding
  `Fiscal Year` concept, if one exists in the bundle. BFL requires a
  räkenskapsår's opening balances (ingående balans) to equal the prior
  year's closing balances (utgående balans); this link lets tooling
  check that continuity without guessing which concept precedes which.
- `verification_number_range` — the first and last
  `verification_number` (§4.1.1) recorded in this fiscal year, e.g.
  `["V1", "V189"]`. Since BFL 5 kap. 6–7 §§ require verifications to be
  traceable via a löpande verifikationsnummer, this makes it checkable
  that the numbering within the year is complete, without opening every
  verification.

**Balances**, per BFL 6 kap. (bokslutets innehåll):

Account balances are per-account data, not a single scalar, so — like
a `Verification`'s kontering (§4.1.2) — they belong in the body as a
table, not in frontmatter:

- A `Fiscal Year` concept MUST include an `# Opening Balances` body
  section (§4.2.2), listing the ingående balans for every account.
  When `previous_fiscal_year` is set, these balances SHOULD equal that
  year's `# Closing Balances` — BFL requires a räkenskapsår's opening
  balances to tie to the prior year's closing balances, and restating
  them here makes that continuity checkable without opening the linked
  concept. For a first fiscal year with no `previous_fiscal_year`, the
  balances are zero for every account, but the section itself MUST
  still be present.
- A `Fiscal Year` concept MUST include a `# Closing Balances` body
  section (§4.2.2) once `status` is `closed`, listing the utgående
  balans for every account. A bokslut that does not state the closing
  position of every account is not complete.

#### 4.2.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Fiscal Year`
concepts SHOULD use:

| Heading              | Purpose                                                                                  |
| --------------------- | ------------------------------------------------------------------------------------------ |
| `# Verifications`     | A link to the fiscal year's `verifications/<label>/` subdirectory.                       |
| `# Opening Balances`  | The ingående balans per account at the start of the fiscal year. REQUIRED.                |
| `# Closing Balances`  | The utgående balans per account at the end of the fiscal year. REQUIRED once `status` is `closed`. |
| `# Closing`           | Narrative details of the årsbokslut/årsredovisning once `status` is `closed`.            |
| `# Citations`         | As OKF §8 — the legal or documentary basis, if not obvious from context.                 |

#### 4.2.3 Example

```markdown
---
type: Fiscal Year
fiscal_year_id: "2025-2026"
start_date: 2025-09-01
end_date: 2026-08-31
status: open
previous_fiscal_year: "fiscal-years/2024-2025"
verification_number_range: ["V1", "V189"]
title: Räkenskapsår 2025-09-01 – 2026-08-31
timestamp: 2026-03-09T00:00:00Z
---

Räkenskapsår för Company AB, brutet räkenskapsår
2025-09-01 – 2026-08-31. Ännu inte avslutat.

# Verifications

Samtliga verifikationer för räkenskapsåret finns under
[verifications/2025-2026](/verifications/2025-2026/).

# Opening Balances

Ingående balans 2025-09-01, hämtad från [föregående räkenskapsårs
utgående balans](/fiscal-years/2024-2025.md).

| Account                          | Balance         |
| --------------------------------- | ---------------: |
| 1930 Företagskonto / affärskonto  | 45 231.00 SEK    |
| 2091 Balanserad vinst eller förlust | -580 014.09 SEK |

# Citations

[1] Bokföringslagen (BFL) 3 kap. 1–3 §§, 6 kap. 1 §
```

Once this räkenskapsår is closed, the concept MUST additionally include
a `# Closing Balances` section in the same two-column form, listing the
utgående balans — 2026-08-31 in this example — for every account.

---

### 4.3 `Supplier`

A `Supplier` concept represents exactly one leverantör: a recurring
motpart in verifikationer, whose identifying and payment details would
otherwise have to be repeated in every `Verification` that names them
as `counterparty`. BFL requires a bookkeeping system with many
transactions against the same counterparty to maintain a sidoordnad
bokföring — a leverantörsreskontra — through which those transactions
can be identified and reconciled (BFL 5 kap. 4 §). A `Supplier`
concept is this profile's representation of the leverantör's
master-data entry in that leverantörsreskontra; the individual
invoices tracked within it are represented by `Supplier Invoice`
concepts (§4.4).

Concept ID convention: place suppliers under a `suppliers/`
subdirectory, one file per leverantör, e.g.
`suppliers/kontorsvaruhuset-ab.md`. Producers SHOULD use a stable,
recognizable slug so a `Verification`'s free-text `counterparty`
(§4.1.1) can be matched to the corresponding `Supplier` concept
without ambiguity.

#### 4.3.1 Frontmatter

```yaml
---
type: Supplier                     # REQUIRED (OKF §4.1)
company_number: <string>           # REQUIRED when applicable
vat_number: <string>               # REQUIRED when applicable
bankgiro: [<string>, …]            # REQUIRED when applicable
plusgiro: [<string>, …]            # REQUIRED when applicable
bank_account: [<string>, …]        # REQUIRED when applicable
title: <Optional display name>     # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
address: <string>                  # Recommended
country: <ISO 3166-1 alpha-2>      # Recommended
f_tax_status: approved | not_approved  # Recommended
payment_terms: <string>            # Recommended
reference_person: <string>         # Recommended
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `description`, `tags`,
`timestamp`) keep their OKF §4.1 meaning.

**Required when applicable**, per BFL 5 kap. 4 §, 6–7 §§ and
Mervärdesskattelagen (ML)'s invoice-content rules:

- `company_number` — the organisationsnummer of a legal person or the
  personnummer of a sole trader (enskild firma), identifying the
  leverantör as the "motpart" a `Verification`'s `counterparty` field
  (§4.1.1) names in free text. A foreign supplier with no Swedish-style
  registration number MAY omit this field and rely on `vat_number`
  instead.
- `vat_number` — the momsregistreringsnummer, required for a supplier
  registered for VAT, in particular for cross-border/reverse-charge
  purchases where ML requires both parties' VAT numbers to be
  recorded. Omit for a supplier with no VAT registration, e.g. a
  private individual.
- `bankgiro` / `plusgiro` / `bank_account` — the leverantör's
  payment-routing numbers. At least one of these three fields MUST be
  present whenever the supplier is paid electronically, so that
  amounts recorded in the leverantörsreskontra can actually be settled
  and reconciled against bank transactions. Each field is a list
  because a supplier can hold several bankgiro, plusgiro, or bank
  accounts. Omit all three only when there is no ongoing payment
  relationship with the supplier.

**Recommended**:

- `address` — the leverantör's postal address, for correspondence and
  archival.
- `country` — an ISO 3166-1 alpha-2 country code, useful to identify a
  foreign supplier identified via `vat_number` rather than
  `company_number`.
- `f_tax_status` — whether the supplier has been granted F-skatt
  (`approved`) or not (`not_approved`). Relevant for suppliers of
  tjänster (services): if a service supplier is not approved for
  F-skatt, Skatteförfarandelagen may require the payer to withhold
  preliminary tax on payment. Not required because it is inapplicable
  to most suppliers of goods.
- `payment_terms` — the betalningsvillkor agreed with the supplier,
  e.g. `"30 dagar netto"`.
- `reference_person` — a named contact person at the supplier (vår
  referens/er referens).

#### 4.3.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Supplier` concepts
SHOULD use:

| Heading               | Purpose                                                                  |
| ---------------------- | ------------------------------------------------------------------------- |
| `# Verifications`      | Links to verifications where this supplier is the `counterparty`.       |
| `# Supplier Invoices`  | Links to `Supplier Invoice` concepts (§4.4) received from this supplier. |
| `# Citations`          | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.3.3 Example

```markdown
---
type: Supplier
company_number: "556677-8899"
vat_number: "SE556677889901"
bankgiro: ["123-4567"]
title: Kontorsvaruhuset AB
address: Lagergatan 4, 123 45 Storstad
country: SE
f_tax_status: approved
payment_terms: 30 dagar netto
timestamp: 2026-01-15T10:00:00Z
---

[Kontorsvaruhuset AB](https://kontorsvaruhuset.example/), leverantör
av kontorsmaterial.

# Verifications

- [verifications/2026/000123](/verifications/2026/000123.md)

# Supplier Invoices

- [supplier-invoices/2026/KV-88213](/supplier-invoices/2026/KV-88213.md)

# Citations

[1] Bokföringslagen (BFL) 5 kap. 4 §, 6–7 §§
[2] Mervärdesskattelagen (ML) — fakturans innehåll
```

---

### 4.4 `Supplier Invoice`

A `Supplier Invoice` concept represents exactly one leverantörsfaktura:
a specific invoice received from a `Supplier` (§4.3), stating what is
owed, to whom, and by when. It sits between `Supplier` and
`Verification`: the `Supplier` is *who* the counterparty is, the
`Supplier Invoice` is *what was invoiced and when it falls due*, and
the `Verification` (§4.1) is *how the resulting affärshändelse was
booked* — the leverantörsfaktura is the verifikation's underlying
document (bokföringsunderlag), not the verifikation itself.

Concept ID convention: place supplier invoices under a
`supplier-invoices/` subdirectory, one file per leverantörsfaktura,
e.g. `supplier-invoices/2026/KV-88213.md`. Producers SHOULD name the
file after `invoice_number` so the corresponding leverantörsfaktura
can be located without opening it.

#### 4.4.1 Frontmatter

```yaml
---
type: Supplier Invoice              # REQUIRED (OKF §4.1)
supplier: <Concept ID>              # REQUIRED
invoice_number: <string>            # REQUIRED
invoice_date: <ISO 8601 date>       # REQUIRED
due_date: <ISO 8601 date>           # REQUIRED
received_date: <ISO 8601 date>      # REQUIRED
sequence_number: <string>           # REQUIRED
amount: <decimal> <ISO 4217 code>   # REQUIRED
payment_status: unpaid | paid       # REQUIRED
vat_amount: <decimal> <ISO 4217 code>  # REQUIRED when applicable
payment_date: <ISO 8601 date>       # REQUIRED when applicable
currency: <ISO 4217 code>           # REQUIRED when applicable
exchange_rate: <decimal>            # REQUIRED when applicable
verification: <Concept ID>          # Recommended
payment_terms: <string>             # Recommended
title: <Optional display name>      # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
resource: <Optional URI to source document>  # Recommended (OKF §4.1)
tags: [<tag>, …]                    # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>      # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `description`, `resource`,
`tags`, `timestamp`) keep their OKF §4.1 meaning.

**Required**, per BFL 5 kap. 4 § (leverantörsreskontra), ML's
invoice-content rules, and Bokföringsnämndens allmänna råd on
löpande bokföring (BFNAR 2013:2):

- `supplier` — the Concept ID of the `Supplier` (§4.3) who issued the
  invoice, rather than repeating their identifying details in free
  text.
- `invoice_number` — the leverantörens fakturanummer: the supplier's
  own invoice number, one of the identifieringstecken a
  leverantörsreskontra must record.
- `invoice_date` — fakturadatum: the date printed on the invoice.
- `due_date` — förfallodatum: the date payment is due, without which
  the reskontra cannot flag an invoice as overdue.
- `received_date` — the date the invoice arrived at the company and
  was ankomststämplad. This, not `invoice_date`, is what governs when
  the invoice must be recorded: "En leverantörsfaktura är... mottagen
  när den kommer in till företaget. Fakturadatum är således av
  underordnad betydelse."
- `sequence_number` — the löpnummer assigned to the invoice on
  arrival: a second identification chain, alongside `invoice_number`,
  needed because "[f]öretaget använder olika identifieringstecken för
  samma faktura i leverantörsreskontran respektive bokföringen."
- `amount` — the total sum payable, including currency, mirroring
  `Verification.amount` (§4.1.1).
- `payment_status` — whether the invoice is still owed (`unpaid`) or
  has been settled (`paid`). A leverantörsreskontra exists
  specifically to track this per invoice, so an already-paid invoice
  is not paid twice.

**Required when applicable**:

- `vat_amount` — the invoice's mervärdesskatt content, when the
  purchase carries Swedish VAT.
- `payment_date` — the actual date payment was made. Required once
  `payment_status` is `paid`, so that the reskontra records "datum för
  betalning... så att du inte av misstag dubbelbetalar fakturan."
- `currency` / `exchange_rate` — for an invoice issued in a foreign
  currency: the original currency and the exchange rate used at
  booking, since the rate at payment may differ and produce a
  valutakursvinst or -förlust (ÅRL 4 kap. 13 §).

**Recommended**:

- `verification` — the Concept ID of the `Verification` (§4.1) that
  books this invoice.
- `payment_terms` — the betalningsvillkor stated on this invoice, when
  they differ from the `Supplier`'s default `payment_terms` (§4.3.1).

#### 4.4.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Supplier Invoice`
concepts SHOULD use:

| Heading         | Purpose                                                                  |
| ---------------- | ------------------------------------------------------------------------- |
| `# Line Items`  | The fakturarader: goods/services invoiced, quantities, and prices.       |
| `# Payment`     | The invoice's payment/reskontra status, to avoid double payment.        |
| `# Citations`   | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.4.3 Example

```markdown
---
type: Supplier Invoice
supplier: "suppliers/kontorsvaruhuset-ab"
invoice_number: "KV-88213"
invoice_date: 2026-06-28
due_date: 2026-07-28
received_date: 2026-06-30
sequence_number: "L0142"
amount: 1250.00 SEK
vat_amount: 250.00 SEK
payment_status: unpaid
verification: "verifications/2026/000123"
payment_terms: 30 dagar netto
title: Leverantörsfaktura KV-88213 — Kontorsvaruhuset AB
resource: "file:///arkiv/leverantorsfakturor/2026/KV-88213.pdf"
timestamp: 2026-06-30T08:00:00Z
---

Faktura från [Kontorsvaruhuset AB](/suppliers/kontorsvaruhuset-ab.md)
avseende kontorsmaterial till kontoret, mottagen 2026-06-30. Bokförd
som [verifications/2026/000123](/verifications/2026/000123.md).

# Line Items

| Item                      | Qty | Unit Price | Amount  |
| -------------------------- | ---: | ---------: | ------: |
| Kontorsmaterial, diverse   |    1 |    1000.00 | 1000.00 |

# Payment

Ej betald. Förfaller 2026-07-28; betalningsvillkor 30 dagar netto
från fakturadatum.

# Citations

[1] Bokföringslagen (BFL) 5 kap. 4 §
[2] Mervärdesskattelagen (ML) — fakturans innehåll
```

---

### 4.5 `Customer`

A `Customer` concept represents exactly one kund: a recurring motpart
in verifikationer, whose identifying and payment details would
otherwise have to be repeated in every `Verification` that names them
as `counterparty`. BFL requires a bookkeeping system with many
transactions against the same counterparty to maintain a sidoordnad
bokföring — a kundreskontra — through which those transactions can be
identified and reconciled (BFL 5 kap. 4 §). A `Customer` concept is
this profile's representation of the kund's master-data entry in that
kundreskontra; the individual invoices tracked within it are
represented by `Customer Invoice` concepts (§4.6).

Concept ID convention: place customers under a `customers/`
subdirectory, one file per kund, e.g. `customers/foretag-ab.md`.
Producers SHOULD use a stable, recognizable slug so a `Verification`'s
free-text `counterparty` (§4.1.1) can be matched to the corresponding
`Customer` concept without ambiguity.

#### 4.5.1 Frontmatter

```yaml
---
type: Customer                     # REQUIRED (OKF §4.1)
title: <Display name>              # REQUIRED
customer_number: <string>          # REQUIRED when applicable
company_number: <string>           # REQUIRED when applicable
vat_number: <string>               # REQUIRED when applicable
description: <Optional one-line summary>  # Recommended (OKF §4.1)
address: <string>                  # Recommended
country: <ISO 3166-1 alpha-2>      # Recommended
payment_terms: <string>            # Recommended
reference_person: <string>         # Recommended
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `description`, `tags`, `timestamp`)
keep their OKF §4.1 meaning, with one change: `title` is **required**
for `Customer`, not merely recommended — promoted from OKF's generic
"Recommended" (OKF §4.1) because a kundreskontra entry without a name
does not identify the kund it belongs to.

**Required when applicable**, per BFL 5 kap. 4 §, 6–7 §§ and BFNAR
2013:2's commentary on identifying a motpart:

- `customer_number` — the kundnummer assigned to the kund, e.g. in
  partihandel. BFNAR 2013:2's commentary on BFL 5 kap. 6 § notes that
  "[u]ppgiften om motpart kan vara ett kundnummer, om det finns
  fullständiga uppgifter om kunden i kundregistret" — a kundnummer is
  an accepted way to identify the motpart named in a `Verification`
  (§4.1.1), provided the full customer details are recorded here.
- `company_number` — the organisationsnummer of a legal person, or the
  personnummer of a sole trader or private individual, identifying the
  kund as the "motpart" a `Verification`'s `counterparty` field
  (§4.1.1) names in free text. A foreign or anonymous-at-point-of-sale
  customer MAY omit this field and rely on `vat_number` or
  `customer_number` instead.
- `vat_number` — the momsregistreringsnummer, required for a customer
  registered for VAT, in particular for cross-border/reverse-charge
  sales where ML requires both parties' VAT numbers to be recorded.
  Omit for a customer with no VAT registration, e.g. a private
  individual.

At least one of `customer_number`, `company_number`, or `vat_number`
SHOULD be present: BFNAR 2013:2's commentary on BFL 5 kap. 6 § accepts
"namn och adress," "namn och organisationsnummer," "registreringsnummer
för mervärdesskatt," or a kundnummer as sufficient to identify a
motpart — a `Customer` concept with none of these and no `address`
does not meet that bar.

**Recommended**:

- `address` — the kund's postal address, for correspondence and
  archival.
- `country` — an ISO 3166-1 alpha-2 country code, useful to identify a
  foreign customer identified via `vat_number` rather than
  `company_number`.
- `payment_terms` — the betalningsvillkor agreed with the customer,
  e.g. `"30 dagar netto"`.
- `reference_person` — a named contact person at the customer (vår
  referens/er referens).

#### 4.5.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Customer` concepts
SHOULD use:

| Heading               | Purpose                                                                  |
| ---------------------- | ------------------------------------------------------------------------- |
| `# Verifications`      | Links to verifications where this customer is the `counterparty`.       |
| `# Customer Invoices`  | Links to `Customer Invoice` concepts (§4.6) issued to this customer.    |
| `# Citations`          | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.5.3 Example

```markdown
---
type: Customer
customer_number: "K-4471"
company_number: "556122-3344"
vat_number: "SE556122334401"
title: Företag AB
address: Kundgatan 9, 111 22 Storstad
country: SE
payment_terms: 30 dagar netto
timestamp: 2026-02-01T10:00:00Z
---

[Företag AB](https://foretag.example/), återkommande kund som köper
konsulttjänster.

# Verifications

- [verifications/2026/000145](/verifications/2026/000145.md)

# Customer Invoices

- [customer-invoices/2026/2026-0456](/customer-invoices/2026/2026-0456.md)

# Citations

[1] Bokföringslagen (BFL) 5 kap. 4 §, 6–7 §§
[2] Mervärdesskattelagen (ML) — fakturans innehåll
[3] BFNAR 2013:2 — kommentar till 5 kap. 6 § BFL om identifiering av
    motpart
```

---

### 4.6 `Customer Invoice`

A `Customer Invoice` concept represents exactly one kundfaktura: a
specific invoice issued to a `Customer` (§4.5), stating what is owed,
by whom, and by when. It sits between `Customer` and `Verification`:
the `Customer` is *who* the counterparty is, the `Customer Invoice` is
*what was invoiced and when it falls due*, and the `Verification`
(§4.1) is *how the resulting affärshändelse was booked* — the
kundfaktura is the verifikation's underlying document
(bokföringsunderlag), not the verifikation itself.

Unlike `Supplier Invoice` (§4.4), a `Customer Invoice` has only one
identification chain: the issuing company assigns `invoice_number`
itself, from a sequential series, at the moment of issue. A `Supplier
Invoice` needs a separate `sequence_number` and `received_date`
because an *incoming* invoice arrives already numbered by the
supplier, under a scheme the receiving company does not control
("Företaget använder olika identifieringstecken för samma faktura i
leverantörsreskontran respektive bokföringen" — BFNAR 2013:2), and its
receipt, not its printed date, governs when it must be booked. An
outgoing kundfaktura has no such second chain and no "received" event:
the issuing company's own `invoice_number` identifies it in both the
kundreskontra and the bokföring from the start, and there is
consequently no `Customer Invoice` equivalent of `sequence_number` or
`received_date`.

Concept ID convention: place customer invoices under a
`customer-invoices/` subdirectory, one file per kundfaktura, e.g.
`customer-invoices/2026/2026-0456.md`. Producers SHOULD name the file
after `invoice_number` so the corresponding kundfaktura can be located
without opening it.

#### 4.6.1 Frontmatter

```yaml
---
type: Customer Invoice              # REQUIRED (OKF §4.1)
customer: <Concept ID>              # REQUIRED
invoice_number: <string>            # REQUIRED
invoice_date: <ISO 8601 date>       # REQUIRED
due_date: <ISO 8601 date>           # REQUIRED
amount: <decimal> <ISO 4217 code>   # REQUIRED
payment_status: unpaid | paid       # REQUIRED
vat_amount: <decimal> <ISO 4217 code>  # REQUIRED when applicable
payment_date: <ISO 8601 date>       # REQUIRED when applicable
currency: <ISO 4217 code>           # REQUIRED when applicable
exchange_rate: <decimal>            # REQUIRED when applicable
verification: <Concept ID>          # Recommended
payment_terms: <string>             # Recommended
title: <Optional display name>      # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
resource: <Optional URI to source document>  # Recommended (OKF §4.1)
tags: [<tag>, …]                    # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>      # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `description`, `resource`,
`tags`, `timestamp`) keep their OKF §4.1 meaning.

**Required**, per BFL 5 kap. 4 § (kundreskontra) and ML's
invoice-content rules:

- `customer` — the Concept ID of the `Customer` (§4.5) the invoice was
  issued to, rather than repeating their identifying details in free
  text.
- `invoice_number` — the fakturanummer the issuing company assigns,
  drawn from a sequential series (ML requires a faktura's löpnummer to
  make it uniquely identifiable within one or more series). Unlike
  `Supplier Invoice.invoice_number` (§4.4.1), this is the company's own
  number, not a counterparty's.
- `invoice_date` — fakturadatum: the date printed on the invoice, and —
  since the company controls issuance — the date that governs when the
  invoice must be booked (contrast `Supplier Invoice`, where
  `received_date` governs instead).
- `due_date` — förfallodatum: the date payment is due, without which
  the reskontra cannot flag an invoice as overdue.
- `amount` — the total sum owed, including currency, mirroring
  `Verification.amount` (§4.1.1).
- `payment_status` — whether the invoice is still owed (`unpaid`) or
  has been settled (`paid`). A kundreskontra exists specifically to
  track this per invoice, so that an already-paid invoice is not
  chased for payment again.

**Required when applicable**:

- `vat_amount` — the invoice's mervärdesskatt content, when the sale
  carries Swedish VAT.
- `payment_date` — the actual date payment was received. Required once
  `payment_status` is `paid`, mirroring `Supplier Invoice.payment_date`
  (§4.4.1).
- `currency` / `exchange_rate` — for an invoice issued in a foreign
  currency: the original currency and the exchange rate used at
  booking, since the rate at payment may differ and produce a
  valutakursvinst or -förlust (ÅRL 4 kap. 13 §).

**Recommended**:

- `verification` — the Concept ID of the `Verification` (§4.1) that
  books this invoice.
- `payment_terms` — the betalningsvillkor stated on this invoice, when
  they differ from the `Customer`'s default `payment_terms` (§4.5.1).

#### 4.6.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Customer Invoice`
concepts SHOULD use:

| Heading         | Purpose                                                                  |
| ---------------- | ------------------------------------------------------------------------- |
| `# Line Items`  | The fakturarader: goods/services invoiced, quantities, and prices.       |
| `# Payment`     | The invoice's payment/reskontra status, to track outstanding amounts.   |
| `# Citations`   | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.6.3 Example

```markdown
---
type: Customer Invoice
customer: "customers/foretag-ab"
invoice_number: "2026-0456"
invoice_date: 2026-06-15
due_date: 2026-07-15
amount: 25000.00 SEK
vat_amount: 5000.00 SEK
payment_status: unpaid
verification: "verifications/2026/000145"
payment_terms: 30 dagar netto
title: Kundfaktura 2026-0456 — Företag AB
timestamp: 2026-06-15T09:00:00Z
---

Faktura till [Företag AB](/customers/foretag-ab.md) avseende
konsulttjänster utförda i maj 2026. Bokförd som
[verifications/2026/000145](/verifications/2026/000145.md).

# Line Items

| Item                       | Qty | Unit Price | Amount   |
| --------------------------- | ---: | ---------: | -------: |
| Konsulttjänster, maj 2026   |    1 |   20000.00 | 20000.00 |

# Payment

Ej betald. Förfaller 2026-07-15; betalningsvillkor 30 dagar netto från
fakturadatum.

# Citations

[1] Bokföringslagen (BFL) 5 kap. 4 §
[2] Mervärdesskattelagen (ML) — fakturans innehåll
```

---

### 4.7 `Employee`

An `Employee` concept represents exactly one anställd: a person the
company pays lön to, and for whom the company must hold enough
identifying and tax data to run löpande löneadministration and to
report each month's arbetsgivardeklaration på individnivå (AGI) —
the per-person breakdown of paid ersättning and gjorda skatteavdrag
that Skatteförfarandelagen (SFL) has required since 2019 (26 kap.).
An `Employee` concept is this profile's representation of that
per-person master data; the individual löneutbetalningar are recorded,
like any other affärshändelse, as `Verification` concepts (§4.1) that
name the employee as `counterparty`.

Concept ID convention: place employees under an `employees/`
subdirectory, one file per anställd, e.g.
`employees/anna-svensson.md`. Producers SHOULD use a stable,
recognizable slug so a `Verification`'s free-text `counterparty`
(§4.1.1) can be matched to the corresponding `Employee` concept
without ambiguity.

#### 4.7.1 Frontmatter

```yaml
---
type: Employee                     # REQUIRED (OKF §4.1)
title: <Full name>                 # REQUIRED
personal_number: <string>          # REQUIRED when applicable
address: <string>                  # REQUIRED when applicable
tax_table: <integer>               # REQUIRED when applicable
tax_column: <integer>              # REQUIRED when tax_table is set
tax_adjustment: <string>           # REQUIRED when applicable
bank_account: [<string>, …]        # REQUIRED when applicable
end_date: <ISO 8601 date>          # REQUIRED when applicable
employment_number: <string>        # Recommended
start_date: <ISO 8601 date>        # Recommended
employment_type: monthly | hourly | board_fee  # Recommended
position: <string>                 # Recommended
description: <Optional one-line summary>  # Recommended (OKF §4.1)
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `description`, `tags`, `timestamp`)
keep their OKF §4.1 meaning, with one change: `title` is **required**
for `Employee`, not merely recommended — promoted from OKF's generic
"Recommended" (OKF §4.1) for the same reason as `Customer.title`
(§4.5.1): a löneutbetalning's `counterparty` names the anställd by
name, and that name has to resolve to a concept.

**Required when applicable**, per SFL 26 kap. (individuppgift i
arbetsgivardeklaration på individnivå) and 10–11 kap. (skatteavdrag
enligt skattetabell och jämkning):

- `personal_number` — the personnummer (or, for a foreign anställd not
  in folkbokföringen, a samordningsnummer) identifying the anställd as
  the "motpart" a `Verification`'s `counterparty` field (§4.1.1) names
  in free text, and the identifier the AGI reports per person each
  month. Omit only for the rare anställd Skatteverket has not yet
  assigned either number to.
- `tax_table` — the preliminärskattetabell Skatteverket has assigned
  the anställd, used to compute the skatteavdrag on each
  löneutbetalning. Omit for an anställd taxed under Lag (1991:586) om
  särskild inkomstskatt för utomlands bosatta (SINK), who pays a flat
  rate instead of a table-based deduction.
- `tax_column` — the skattekolumn within `tax_table` (Skatteverket's
  tables run several columns side by side, e.g. for differing antal
  dagar per vecka or biinkomst treatment); `tax_table` alone does not
  fix a single skatteavdrag belopp without it. Required whenever
  `tax_table` is present; omit together with `tax_table` under the
  same SINK exception.
- `tax_adjustment` — the jämkningsbeslut Skatteverket has issued for
  the anställd, when one exists, since it overrides the deduction
  `tax_table` would otherwise produce.
- `address` — the anställdas home address. Omit only when the company
  does not hold it on file, e.g. an anställd supplied and paid through
  a personnel-leasing arrangement whose employer of record maintains
  the address.
- `bank_account` — the account lönen is paid into. Required whenever
  the anställd is paid electronically, mirroring `Supplier.bank_account`
  (§4.3.1).
- `end_date` — the anställd's last day of employment. Required once
  the anställning has ended.

**Recommended**:

- `employment_number` — the anställningsnummer, if the company assigns
  one.
- `start_date` — the anställningsdatum.
- `employment_type` — whether the anställd is paid `monthly`
  (månadslön), `hourly` (timlön), or a `board_fee` (styrelsearvode).
- `position` — the anställdas befattning.

#### 4.7.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Employee` concepts
SHOULD use:

| Heading          | Purpose                                                                   |
| ----------------- | -------------------------------------------------------------------------- |
| `# Verifications` | Links to verifications where this employee is the `counterparty`.        |
| `# Citations`     | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.7.3 Example

```markdown
---
type: Employee
title: Anna Svensson
personal_number: "19850612-1234"
address: Vallgatan 12, 411 16 Göteborg
tax_table: 33
tax_column: 1
bank_account: ["SE45 5000 0000 0583 9825 7466"]
employment_number: "E-014"
start_date: 2022-03-01
employment_type: monthly
position: Redovisningsekonom
timestamp: 2022-03-01T08:00:00Z
---

Anna Svensson, anställd som redovisningsekonom sedan 2022-03-01.

# Verifications

- [verifications/2026/000201](/verifications/2026/000201.md)

# Citations

[1] Skatteförfarandelagen (SFL) 26 kap., 10–11 kap.
```

---

### 4.8 `Payslip`

A `Payslip` concept represents exactly one lönespecifikation: the
breakdown an arbetsgivare gives an `Employee` (§4.7) for one löneperiod,
stating what was paid and how the bruttolön (gross pay) became the
nettolön (net pay) actually transferred. It sits between `Employee` and
`Verification`, mirroring how `Supplier Invoice` (§4.4) sits between
`Supplier` and `Verification`: the `Employee` is *who* the anställd is,
the `Payslip` is *what was paid, for which period, and how it breaks
down*, and the `Verification` (§4.1) is *how the resulting
löneutbetalning was booked* — the lönespecifikation is the
verifikation's underlying document (bokföringsunderlag), not the
verifikation itself.

Concept ID convention: place payslips under a `payslips/` subdirectory,
one file per lönespecifikation, e.g.
`payslips/2026/anna-svensson-2026-06.md`. Unlike a leverantörsfaktura
or kundfaktura, a lönespecifikation carries no invoice-style löpnummer
of its own, so producers SHOULD name the file after the anställd's slug
and the löneperiod instead.

#### 4.8.1 Frontmatter

```yaml
---
type: Payslip                      # REQUIRED (OKF §4.1)
employee: <Concept ID>             # REQUIRED
start_date: <ISO 8601 date>        # REQUIRED
end_date: <ISO 8601 date>          # REQUIRED
payment_date: <ISO 8601 date>      # REQUIRED
gross_pay: <decimal> <ISO 4217 code>   # REQUIRED
tax_withheld: <decimal> <ISO 4217 code>  # REQUIRED
net_pay: <decimal> <ISO 4217 code>     # REQUIRED
other_deductions: <decimal> <ISO 4217 code>  # REQUIRED when applicable
employer_contributions: <decimal> <ISO 4217 code>  # Recommended
verification: <Concept ID>         # Recommended
title: <Optional display name>     # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
resource: <Optional URI to source document>  # Recommended (OKF §4.1)
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `description`, `resource`,
`tags`, `timestamp`) keep their OKF §4.1 meaning.

**Required**, per BFL 5 kap. 6–7 §§ (bokföringsunderlag for the
löneutbetalning) and SFL 26 kap. (individuppgift i
arbetsgivardeklaration på individnivå, AGI):

- `employee` — the Concept ID of the `Employee` (§4.7) the
  lönespecifikation was issued to, rather than repeating their
  identifying details in free text.
- `start_date` / `end_date` — the löneperiod the specifikationen
  covers, mirroring `Fiscal Year.start_date`/`end_date` (§4.2.1). A
  löneperiod MAY be shorter than a full month — for example, an
  anställd who börjar or slutar sin anställning mid-period — so both
  dates are required rather than a single period label.
- `payment_date` — utbetalningsdagen: the date lönen was actually
  transferred, mirroring `Supplier Invoice.payment_date`/`Customer
  Invoice.payment_date` (§4.4.1/§4.6.1) and the date the `Verification`
  (§4.1) booking the löneutbetalning should carry as its
  `transaction_date`.
- `gross_pay` — bruttolönen: the sum of all lönearter before avdrag,
  and one of the two per-anställd figures SFL 26 kap. requires
  reporting each month in the AGI individuppgift.
- `tax_withheld` — the avdragna preliminärskatten: the second of the
  two per-anställd figures SFL 26 kap. requires in the AGI
  individuppgift.
- `net_pay` — nettolönen actually paid out, mirroring
  `Verification.amount` (§4.1.1) so the lönespecifikation can be
  reconciled against the löneutbetalning it documents.

**Required when applicable**:

- `other_deductions` — the sum of any avdrag beyond `tax_withheld`,
  e.g. fackföreningsavgift, reglering av löneförskott, or utmätning.
  Required whenever such a deduction was made; omit for a payslip with
  no deductions besides preliminary tax.

**Recommended**:

- `employer_contributions` — the arbetsgivaravgifter (and, where
  relevant, särskild löneskatt) computed on this payslip's ersättning.
  A lönespecifikation given to the anställd does not always itemize
  this — it is an employer cost, not a deduction from the anställd's
  lön — but producers MAY record it here rather than only in the
  `Verification`'s kontering (§4.1.2).
- `verification` — the Concept ID of the `Verification` (§4.1) that
  books the löneutbetalning.
- `resource` — a URI to the original lönebesked document, when one
  exists.

#### 4.8.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Payslip` concepts
SHOULD use:

| Heading         | Purpose                                                                                    |
| ---------------- | -------------------------------------------------------------------------------------------- |
| `# Line Items`  | The lönearter: salary components, benefits, cost reimbursements (e.g. utlägg), and deductions that sum from `gross_pay` to `net_pay`. |
| `# Citations`   | As OKF §8 — the legal or documentary basis, if not obvious from context.                   |

#### 4.8.3 Example

```markdown
---
type: Payslip
employee: "employees/anna-svensson"
start_date: 2026-06-01
end_date: 2026-06-30
payment_date: 2026-06-25
gross_pay: 32000.00 SEK
tax_withheld: 8100.00 SEK
net_pay: 24050.00 SEK
other_deductions: 300.00 SEK
employer_contributions: 10240.00 SEK
verification: "verifications/2026/000201"
title: Lönespecifikation Anna Svensson — juni 2026
timestamp: 2026-06-25T08:00:00Z
---

Lönespecifikation för [Anna Svensson](/employees/anna-svensson.md)
avseende juni 2026. Bokförd som
[verifications/2026/000201](/verifications/2026/000201.md).

# Line Items

| Löneart                 | Typ    |   Belopp |
| ------------------------ | ------ | -------: |
| Månadslön                | Lön    | 32000.00 |
| Utlägg, kontorsmaterial  | Utlägg |   450.00 |
| Avdragen skatt           | Avdrag | -8100.00 |
| Fackföreningsavgift      | Avdrag |  -300.00 |

# Citations

[1] Bokföringslagen (BFL) 5 kap. 6–7 §§
[2] Skatteförfarandelagen (SFL) 26 kap.
```

---

### 4.9 `Chart of Accounts`

A `Chart of Accounts` concept represents the kontoplan: the company's
complete list of bookkeeping accounts, their names, and — where
relevant — which field of the periodic mervärdesskattedeklaration each
account's postings map into. BFL requires every bookkeeping system to
be accompanied by a systemdokumentation describing the system's
organisation and structure, "så att sambanden mellan
systemdokumentationen och den löpande bokföringen enkelt kan utläsas"
(BFL 5 kap. 1 §) — a kontoplan is a core part of that documentation,
since without it the accounts referenced by every `Verification`'s
kontering (§4.1.2) and every `Fiscal Year`'s balances (§4.2.1) cannot
be understood on their own. Separately, a VAT-registered company must
file a periodic mervärdesskattedeklaration reporting utgående and
ingående moms, among other amounts, per redovisningsperiod (SFL 26
kap.); Skatteverket's blankett for that declaration divides these
amounts into a fixed set of numbered fält (rutor). A `Chart of
Accounts` concept lets tooling derive that declaration automatically,
by summing `Verification` postings per account and rolling the sums up
through this account-to-fält mapping.

Unlike `Supplier` (§4.3), `Customer` (§4.5), and `Employee` (§4.7) —
which are also bundle-wide master data, but one file per entity — a
`Chart of Accounts` concept is a single file for the whole bundle,
since the systemdokumentation BFL 5 kap. 1 § requires describes the
bookkeeping system as a whole, not one leverantör, kund, or anställd at
a time. It is also, like `Supplier`/`Customer`/`Employee`, scoped to
the company as a whole rather than to any one `Fiscal Year` (§4.2): a
kontoplan may occasionally be revised, but it is not duplicated per
räkenskapsår, and producers SHOULD update the single file in place —
bumping `timestamp` — when accounts are added, renamed, or remapped.

Concept ID convention: place the chart of accounts at the bundle root
as `chart-of-accounts.md`. There is exactly one `Chart of Accounts`
concept per bundle — not one file per account and not one per fiscal
year — so, unlike §4.1–§4.8, no subdirectory or per-entity filename
convention is needed.

#### 4.9.1 Frontmatter

```yaml
---
type: Chart of Accounts            # REQUIRED (OKF §4.1)
account_standard: <string>         # Recommended
title: <Optional display name>     # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `description`, `tags`,
`timestamp`) keep their OKF §4.1 meaning.

**Recommended**:

- `account_standard` — which version of the Baskontoplan (BAS) or other
  kontoplan standard this chart of accounts follows, e.g. `"BAS 2026"`.
  Not itself a legal requirement — BFL 5 kap. 1 § requires a
  systemdokumentation, not adherence to any particular published
  kontoplan — but recording it lets tooling and readers understand
  where an account's number and name originate, and flag drift once
  the underlying BAS standard is later revised.

**Accounts**, per BFL 5 kap. 1 §:

An account's number, name, and (where applicable) VAT declaration
field are per-account data, not a single scalar, so — like a `Fiscal
Year`'s balances (§4.2.1) — they belong in the body as a table, not in
frontmatter:

- A `Chart of Accounts` concept MUST include an `# Accounts` body
  section (§4.9.2), listing every account number and account name the
  bookkeeping system uses. A systemdokumentation that omits accounts
  actually posted to in `Verification` concepts (§4.1.2) does not let
  "sambanden mellan systemdokumentationen och den löpande bokföringen"
  be readily understood, as BFL 5 kap. 1 § requires.
- The VAT Declaration Field column is **required when applicable**:
  populate it for every account whose transactions are to be summed
  into a specific field (ruta) of the periodic
  mervärdesskattedeklaration — for example an utgående-moms account, an
  ingående-moms account, or an EU purchase/sale account. Leave it empty
  for accounts with no such mapping, e.g. a bank account or an
  inventory account, whose postings never enter the moms return.

#### 4.9.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Chart of Accounts`
concepts SHOULD use:

| Heading      | Purpose                                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------------------------ |
| `# Accounts` | The kontoplan: every account number and name, and, where applicable, the momsdeklaration field it maps to. REQUIRED. |
| `# Citations` | As OKF §8 — the legal or documentary basis, if not obvious from context.                                        |

#### 4.9.3 Example

```markdown
---
type: Chart of Accounts
account_standard: "BAS 2026"
title: Kontoplan — Company AB
description: Kontoplan för Company AB, med varje kontos mappning mot
  fält i den periodiska mervärdesskattedeklarationen, där sådan
  mappning finns.
timestamp: 2026-07-01T09:00:00Z
---

Kontoplan för Company AB, baserad på BAS 2026. Konton utan
mervärdesskatterelevans, t.ex. bankkonton, saknar en VAT Declaration
Field-post.

# Accounts

| Account | Account Name                                     | VAT Declaration Field |
| ------- | ------------------------------------------------- | ---------------------- |
| 1930    | Företagskonto / affärskonto                        |                         |
| 2611    | Utgående moms på försäljning inom Sverige, 25 %    | 10                      |
| 2640    | Ingående moms                                      | 48                      |
| 4535    | Inköp av tjänster från annat EU-land, 25 %         | C21                     |

# Citations

[1] Bokföringslagen (BFL) 5 kap. 1 §
[2] Mervärdesskattelagen (ML); Skatteförfarandelagen (SFL) 26 kap. —
    Skatteverkets blankett för mervärdesskattedeklaration
```

---

## 6. Conformance

A bundle is conformant with this profile if it satisfies OKF v0.1
conformance (OKF §9) **and**, additionally:

- every concept with `type: Verification` has all fields listed as
  "Required" in §4.1.1, plus `supporting_documents` whenever the
  underlying affärshändelse in fact had a referenced agreement or
  document;
- every concept with `type: Fiscal Year` has all fields listed as
  "Required" in §4.2.1, plus `closing_date` and `closing_method`
  whenever `status` is `closed`; includes an `# Opening Balances` body
  section (§4.2.2); and includes a `# Closing Balances` body section
  (§4.2.2) whenever `status` is `closed`.
- every concept with `type: Supplier` has `company_number` and
  `vat_number` whenever the underlying leverantör in fact has such a
  number, and at least one of `bankgiro`, `plusgiro`, or
  `bank_account` whenever the supplier is paid electronically (§4.3.1).
- every concept with `type: Supplier Invoice` has all fields listed as
  "Required" in §4.4.1, plus `vat_amount` whenever the purchase carries
  Swedish VAT, `payment_date` whenever `payment_status` is `paid`, and
  `currency`/`exchange_rate` whenever the invoice is issued in a
  foreign currency (§4.4.1).
- every concept with `type: Customer` has `title`, plus
  `customer_number`, `company_number`, and `vat_number` whenever the
  underlying kund in fact has such an identifier (§4.5.1).
- every concept with `type: Customer Invoice` has all fields listed as
  "Required" in §4.6.1, plus `vat_amount` whenever the sale carries
  Swedish VAT, `payment_date` whenever `payment_status` is `paid`, and
  `currency`/`exchange_rate` whenever the invoice is issued in a
  foreign currency (§4.6.1).
- every concept with `type: Employee` has `title`, plus
  `personal_number`, `address`, `tax_table`, `tax_adjustment`, and
  `bank_account` whenever the underlying anställd in fact has such
  data on file; `tax_column` whenever `tax_table` is present; and
  `end_date` whenever the anställning has ended (§4.7.1).
- every concept with `type: Payslip` has all fields listed as
  "Required" in §4.8.1, plus `other_deductions` whenever a deduction
  beyond `tax_withheld` was made (§4.8.1).
- every concept with `type: Chart of Accounts` includes an `# Accounts`
  body section (§4.9.2) listing every account number and account name
  the bookkeeping system uses, with the VAT Declaration Field populated
  for every account whose transactions map to a field of the periodic
  mervärdesskattedeklaration (§4.9.1).

As with OKF itself (OKF §9), consumers MUST NOT reject a
`Verification`, `Fiscal Year`, `Supplier`, `Supplier Invoice`,
`Customer`, `Customer Invoice`, `Employee`, `Payslip`, or `Chart of
Accounts` concept over missing "Recommended" fields — only over
missing "Required" (or applicable "Required when applicable") fields.

---

## 7. Citations

The requirements in §4.1, §4.3, §4.4, §4.5, and §4.6 are drawn directly
from the Bokföringslag (BFL, SFS 1999:1078); for `Supplier`'s and
`Customer`'s VAT numbers and `Supplier Invoice`'s/`Customer Invoice`'s
invoice-content fields, the Mervärdesskattelag (ML, SFS 2023:200); for
`Supplier Invoice`'s and `Customer Invoice`'s foreign-currency fields,
the Årsredovisningslag (ÅRL, SFS 1995:1554); for `Supplier
Invoice`'s `received_date`/`sequence_number` and `Customer`'s
`customer_number`, Bokföringsnämndens allmänna råd om bokföring (BFNAR
2013:2); for `Employee`'s identifying and tax-withholding fields
(§4.7), the Skatteförfarandelag (SFL, SFS 2011:1244) and, for the
`tax_table` exception, Lag (1991:586) om särskild inkomstskatt för
utomlands bosatta (SINK); for `Payslip`'s ersättnings- and
skatteavdrag fields (§4.8), the same Bokföringslag provisions as §4.1
and the same Skatteförfarandelag provisions as §4.7; and for `Chart of
Accounts` (§4.9), the Bokföringslag's systemdokumentation requirement
for the concept type's existence, and the Mervärdesskattelag together
with the Skatteförfarandelag's periodic skattedeklaration provisions
for the VAT-declaration-field mapping itself:

[1] BFL 1 kap. 2 §, 6–7 p. — definitions of *affärshändelse* and
    *verifikation*.
[2] BFL 5 kap. 6–7 §§ — required content and dating of a
    verifikation.
[3] BFL 3 kap. 1–3 §§ — definition of *räkenskapsår*, brutna
    räkenskapsår, and ändring av räkenskapsår.
[4] BFL 6 kap. 1 § — the duty to close the löpande bokföring for each
    räkenskapsår with an årsredovisning or ett årsbokslut.
[5] BFL 5 kap. 4 § — sidoordnad bokföring, e.g. leverantörsreskontra
    or kundreskontra, for counterparties with many transactions.
[6] ML — invoice-content rules requiring both parties'
    momsregistreringsnummer on cross-border/reverse-charge purchases.
[7] BFNAR 2013:2 — a leverantörsfaktura is treated as mottagen
    (received) on arrival at the company, ankomststämplad and assigned
    a löpnummer distinct from its own fakturanummer, so the
    leverantörsreskontra and the resulting verifikation stay traceable
    to one another.
[8] ÅRL 4 kap. 13 § — omräkning till svenska kronor of claims and
    liabilities denominated in foreign currency, relevant when a
    leverantörsfaktura's payment-date exchange rate differs from the
    rate used at booking.
[9] BFNAR 2013:2 — commentary on BFL 5 kap. 6 § noting that a
    kundnummer, alongside name+address, name+organisationsnummer, or a
    momsregistreringsnummer, is an accepted way to identify a motpart,
    provided the full customer details are recorded ("fullständiga
    uppgifter om kunden i kundregistret").
[10] SFL 26 kap. — the duty to report an individuppgift per anställd
     (personnummer/samordningsnummer, utbetald ersättning, gjort
     skatteavdrag) in each month's arbetsgivardeklaration på
     individnivå (AGI).
[11] SFL 10–11 kap. — skatteavdrag enligt skattetabell, and jämkning
     of that deduction on Skatteverket's decision.
[12] Lag (1991:586) om särskild inkomstskatt för utomlands bosatta
     (SINK) — the flat-rate alternative to table-based skatteavdrag for
     an anställd bosatt utomlands, relevant to the `tax_table`
     exception in §4.7.1.
[13] BFL 5 kap. 1 § — the duty to maintain a systemdokumentation
     describing the bookkeeping system's organisation and structure,
     "så att sambanden mellan systemdokumentationen och den löpande
     bokföringen enkelt kan utläsas"; a kontoplan is a core part of
     that documentation.
[14] ML, together with SFL 26 kap.'s periodic skattedeklaration
     provisions — the duty to report utgående and ingående moms per
     redovisningsperiod. The specific fält/ruta numbering used to do so
     is set by Skatteverket's blankett for the mervärdesskattedeklaration,
     not by a paragraf in ML or SFL, so — like [6] — this citation is
     at the chapter/form level rather than a specific paragraf.
