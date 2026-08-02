# Accounting Knowledge Bundle Specification

**Version 0.1 — Draft**

This document specifies how bookkeeping ("bokföring") knowledge is
represented as an [Open Knowledge Format](./reference/okf-spec-v01.md) (OKF)
bundle. It is a **profile** of OKF v0.1 (see [`okf-spec-v01.md`](./reference/okf-spec-v01.md))
for the accounting domain: every rule in OKF v0.1 applies unless this
document explicitly narrows it. Where this document uses a section
number in parentheses, e.g. "(OKF §4.1)", it refers to the
corresponding section of [`okf-spec-v01.md`](./reference/okf-spec-v01.md).

---

## 1. Purpose

OKF v0.1 deliberately requires only a `type` field (OKF §4.1) and
leaves everything else to the producer. That is correct for a
general-purpose format, but accounting is not general-purpose: Swedish
law dictates exactly what information must accompany every recorded
business event, who its parties are, and what must periodically be
declared from it. This profile takes the "producer-defined keys" escape
hatch that OKF explicitly allows (OKF §4.1, "Extensions") and uses it to:

- name a fixed set of concept types for the accounting domain —
  `Organization`, `Verification`, `Fiscal Year`, `Supplier`, `Supplier
  Invoice`, `Customer`, `Customer Invoice`, `Employee`, `Payslip`,
  `Chart of Accounts`, `Expense`, `Employer Tax Declaration`, and
  `VAT Declaration` (§4.1–§4.13);
- promote, per type, the legally mandated fields from optional to
  **required** (§4.x.1); and
- require, per type, the body sections that carry the per-row data
  frontmatter cannot express — a verifikation's konteringar, a
  räkenskapsårs balanser, a kontoplans konton, a deklarations rutor and
  individuppgifter (§4.x.2); and
- reserve an `archive/` directory (§5) where the underlag those types
  reference — kvitton, fakturor, kontoutdrag, importfiler — are kept in
  the form they were received, so that a bundle carries its own
  räkenskapsinformation instead of pointing outside itself.

Those types are not a flat list. The `Verification` (§4.2) is the
grundmaterial BFL requires for every affärshändelse; the rest exist
around it. `Organization` (§4.1) is the company whose bokföring it
belongs to, and `Fiscal Year` (§4.3) the räkenskapsår it falls in.
`Supplier` (§4.4), `Customer` (§4.6), and `Employee` (§4.8) hold the
master data of the motpart it names. `Supplier Invoice` (§4.5),
`Customer Invoice` (§4.7), `Payslip` (§4.9), and `Expense` (§4.11) hold
the underlying document (bokföringsunderlag) it rests on. `Chart of
Accounts` (§4.10) names the accounts it posts to. And `Employer Tax
Declaration` (§4.12) and `VAT Declaration` (§4.13) are the deklarationer
derived by aggregating verifikationer over a redovisningsperiod.

The primary legal source for these requirements is the Bokföringslag
(BFL); the moms-, fakturainnehålls-, löne-, and deklarationsrelaterade
requirements additionally draw on the Mervärdesskattelag (ML), the
Skatteförfarandelag (SFL), the Årsredovisningslag (ÅRL), and
Bokföringsnämndens allmänna råd (BFNAR), with fält- och rutanumrering
taken from Skatteverkets blanketter and arbetsställenummer from
Statistiska centralbyråns Företagsregister. See
[Citations](#7-citations) for the specific references.

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
  `counterparty` field (§4.2.1) names in free text when the
  affärshändelse is a purchase.
- **Leverantörsfaktura (Supplier Invoice)** — an invoice received from
  a leverantör for goods or services purchased; the document a
  `Verification`'s `supporting_documents` (§4.2.1) references when the
  affärshändelse is a purchase, and the accounting purpose this
  profile's `Supplier Invoice` concept type (§4.5) serves.
- **Leverantörsreskontra** — a sidoordnad bokföring (subsidiary
  ledger) recording, per leverantör, the invoices received and amounts
  owed (BFL 5 kap. 4 §); the accounting purpose this profile's
  `Supplier` (§4.4) and `Supplier Invoice` (§4.5) concept types jointly
  serve — `Supplier` holds the leverantör's master data, `Supplier
  Invoice` holds each invoice and amount owed.
- **Kund (Customer)** — the counterparty a company sells goods or
  services to; the "motpart" a `Verification`'s `counterparty` field
  (§4.2.1) names in free text when the affärshändelse is a sale.
- **Kundfaktura (Customer Invoice)** — an invoice issued to a kund for
  goods or services sold; the document a `Verification`'s
  `supporting_documents` (§4.2.1) references when the affärshändelse is
  a sale, and the accounting purpose this profile's `Customer Invoice`
  concept type (§4.7) serves.
- **Kundreskontra** — a sidoordnad bokföring (subsidiary ledger)
  recording, per kund, the invoices issued and amounts owed to the
  company (BFL 5 kap. 4 §); the accounting purpose this profile's
  `Customer` (§4.6) and `Customer Invoice` (§4.7) concept types jointly
  serve — `Customer` holds the kund's master data, `Customer Invoice`
  holds each invoice and amount owed.
- **Anställd (Employee)** — a natural person employed by the company in
  return for lön (salary/wages); the "motpart" a `Verification`'s
  `counterparty` field (§4.2.1) names in free text when the
  affärshändelse is a löneutbetalning (salary payment). The accounting
  purpose this profile's `Employee` concept type (§4.8) serves is the
  per-person identifying and tax-withholding data an arbetsgivare must
  hold to run löpande löneadministration and report each month's
  arbetsgivardeklaration på individnivå (AGI).
- **Lönespecifikation (Payslip)** — the specification an arbetsgivare
  issues an anställd for one löneperiod, breaking down how bruttolön
  (gross pay) becomes nettolön (net pay) through its lönearter: grundlön,
  tillägg, skattefria kostnadsersättningar (e.g. utlägg), avdragen skatt,
  and other avdrag. It sits between `Employee` and `Verification` the
  same way `Supplier Invoice` sits between `Supplier` and `Verification`
  (§4.5): the `Employee` is *who* the anställd is, the `Payslip`
  (§4.9) is *what was paid, for which period, and how it breaks down*,
  and the `Verification` (§4.2) is *how the resulting löneutbetalning
  was booked* — the lönespecifikation is the verifikation's underlying
  document (bokföringsunderlag), not the verifikation itself.
- **Utlägg (Expense)** — a business cost an anställd (or, in an
  aktiebolag, a närstående such as the owner) pays with personal
  funds on the company's behalf, creating a debt the company owes
  back to that person until reglerad (settled) — typically at the
  next löneutbetalning, alongside the `Payslip`'s (§4.9) other
  lönearter, or via a direct payout. Skatteverket treats an utlägg
  with no kvitto (receipt) preserved as not established, and
  requalifies it as taxable lön instead — this profile's `Expense`
  concept type (§4.11) exists to make that underlying kvitto and its
  reimbursement status explicit and checkable.
- **Kontoplan (Chart of Accounts)** — a bookkeeping system's complete
  list of accounts, each account's number and name, forming part of
  the systemdokumentation BFL 5 kap. 1 § requires (§7 [13]). This
  profile's `Chart of Accounts` concept type (§4.10) represents the
  kontoplan bundle-wide, one file per bundle rather than per
  räkenskapsår or per account — mirroring how `Supplier` (§4.4),
  `Customer` (§4.6), and `Employee` (§4.8) hold bundle-wide master data
  rather than duplicating it per fiscal year, but unlike them, as a
  single file rather than one file per entity.
- **Momsdeklaration (VAT Declaration)** — the periodic
  mervärdesskattedeklaration a VAT-registered company files with
  Skatteverket, reporting utgående and ingående moms and other
  VAT-relevant amounts per redovisningsperiod into a fixed set of
  numbered fält (rutor) that Skatteverket's blankett defines (SFL 26
  kap.). This profile's `Chart of Accounts` concept type (§4.10)
  records, per account, which of these fält (if any) the account's
  postings map into, so that a momsdeklaration can be derived by
  summing `Verification` (§4.2) postings per account and rolling them
  up via that mapping; this profile's `VAT Declaration` concept type
  (§4.13) is the artefakt that derivation produces — the declaration as
  assembled, avstämd against the bokföring, arkiverad, and lämnad to
  Skatteverket. The mapping is *how* a declaration is created and
  checked; the `VAT Declaration` is *what is filed and kept*.
- **Redovisningsmetod** — which händelse makes moms redovisningsbar in a
  given redovisningsperiod. Under **fakturametoden**
  (faktureringsmetoden), momsen redovisas när kund- och
  leverantörsfakturor skickas eller mottas. Under **kontantmetoden**
  (bokslutsmetoden), utgående moms redovisas först i den
  redovisningsperiod då betalning tas emot and ingående moms lyfts i den
  period då betalningen görs — with the further rule that vid
  räkenskapsårets utgång momsen även ska redovisas på obetalda fordringar
  och skulder. A company applies one metod, recorded once bundle-wide on
  the `Organization` concept (§4.1); each `VAT Declaration` (§4.13)
  restates it for the period it covers, since the metod decides which
  affärshändelser fall into that redovisningsperiod at all.
- **Arbetsgivardeklaration (Employer Tax Declaration)** — the monthly
  report an arbetsgivare files with Skatteverket for one
  redovisningsperiod, declaring utbetalda ersättningar, gjorda
  skatteavdrag, and arbetsgivaravgifter (SFL 26 kap.). It has two parts:
  a **huvuduppgift**, filed once per period for the whole company (e.g.
  summa arbetsgivaravgifter FK487, summa avdragen skatt FK497), and one
  **individuppgift** per betalningsmottagare (e.g. personnummer FK215,
  kontant ersättning FK011, avdragen skatt FK001) — the per-person
  breakdown `Employee` (§4.8) and `Payslip` (§4.9) already refer to as
  the "arbetsgivardeklaration på individnivå (AGI)". This profile's
  `Employer Tax Declaration` concept type (§4.12) represents one such
  declaration, aggregating a period's `Payslip` concepts into its
  individuppgifter and reconciling against the löneutbetalning
  `Verification`(s) (§4.2).
- **Organisation (Organization)** — the juridiska person (an aktiebolag,
  an enskild firma, or other) whose bokföring the bundle documents: the
  company itself, holding its own identitet (organisationsnummer, firma),
  skatteregistreringar (momsregistreringsnummer, F-skatt), teknisk
  kontaktperson for dealings with Skatteverket, and arbetsställen. The
  accounting purpose this profile's `Organization` concept type (§4.1)
  serves — bundle-wide, one file per bundle like `Chart of Accounts`
  (§4.10) — is to hold that egen masterdata once rather than repeating the
  organisationsnummer in every `Employer Tax Declaration` (§4.12) and
  elsewhere.
- **Arbetsställe (Workplace)** — a physical location (adress) where an
  arbetsgivare conducts verksamhet; Statistiska centralbyråns (SCB)
  Företagsregister assigns each arbetsställe an arbetsställenummer
  (CFAR-nummer). An arbetsgivare med fler än ett arbetsställe must report
  the relevant arbetsställenummer per betalningsmottagare in the
  arbetsgivardeklaration på individnivå (AGI) — Skatteverkets fältkod
  FK060. This profile's `Organization` concept type (§4.1) records the
  company's arbetsställen and their CFAR-nummer, so each `Employee`'s
  (§4.8) FK060 in an `Employer Tax Declaration`'s (§4.12) individuppgift
  resolves to an address.
- **Arkiv (Archive)** — the `archive/` directory at the bundle root,
  where räkenskapsinformation is kept in the form it was received or
  transferred to: the kvitton, fakturor, kontoutdrag,
  lönespecifikationer, deklarationsfiler, and import-underlag that the
  concepts describe but are not themselves. BFL requires both that such
  material be preserved (7 kap. 1–2 §§) and that a verifikation state
  "var de finns tillgängliga" (5 kap. 6–7 §§); the arkiv is where a
  bundle answers both at once. Its files are not concepts — OKF §3.1
  makes only `.md` files concept documents — so they carry no
  frontmatter and are reached by path: a `Verification`'s `resource` and
  `supporting_documents` (§4.2.1) point into the arkiv, and an
  `Expense`'s `resource` (§4.11.1), which this profile promotes from
  Recommended to required, MUST do so. See §5.

---

## 4. Concept Types

All example data in this section is fictitious. The organisationsnummer,
momsregistreringsnummer, and personnummer that appear in the examples are
constructed so as not to identify a real company or a real person: the
organisationsnummer carry a valid Luhn-kontrollsiffra but are not
registered with Bolagsverket, and the personnummer carry a deliberately
invalid kontrollsiffra. Producers of new examples MUST do the same.

### 4.1 `Organization`

An `Organization` concept represents the company itself: the juridiska
person (aktiebolag, enskild firma, or other) whose bokföring the bundle
documents. It holds the company's own master data — its identitet
(organisationsnummer, firma), skatteregistreringar
(momsregistreringsnummer, F-skatt), redovisningsmetod för moms, teknisk
kontaktperson for dealings with Skatteverket, and arbetsställen — that
other concept types otherwise have to repeat or leave implicit. In particular, the arbetsgivardeklaration
an `Employer Tax Declaration` (§4.12) represents must carry the
arbetsgivarens organisationsnummer (Skatteverkets fältkod FK201) and, in
each individuppgift, the betalningsmottagarens arbetsställenummer (FK060)
when the arbetsgivare has more than one arbetsställe (SFL 26 kap.); an
`Organization` concept is where that organisationsnummer and those
arbetsställen live.

Unlike `Supplier` (§4.4), `Customer` (§4.6), and `Employee` (§4.8) — which
are also bundle-wide master data, but one file per entity — an
`Organization` concept is a single file for the whole bundle, since a
bundle documents the bokföring of exactly one company. In this it mirrors
`Chart of Accounts` (§4.10): scoped to the company as a whole rather than to
any one `Fiscal Year` (§4.3), and represented as a single file rather than
one file per entity. Producers SHOULD update that single file in place —
bumping `timestamp` — when the company's details change, e.g. a new teknisk
kontaktperson or a nytt arbetsställe.

Concept ID convention: place the organization at the bundle root as
`organization.md`. There is exactly one `Organization` concept per bundle
— not one per fiscal year — so, like `Chart of Accounts` (§4.10) and unlike
§4.2–§4.9, no subdirectory or per-entity filename convention is needed.

#### 4.1.1 Frontmatter

```yaml
---
type: Organization                     # REQUIRED (OKF §4.1)
title: <Registered company name>       # REQUIRED
organization_number: <string>          # REQUIRED
vat_number: <string>                   # REQUIRED when applicable
workplace_number: <string>             # REQUIRED when applicable
f_tax_status: approved | not_approved  # Recommended
accounting_method: fakturametoden | kontantmetoden  # Recommended
registered_office: <string>            # Recommended
postal_address: <string>               # Recommended
workplace_address: <string>            # Recommended
technical_contact: <string>            # Recommended
technical_contact_email: <string>      # Recommended
technical_contact_phone: <string>      # Recommended
description: <Optional one-line summary>  # Recommended (OKF §4.1)
tags: [<tag>, …]                       # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>         # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `description`, `tags`, `timestamp`) keep
their OKF §4.1 meaning, with one change: `title` is **required** for
`Organization`, not merely recommended — promoted from OKF's generic
"Recommended" (OKF §4.1) for the same reason as `Customer.title` (§4.6.1)
and `Employee.title` (§4.8.1): a company concept without a firma does not
identify the company it describes.

**Required**, per SFL 26 kap. (arbetsgivardeklarationens huvuduppgift):

- `organization_number` — the company's own organisationsnummer (or, for
  an enskild firma, the innehavarens personnummer). This is the FK201 the
  arbetsgivardeklaration reports (§4.12.1) and the identity every other
  concept ultimately traces back to; recording it once here avoids
  repeating it in each `Employer Tax Declaration` (§4.12) and elsewhere.

**Required when applicable**, per Mervärdesskattelagen (ML) and SFL 26
kap. (individuppgiftens arbetsställenummer):

- `vat_number` — the company's momsregistreringsnummer, required whenever
  the company is registered for VAT, since it appears on every kundfaktura
  the company issues and governs its own mervärdesskattedeklaration.
  Mirrors `Supplier.vat_number` (§4.4.1). Omit for a company not
  registered for VAT.
- `workplace_number` — the primary arbetsställe's arbetsställenummer
  (CFAR-nummer), assigned by Statistiska centralbyråns (SCB)
  Företagsregister. Required whenever the company has been assigned one —
  i.e. has more than one arbetsställe — because an arbetsgivare med fler
  än ett arbetsställe must report the relevant arbetsställenummer per
  betalningsmottagare in the AGI individuppgift (FK060, §4.12.1). A
  company with a single arbetsställe, to which SCB assigns no
  arbetsställenummer, MAY omit it.

**Recommended**:

- `f_tax_status` — whether the company holds F-skatt (`approved`) or not
  (`not_approved`), mirroring `Supplier.f_tax_status` (§4.4.1). Relevant
  because a company invoicing for tjänster states its innehav av F-skatt
  on its kundfakturor.
- `accounting_method` — the company's redovisningsmetod för moms (§3):
  `fakturametoden`, where momsen redovisas när fakturor skickas eller
  mottas, or `kontantmetoden`, where den redovisas när betalning sker.
  Bundle-wide master data for the same reason `vat_number` is — a company
  applies one metod, not one per period — and recorded here so each
  `VAT Declaration` (§4.13) can be checked against the metod the company
  actually applies. Recommended rather than required because a company
  that is not momsregistrerad has no redovisningsmetod to state.
- `registered_office` — the bolagets säte (registered office / kommun), as
  stated in the company's registration and årsredovisning.
- `postal_address` — the company's postal/correspondence address, when it
  differs from `workplace_address`.
- `workplace_address` — the primary arbetsställe's physical address. When
  the company has more than one arbetsställe, list them all — with their
  arbetsställenummer — in the `# Arbetsställen` body section (§4.1.2).
- `technical_contact` — the name of the company's tekniska kontaktperson:
  the person Skatteverket and other myndigheter contact about the
  company's deklarationer and e-tjänster.
- `technical_contact_email` / `technical_contact_phone` — that contact
  person's e-postadress and telefonnummer.

**Arbetsställen**, per SFL 26 kap. (arbetsställenummer i individuppgiften):

An arbetsställe's address and arbetsställenummer are per-arbetsställe data,
not a single scalar, so — like a `Fiscal Year`'s balances (§4.3.1) or a
`Chart of Accounts`' accounts (§4.10.1) — when there is more than one
arbetsställe they belong in the body as a table, not in frontmatter:

- An `Organization` concept MUST include an `# Arbetsställen` body section
  (§4.1.2) whenever the company has more than one arbetsställe, listing
  each arbetsställe's address and arbetsställenummer (CFAR-nummer). Without
  it, an `Employee`'s (§4.8) FK060 in an `Employer Tax Declaration`'s
  (§4.12) individuppgift cannot be resolved to a specific arbetsställe. A
  company with a single arbetsställe MAY record it in `workplace_address`
  alone and omit the section.

#### 4.1.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Organization` concepts
SHOULD use:

| Heading           | Purpose                                                                                                                    |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| `# Arbetsställen`  | Each arbetsställe's address and arbetsställenummer (CFAR-nummer). REQUIRED when the company has more than one arbetsställe. |
| `# Contact`        | The tekniska kontaktpersonen and any other roller (e.g. firmatecknare, ekonomiansvarig).                                  |
| `# Citations`      | As OKF §8 — the legal or documentary basis, if not obvious from context.                                                  |

#### 4.1.3 Example

```markdown
---
type: Organization
title: Company AB
organization_number: "559999-9991"
vat_number: "SE559999999101"
workplace_number: "12345678"
f_tax_status: approved
accounting_method: fakturametoden
registered_office: Storstad
postal_address: Storgatan 1, 111 22 Storstad
workplace_address: Storgatan 1, 111 22 Storstad
technical_contact: Erik Karlsson
technical_contact_email: erik.karlsson@company.example
technical_contact_phone: "+46 8 123 45 67"
timestamp: 2026-07-01T09:00:00Z
---

[Company AB](https://company.example/), org.nr 559999-9991. Bolagets egen
masterdata: identitet, skatteregistreringar, redovisningsmetod för moms,
teknisk kontaktperson för deklarationer, och arbetsställen.
Organisationsnumret här är samma FK201 som varje
[arbetsgivardeklaration](/employer-tax-declarations/) (§4.12) rapporterar,
och redovisningsmetoden (fakturametoden) är den varje
[momsdeklaration](/vat-declarations/) (§4.13) tillämpar.

# Arbetsställen

| Arbetsställe | Adress                            | Arbetsställenummer (CFAR) |
| ------------- | --------------------------------- | -------------------------- |
| Huvudkontor   | Storgatan 1, 111 22 Storstad      | 12345678                   |
| Lager         | Industrivägen 4, 111 45 Storstad  | 87654321                   |

# Contact

Teknisk kontaktperson för deklarationer och e-tjänster: Erik Karlsson,
erik.karlsson@company.example, +46 8 123 45 67.

# Citations

[1] Skatteförfarandelagen (SFL) 26 kap. — arbetsgivardeklarationens
    organisationsnummer (FK201) och individuppgiftens arbetsställenummer
    (FK060).
[2] Statistiska centralbyrån (SCB), Företagsregistret — arbetsställenummer
    (CFAR-nummer) per arbetsställe.
```

---

### 4.2 `Verification`

A `Verification` concept represents exactly one verifikation: the
grundmaterial ("raw material") of all bookkeeping. Every
affärshändelse must have one (chapter 4, "Verifikationer").

Concept ID convention: place verifications under a `verifications/`
subdirectory, one file per verifikation, e.g.
`verifications/2026/000123.md`. Because BFL requires verifications to
be traceable in registration order via their `verification_number`
(§4.2.1 below), producers SHOULD choose filenames that preserve that
order.

#### 4.2.1 Frontmatter

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
  corrections) MAY omit it. When the handling is archived in the
  bundle's arkiv, the entry SHOULD state its bundle-relative path
  (§5) — that path is what answers "var de finns tillgängliga".

**Recommended**:

- `resource` — a URI to the scanned/original source document (kvitto,
  faktura, kontoutdrag, etc.), when one exists. SHOULD be a
  bundle-relative path under `archive/` (§5) when the document is
  archived with the bundle; an external URI is permitted but leaves the
  underlag outside it. Omit for a bokföringsorder that has no external
  document.
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

#### 4.2.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Verification`
concepts SHOULD use:

| Heading                  | Purpose                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------ |
| `# Postings`             | The kontering: which accounts are debited/credited and by how much.                  |
| `# Supporting Documents` | Expands on `supporting_documents`: where each referenced handling/avtal is archived. |
| `# Citations`            | As OKF §8 — the legal or documentary basis, if not obvious from context.             |

#### 4.2.3 Example

```markdown
---
type: Verification
verification_number: "2026-000123"
transaction_date: 2026-06-30
recorded_date: 2026-07-01
description: Inköp av kontorsmaterial från Kontorsvaruhuset AB
amount: 1250.00 SEK
counterparty: Kontorsvaruhuset AB
supporting_documents:
  - "Leverantörsfaktura #KV-88213, /archive/leverantorsfakturor/2026/KV-88213.pdf"
title: Inköp kontorsmaterial — faktura KV-88213
resource: "/archive/leverantorsfakturor/2026/KV-88213.pdf"
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
  `/archive/leverantorsfakturor/2026/KV-88213.pdf`.

# Citations

[1] Bokföringslagen (BFL) 5 kap. 6–7 §§
```

---

### 4.3 `Fiscal Year`

A `Fiscal Year` concept represents exactly one räkenskapsår: the period
the löpande bokföring is organized into and, at its end, closed off with
an annual closing (chapter 3, "Räkenskapsår"; chapter 6, "Hur den
löpande bokföringen avslutas"). Every `Verification` belongs to exactly
one fiscal year.

Concept ID convention: place fiscal years under a `fiscal-years/`
subdirectory, one file per räkenskapsår, e.g.
`fiscal-years/2025-2026.md`. Producers SHOULD use the same label for
the fiscal year's file and for its corresponding
`verifications/<label>/` subdirectory (§4.2), so the two can be
correlated without opening either.

#### 4.3.1 Frontmatter

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
  `verification_number` (§4.2.1) recorded in this fiscal year, e.g.
  `["V1", "V189"]`. Since BFL 5 kap. 6–7 §§ require verifications to be
  traceable via a löpande verifikationsnummer, this makes it checkable
  that the numbering within the year is complete, without opening every
  verification.

**Balances**, per BFL 6 kap. (bokslutets innehåll):

Account balances are per-account data, not a single scalar, so — like
a `Verification`'s kontering (§4.2.2) — they belong in the body as a
table, not in frontmatter:

- A `Fiscal Year` concept MUST include an `# Opening Balances` body
  section (§4.3.2), listing the ingående balans for every account.
  When `previous_fiscal_year` is set, these balances SHOULD equal that
  year's `# Closing Balances` — BFL requires a räkenskapsår's opening
  balances to tie to the prior year's closing balances, and restating
  them here makes that continuity checkable without opening the linked
  concept. For a first fiscal year with no `previous_fiscal_year`, the
  balances are zero for every account, but the section itself MUST
  still be present.
- A `Fiscal Year` concept MUST include a `# Closing Balances` body
  section (§4.3.2) once `status` is `closed`, listing the utgående
  balans for every account. A bokslut that does not state the closing
  position of every account is not complete.

#### 4.3.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Fiscal Year`
concepts SHOULD use:

| Heading              | Purpose                                                                                  |
| --------------------- | ------------------------------------------------------------------------------------------ |
| `# Verifications`     | A link to the fiscal year's `verifications/<label>/` subdirectory.                       |
| `# Opening Balances`  | The ingående balans per account at the start of the fiscal year. REQUIRED.                |
| `# Closing Balances`  | The utgående balans per account at the end of the fiscal year. REQUIRED once `status` is `closed`. |
| `# Closing`           | Narrative details of the årsbokslut/årsredovisning once `status` is `closed`.            |
| `# Citations`         | As OKF §8 — the legal or documentary basis, if not obvious from context.                 |

#### 4.3.3 Example

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

### 4.4 `Supplier`

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
concepts (§4.5).

Concept ID convention: place suppliers under a `suppliers/`
subdirectory, one file per leverantör, e.g.
`suppliers/kontorsvaruhuset-ab.md`. Producers SHOULD use a stable,
recognizable slug so a `Verification`'s free-text `counterparty`
(§4.2.1) can be matched to the corresponding `Supplier` concept
without ambiguity.

#### 4.4.1 Frontmatter

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
  (§4.2.1) names in free text. A foreign supplier with no Swedish-style
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

#### 4.4.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Supplier` concepts
SHOULD use:

| Heading               | Purpose                                                                  |
| ---------------------- | ------------------------------------------------------------------------- |
| `# Verifications`      | Links to verifications where this supplier is the `counterparty`.       |
| `# Supplier Invoices`  | Links to `Supplier Invoice` concepts (§4.5) received from this supplier. |
| `# Citations`          | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.4.3 Example

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

### 4.5 `Supplier Invoice`

A `Supplier Invoice` concept represents exactly one leverantörsfaktura:
a specific invoice received from a `Supplier` (§4.4), stating what is
owed, to whom, and by when. It sits between `Supplier` and
`Verification`: the `Supplier` is *who* the counterparty is, the
`Supplier Invoice` is *what was invoiced and when it falls due*, and
the `Verification` (§4.2) is *how the resulting affärshändelse was
booked* — the leverantörsfaktura is the verifikation's underlying
document (bokföringsunderlag), not the verifikation itself.

Concept ID convention: place supplier invoices under a
`supplier-invoices/` subdirectory, one file per leverantörsfaktura,
e.g. `supplier-invoices/2026/KV-88213.md`. Producers SHOULD name the
file after `invoice_number` so the corresponding leverantörsfaktura
can be located without opening it.

#### 4.5.1 Frontmatter

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

- `supplier` — the Concept ID of the `Supplier` (§4.4) who issued the
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
  `Verification.amount` (§4.2.1).
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

- `verification` — the Concept ID of the `Verification` (§4.2) that
  books this invoice.
- `payment_terms` — the betalningsvillkor stated on this invoice, when
  they differ from the `Supplier`'s default `payment_terms` (§4.4.1).

#### 4.5.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Supplier Invoice`
concepts SHOULD use:

| Heading         | Purpose                                                                  |
| ---------------- | ------------------------------------------------------------------------- |
| `# Line Items`  | The fakturarader: goods/services invoiced, quantities, and prices.       |
| `# Payment`     | The invoice's payment/reskontra status, to avoid double payment.        |
| `# Citations`   | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.5.3 Example

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
resource: "/archive/leverantorsfakturor/2026/KV-88213.pdf"
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

### 4.6 `Customer`

A `Customer` concept represents exactly one kund: a recurring motpart
in verifikationer, whose identifying and payment details would
otherwise have to be repeated in every `Verification` that names them
as `counterparty`. BFL requires a bookkeeping system with many
transactions against the same counterparty to maintain a sidoordnad
bokföring — a kundreskontra — through which those transactions can be
identified and reconciled (BFL 5 kap. 4 §). A `Customer` concept is
this profile's representation of the kund's master-data entry in that
kundreskontra; the individual invoices tracked within it are
represented by `Customer Invoice` concepts (§4.7).

Concept ID convention: place customers under a `customers/`
subdirectory, one file per kund, e.g. `customers/foretag-ab.md`.
Producers SHOULD use a stable, recognizable slug so a `Verification`'s
free-text `counterparty` (§4.2.1) can be matched to the corresponding
`Customer` concept without ambiguity.

#### 4.6.1 Frontmatter

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
  (§4.2.1), provided the full customer details are recorded here.
- `company_number` — the organisationsnummer of a legal person, or the
  personnummer of a sole trader or private individual, identifying the
  kund as the "motpart" a `Verification`'s `counterparty` field
  (§4.2.1) names in free text. A foreign or anonymous-at-point-of-sale
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

#### 4.6.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Customer` concepts
SHOULD use:

| Heading               | Purpose                                                                  |
| ---------------------- | ------------------------------------------------------------------------- |
| `# Verifications`      | Links to verifications where this customer is the `counterparty`.       |
| `# Customer Invoices`  | Links to `Customer Invoice` concepts (§4.7) issued to this customer.    |
| `# Citations`          | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.6.3 Example

```markdown
---
type: Customer
customer_number: "K-4471"
company_number: "556122-3347"
vat_number: "SE556122334701"
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

### 4.7 `Customer Invoice`

A `Customer Invoice` concept represents exactly one kundfaktura: a
specific invoice issued to a `Customer` (§4.6), stating what is owed,
by whom, and by when. It sits between `Customer` and `Verification`:
the `Customer` is *who* the counterparty is, the `Customer Invoice` is
*what was invoiced and when it falls due*, and the `Verification`
(§4.2) is *how the resulting affärshändelse was booked* — the
kundfaktura is the verifikation's underlying document
(bokföringsunderlag), not the verifikation itself.

Unlike `Supplier Invoice` (§4.5), a `Customer Invoice` has only one
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

#### 4.7.1 Frontmatter

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

- `customer` — the Concept ID of the `Customer` (§4.6) the invoice was
  issued to, rather than repeating their identifying details in free
  text.
- `invoice_number` — the fakturanummer the issuing company assigns,
  drawn from a sequential series (ML requires a faktura's löpnummer to
  make it uniquely identifiable within one or more series). Unlike
  `Supplier Invoice.invoice_number` (§4.5.1), this is the company's own
  number, not a counterparty's.
- `invoice_date` — fakturadatum: the date printed on the invoice, and —
  since the company controls issuance — the date that governs when the
  invoice must be booked (contrast `Supplier Invoice`, where
  `received_date` governs instead).
- `due_date` — förfallodatum: the date payment is due, without which
  the reskontra cannot flag an invoice as overdue.
- `amount` — the total sum owed, including currency, mirroring
  `Verification.amount` (§4.2.1).
- `payment_status` — whether the invoice is still owed (`unpaid`) or
  has been settled (`paid`). A kundreskontra exists specifically to
  track this per invoice, so that an already-paid invoice is not
  chased for payment again.

**Required when applicable**:

- `vat_amount` — the invoice's mervärdesskatt content, when the sale
  carries Swedish VAT.
- `payment_date` — the actual date payment was received. Required once
  `payment_status` is `paid`, mirroring `Supplier Invoice.payment_date`
  (§4.5.1).
- `currency` / `exchange_rate` — for an invoice issued in a foreign
  currency: the original currency and the exchange rate used at
  booking, since the rate at payment may differ and produce a
  valutakursvinst or -förlust (ÅRL 4 kap. 13 §).

**Recommended**:

- `verification` — the Concept ID of the `Verification` (§4.2) that
  books this invoice.
- `payment_terms` — the betalningsvillkor stated on this invoice, when
  they differ from the `Customer`'s default `payment_terms` (§4.6.1).

#### 4.7.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Customer Invoice`
concepts SHOULD use:

| Heading         | Purpose                                                                  |
| ---------------- | ------------------------------------------------------------------------- |
| `# Line Items`  | The fakturarader: goods/services invoiced, quantities, and prices.       |
| `# Payment`     | The invoice's payment/reskontra status, to track outstanding amounts.   |
| `# Citations`   | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.7.3 Example

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

### 4.8 `Employee`

An `Employee` concept represents exactly one anställd: a person the
company pays lön to, and for whom the company must hold enough
identifying and tax data to run löpande löneadministration and to
report each month's arbetsgivardeklaration på individnivå (AGI) —
the per-person breakdown of paid ersättning and gjorda skatteavdrag
that Skatteförfarandelagen (SFL) has required since 2019 (26 kap.).
An `Employee` concept is this profile's representation of that
per-person master data; the individual löneutbetalningar are recorded,
like any other affärshändelse, as `Verification` concepts (§4.2) that
name the employee as `counterparty`.

Concept ID convention: place employees under an `employees/`
subdirectory, one file per anställd, e.g.
`employees/anna-svensson.md`. Producers SHOULD use a stable,
recognizable slug so a `Verification`'s free-text `counterparty`
(§4.2.1) can be matched to the corresponding `Employee` concept
without ambiguity.

#### 4.8.1 Frontmatter

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
(§4.6.1): a löneutbetalning's `counterparty` names the anställd by
name, and that name has to resolve to a concept.

**Required when applicable**, per SFL 26 kap. (individuppgift i
arbetsgivardeklaration på individnivå) and 10–11 kap. (skatteavdrag
enligt skattetabell och jämkning):

- `personal_number` — the personnummer (or, for a foreign anställd not
  in folkbokföringen, a samordningsnummer) identifying the anställd as
  the "motpart" a `Verification`'s `counterparty` field (§4.2.1) names
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
  (§4.4.1).
- `end_date` — the anställd's last day of employment. Required once
  the anställning has ended.

**Recommended**:

- `employment_number` — the anställningsnummer, if the company assigns
  one.
- `start_date` — the anställningsdatum.
- `employment_type` — whether the anställd is paid `monthly`
  (månadslön), `hourly` (timlön), or a `board_fee` (styrelsearvode).
- `position` — the anställdas befattning.

#### 4.8.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Employee` concepts
SHOULD use:

| Heading          | Purpose                                                                   |
| ----------------- | -------------------------------------------------------------------------- |
| `# Verifications` | Links to verifications where this employee is the `counterparty`.        |
| `# Citations`     | As OKF §8 — the legal or documentary basis, if not obvious from context. |

#### 4.8.3 Example

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

### 4.9 `Payslip`

A `Payslip` concept represents exactly one lönespecifikation: the
breakdown an arbetsgivare gives an `Employee` (§4.8) for one löneperiod,
stating what was paid and how the bruttolön (gross pay) became the
nettolön (net pay) actually transferred. It sits between `Employee` and
`Verification`, mirroring how `Supplier Invoice` (§4.5) sits between
`Supplier` and `Verification`: the `Employee` is *who* the anställd is,
the `Payslip` is *what was paid, for which period, and how it breaks
down*, and the `Verification` (§4.2) is *how the resulting
löneutbetalning was booked* — the lönespecifikation is the
verifikation's underlying document (bokföringsunderlag), not the
verifikation itself.

Concept ID convention: place payslips under a `payslips/` subdirectory,
one file per lönespecifikation, e.g.
`payslips/2026/anna-svensson-2026-06.md`. Unlike a leverantörsfaktura
or kundfaktura, a lönespecifikation carries no invoice-style löpnummer
of its own, so producers SHOULD name the file after the anställd's slug
and the löneperiod instead.

#### 4.9.1 Frontmatter

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

- `employee` — the Concept ID of the `Employee` (§4.8) the
  lönespecifikation was issued to, rather than repeating their
  identifying details in free text.
- `start_date` / `end_date` — the löneperiod the specifikationen
  covers, mirroring `Fiscal Year.start_date`/`end_date` (§4.3.1). A
  löneperiod MAY be shorter than a full month — for example, an
  anställd who börjar or slutar sin anställning mid-period — so both
  dates are required rather than a single period label.
- `payment_date` — utbetalningsdagen: the date lönen was actually
  transferred, mirroring `Supplier Invoice.payment_date`/`Customer
  Invoice.payment_date` (§4.5.1/§4.7.1) and the date the `Verification`
  (§4.2) booking the löneutbetalning should carry as its
  `transaction_date`.
- `gross_pay` — bruttolönen: the sum of all lönearter before avdrag,
  and one of the two per-anställd figures SFL 26 kap. requires
  reporting each month in the AGI individuppgift.
- `tax_withheld` — the avdragna preliminärskatten: the second of the
  two per-anställd figures SFL 26 kap. requires in the AGI
  individuppgift.
- `net_pay` — nettolönen actually paid out, mirroring
  `Verification.amount` (§4.2.1) so the lönespecifikation can be
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
  `Verification`'s kontering (§4.2.2).
- `verification` — the Concept ID of the `Verification` (§4.2) that
  books the löneutbetalning.
- `resource` — a URI to the original lönebesked document, when one
  exists.

#### 4.9.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Payslip` concepts
SHOULD use:

| Heading         | Purpose                                                                                    |
| ---------------- | -------------------------------------------------------------------------------------------- |
| `# Line Items`  | The lönearter: salary components, benefits, cost reimbursements (e.g. utlägg), and deductions that sum from `gross_pay` to `net_pay`. |
| `# Citations`   | As OKF §8 — the legal or documentary basis, if not obvious from context.                   |

#### 4.9.3 Example

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

### 4.10 `Chart of Accounts`

A `Chart of Accounts` concept represents the kontoplan: the company's
complete list of bookkeeping accounts, their names, and — where
relevant — which field of the periodic mervärdesskattedeklaration each
account's postings map into. BFL requires every bookkeeping system to
be accompanied by a systemdokumentation describing the system's
organisation and structure, "så att sambanden mellan
systemdokumentationen och den löpande bokföringen enkelt kan utläsas"
(BFL 5 kap. 1 §) — a kontoplan is a core part of that documentation,
since without it the accounts referenced by every `Verification`'s
kontering (§4.2.2) and every `Fiscal Year`'s balances (§4.3.1) cannot
be understood on their own. Separately, a VAT-registered company must
file a periodic mervärdesskattedeklaration reporting utgående and
ingående moms, among other amounts, per redovisningsperiod (SFL 26
kap.); Skatteverket's blankett for that declaration divides these
amounts into a fixed set of numbered fält (rutor). A `Chart of
Accounts` concept lets tooling derive that declaration automatically,
by summing `Verification` postings per account and rolling the sums up
through this account-to-fält mapping. The declaration so derived is then
recorded as a `VAT Declaration` concept (§4.13), which is what gets
arkiverad and lämnad to Skatteverket: this mapping stays the means of
*producing* and re-checking a declaration, not a substitute for the
filed artefakt itself.

Unlike `Supplier` (§4.4), `Customer` (§4.6), and `Employee` (§4.8) —
which are also bundle-wide master data, but one file per entity — a
`Chart of Accounts` concept is a single file for the whole bundle,
since the systemdokumentation BFL 5 kap. 1 § requires describes the
bookkeeping system as a whole, not one leverantör, kund, or anställd at
a time. It is also, like `Supplier`/`Customer`/`Employee`, scoped to
the company as a whole rather than to any one `Fiscal Year` (§4.3): a
kontoplan may occasionally be revised, but it is not duplicated per
räkenskapsår, and producers SHOULD update the single file in place —
bumping `timestamp` — when accounts are added, renamed, or remapped.

Concept ID convention: place the chart of accounts at the bundle root
as `chart-of-accounts.md`. There is exactly one `Chart of Accounts`
concept per bundle — not one file per account and not one per fiscal
year — so, unlike §4.2–§4.9, no subdirectory or per-entity filename
convention is needed.

#### 4.10.1 Frontmatter

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
Year`'s balances (§4.3.1) — they belong in the body as a table, not in
frontmatter:

- A `Chart of Accounts` concept MUST include an `# Accounts` body
  section (§4.10.2), listing every account number and account name the
  bookkeeping system uses. A systemdokumentation that omits accounts
  actually posted to in `Verification` concepts (§4.2.2) does not let
  "sambanden mellan systemdokumentationen och den löpande bokföringen"
  be readily understood, as BFL 5 kap. 1 § requires.
- The VAT Declaration Field column is **required when applicable**:
  populate it for every account whose transactions are to be summed
  into a specific field (ruta) of the periodic
  mervärdesskattedeklaration — for example an utgående-moms account, an
  ingående-moms account, or an EU purchase/sale account. Leave it empty
  for accounts with no such mapping, e.g. a bank account or an
  inventory account, whose postings never enter the moms return.

#### 4.10.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Chart of Accounts`
concepts SHOULD use:

| Heading      | Purpose                                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------------------------ |
| `# Accounts` | The kontoplan: every account number and name, and, where applicable, the momsdeklaration field it maps to. REQUIRED. |
| `# Citations` | As OKF §8 — the legal or documentary basis, if not obvious from context.                                        |

#### 4.10.3 Example

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

### 4.11 `Expense`

An `Expense` concept represents exactly one utlägg: a business cost an
anställd (or, in an aktiebolag, a närstående such as the owner) has
paid with personal funds on the company's behalf, creating a debt the
company owes back to that person. It sits between `Employee` (§4.8)
and `Verification`/`Payslip` (§4.9): the `Employee` is *who* paid
privately, the `Expense` is *what was paid, evidenced by which kvitto,
and whether/how it has been reimbursed*, and the `Verification` (§4.2)
is *how the resulting cost and debt were booked* — the kvitto is the
verifikation's underlying document (bokföringsunderlag), not the
verifikation itself.

An utlägg is booked in two steps, and this profile's fields exist to
keep both traceable: the cost and any moms are booked immediately
against a debt-to-employee account when the outlay occurs, and that
debt is later settled — often bundled into the employee's next
`Payslip` as an untaxed löneart rather than paid out directly. A
bookkeeping guide's own worked example of a failed audit illustrates
why the kvitto matters: an utlägg claimed with no kvitto preserved was
requalified by Skatteverket as ordinary lön, triggering
arbetsgivaravgifter and a skattetillägg on top. This profile therefore
promotes OKF's generic `resource` field (OKF §4.1) from Recommended to
**required** for `Expense` — an utlägg concept with no referenced
kvitto does not evidence a real utlägg.

Concept ID convention: place expenses under an `expenses/`
subdirectory, one file per utlägg, e.g.
`expenses/2026/anna-svensson-2026-06-03.md`. Like a `Payslip` (§4.9),
an utlägg carries no invoice-style löpnummer of its own, so producers
SHOULD name the file after the anställd's slug and the
`expense_date` instead.

#### 4.11.1 Frontmatter

```yaml
---
type: Expense                      # REQUIRED (OKF §4.1)
employee: <Concept ID>             # REQUIRED
expense_date: <ISO 8601 date>      # REQUIRED
description: <string>              # REQUIRED
amount: <decimal> <ISO 4217 code>  # REQUIRED
resource: </archive/… path to kvitto>  # REQUIRED
reimbursement_status: unpaid | paid  # REQUIRED
vat_amount: <decimal> <ISO 4217 code>  # REQUIRED when applicable
reimbursement_date: <ISO 8601 date>    # REQUIRED when applicable
currency: <ISO 4217 code>          # REQUIRED when applicable
exchange_rate: <decimal>           # REQUIRED when applicable
verification: <Concept ID>         # Recommended
payslip: <Concept ID>              # Recommended
title: <Optional display name>     # Recommended (OKF §4.1)
tags: [<tag>, …]                   # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>     # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `tags`, `timestamp`) keep
their OKF §4.1 meaning, with two changes: `description` is **required**
for `Expense`, not merely recommended, mirroring
`Verification.description` (§4.2.1); and `resource` is **required**,
not merely recommended, for the reason given above.

**Required**:

- `employee` — the Concept ID of the `Employee` (§4.8) who paid the
  utlägg with personal funds, rather than repeating their identifying
  details in free text.
- `expense_date` — the date the utlägg was made: when the anställd
  actually paid with personal funds, mirroring
  `Verification.transaction_date` (§4.2.1).
- `description` — what the utlägg concerns — what was bought or which
  cost it covers, e.g. kontorsmaterial, en tjänsteresa, or
  trängselskatt. Stricter than OKF's generic "one-sentence summary"
  (OKF §4.1), mirroring `Verification.description` (§4.2.1).
- `amount` — the total sum the anställd paid, including any moms.
- `resource` — the kvitto: promoted to required, since a bookkeeping
  guide notes that "den anställde måste spara alla kvitton för att det
  ska betraktas som ett utlägg och vara avdragsgillt för företaget" —
  without a referenced kvitto, an `Expense` concept does not evidence an
  utlägg at all. For the same reason the value MUST be a bundle-relative
  path under `archive/` (§5) resolving to a file that is present: an
  external URI records that a kvitto once existed, not that it has been
  preserved.
- `reimbursement_status` — whether the debt to the anställd is still
  owed (`unpaid`) or has been settled (`paid`). Exists so that, when
  reglering happens via the next `Payslip` (§4.9) rather than a direct
  payout, tooling can confirm the payout was booked against the debt
  account rather than kostnadsförd a second time as lön.

**Required when applicable**:

- `vat_amount` — the utlägg's mervärdesskatt content, when the
  underlying cost carried Swedish VAT and the moms was lyft
  separately in the kontering.
- `reimbursement_date` — the regleringsdag: the date the debt was
  actually settled. Required once `reimbursement_status` is `paid`,
  since the settling `Verification`'s `transaction_date` (§4.2.1)
  SHOULD equal this date.
- `currency` / `exchange_rate` — for an utlägg paid in a foreign
  currency, e.g. kost och logi i utlandet: the original currency and
  the exchange rate used at booking.

**Recommended**:

- `verification` — the Concept ID of the `Verification` (§4.2) that
  books the utlägg's cost and the resulting debt to the anställd, at
  the time the outlay occurred.
- `payslip` — the Concept ID of the `Payslip` (§4.9) that reimburses
  this utlägg as one of its lönearter, when reglering happens that
  way rather than through a separate direct payout.

#### 4.11.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Expense` concepts
SHOULD use:

| Heading           | Purpose                                                                              |
| ------------------ | --------------------------------------------------------------------------------------- |
| `# Receipt`       | The kvitto: what it shows, whose name it is issued to, and where it is archived.       |
| `# Reimbursement` | How and when the debt to the anställd was (or will be) reglerad, and against which account/Verification/Payslip. |
| `# Citations`     | As OKF §8 — the legal or documentary basis, if not obvious from context.                 |

#### 4.11.3 Example

```markdown
---
type: Expense
employee: "employees/anna-svensson"
expense_date: 2026-06-03
description: Kontorsmaterial inköpt med privata medel till kontoret
amount: 450.00 SEK
vat_amount: 90.00 SEK
resource: "/archive/kvitton/2026/anna-svensson-kontorsmaterial-2026-06-03.pdf"
reimbursement_status: paid
reimbursement_date: 2026-06-25
verification: "verifications/2026/000178"
payslip: "payslips/2026/anna-svensson-2026-06"
title: Utlägg, kontorsmaterial — Anna Svensson
timestamp: 2026-06-03T14:00:00Z
---

[Anna Svensson](/employees/anna-svensson.md) lade ut 450.00 kr privat
för kontorsmaterial till kontoret 2026-06-03. Kostnaden och momsen
bokfördes samma dag som en skuld till Anna. Skulden reglerades
2026-06-25 som en rad på hennes lönespecifikation för juni 2026 — se
[payslips/2026/anna-svensson-2026-06](/payslips/2026/anna-svensson-2026-06.md).

# Receipt

Kvitto från Kontorsvaruhuset AB, utställt på Anna Svensson, arkiverat
under `/archive/kvitton/2026/anna-svensson-kontorsmaterial-2026-06-03.pdf`.

# Reimbursement

Skulden bokades upp 2026-06-03 mot
[verifications/2026/000178](/verifications/2026/000178.md). Reglerad
2026-06-25 som raden "Utlägg, kontorsmaterial" (450.00 kr) på
lönespecifikationen för juni 2026, mot skuldkontot — inte kostnadsförd
en andra gång som lön.

# Citations

[1] Bokföringslagen (BFL) 5 kap. 6–7 §§
```

---

### 4.12 `Employer Tax Declaration`

An `Employer Tax Declaration` concept represents exactly one
arbetsgivardeklaration: the monthly report an arbetsgivare must file
with Skatteverket for one redovisningsperiod, declaring the utbetalda
ersättningar, gjorda skatteavdrag, and arbetsgivaravgifter for that
month (SFL 26 kap.). It sits *above* `Payslip` (§4.9) the way `Fiscal
Year` (§4.3) sits above `Verification` (§4.2): a single
arbetsgivardeklaration aggregates a whole period's löneutbetalningar
into one huvuduppgift for the company and one individuppgift per
betalningsmottagare — each individuppgift corresponding to one
`Payslip` (§4.9) — and the whole declaration reconciles against the
löneutbetalning `Verification`(s) (§4.2) that booked the month's lön.

Like the momsdeklaration (§4.13), an arbetsgivardeklaration is
represented as a stored concept: it records the period's assembled
huvuduppgift and individuppgifter — and, in its body, how they were
derived. What differs is where the derivation comes from. A
momsdeklaration has a bundle-wide account-to-fält mapping to roll up
through, held in the `Chart of Accounts` (§4.10), so tooling can
recompute it from `Verification` postings alone. An
arbetsgivardeklaration has no equivalent mapping: its individuppgifter
are per-anställd and already materialized as `Payslip` concepts (§4.9),
so its `# Derivation` section (§4.12.2) traces back to those concepts
rather than to a kontoplan.

Concept ID convention: place employer tax declarations under an
`employer-tax-declarations/` subdirectory, one file per
redovisningsperiod, e.g. `employer-tax-declarations/2026-02.md`.
Producers SHOULD name the file after the `period` (`YYYY-MM`) so the
declaration for a given month can be located without opening it.

#### 4.12.1 Frontmatter

```yaml
---
type: Employer Tax Declaration     # REQUIRED (OKF §4.1)
period: <YYYY-MM>                  # REQUIRED
organization_number: <string>     # REQUIRED
status: draft | final             # REQUIRED
total_employer_contributions: <decimal> <ISO 4217 code>  # REQUIRED
total_tax_withheld: <decimal> <ISO 4217 code>            # REQUIRED
submitted_date: <ISO 8601 date>   # REQUIRED when status: final
filing_deadline: <ISO 8601 date>  # Recommended
payslips: [<Concept ID>, …]       # Recommended
verifications: [<Concept ID>, …]  # Recommended
title: <Optional display name>    # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
resource: <Optional URI to source document>  # Recommended (OKF §4.1)
tags: [<tag>, …]                  # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>    # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `description`, `resource`,
`tags`, `timestamp`) keep their OKF §4.1 meaning.

**Required**, per SFL 26 kap. (arbetsgivardeklaration med huvuduppgift
och individuppgift):

- `period` — the redovisningsperiod the declaration covers, as
  `YYYY-MM` (Skatteverkets fältkod FK006). One arbetsgivardeklaration is
  filed per calendar month.
- `organization_number` — the arbetsgivarens organisationsnummer
  (FK201), identifying the company that filed the declaration — the same
  organisationsnummer recorded once, bundle-wide, in the `Organization`
  concept (§4.1).
- `status` — whether the declaration is still being assembled (`draft`)
  or has been filed with Skatteverket (`final`). Mirrors
  `Fiscal Year.status` (§4.3.1): a `draft` declaration MAY still have
  incomplete underlag (described in the body), whereas a `final` one has
  been submitted and its huvuduppgift and individuppgifter are complete.
- `total_employer_contributions` — the summa arbetsgivaravgifter och
  särskild löneskatt for the period (FK487), including currency; the
  huvuduppgift's aggregate avgiftsbelopp.
- `total_tax_withheld` — the summa avdragen skatt for the period
  (FK497), including currency; the huvuduppgift's aggregate skatteavdrag.

**Required when applicable**:

- `submitted_date` — the date the declaration was lämnad (filed) to
  Skatteverket. Required once `status` is `final`, mirroring
  `Fiscal Year.closing_date` (§4.3.1). SFL 26 kap. requires the
  declaration to be filed by a deadline — normally the 12th of the month
  after the redovisningsperiod, the 17th for the January and August
  periods — so `submitted_date` SHOULD fall on or before
  `filing_deadline`.

**Recommended**:

- `filing_deadline` — the date by which the declaration must be filed:
  normally the 12th of the month following `period`, or the 17th for the
  January and August periods. Derivable from `period`, so recommended
  rather than required, but producers SHOULD populate it to make the
  deadline checkable by tooling.
- `payslips` — the Concept IDs of the `Payslip` concepts (§4.9) whose
  löneperioder fall in this redovisningsperiod, one per individuppgift,
  rather than repeating each anställd's figures in free text.
- `verifications` — the Concept IDs of the löneutbetalning
  `Verification` concepts (§4.2) the huvuduppgift is reconciled against,
  so tooling can check that FK487/FK497 tie to the booked personalskatt
  and sociala avgifter.

**Huvuduppgift and individuppgifter**, per SFL 26 kap.:

The per-betalningsmottagare individuppgifter are per-anställd data, not
a single scalar, so — like a `Fiscal Year`'s balances (§4.3.1) or a
`Chart of Accounts`' accounts (§4.10.1) — they belong in the body as a
table, not in frontmatter:

- An `Employer Tax Declaration` concept MUST include a `# Huvuduppgift`
  body section (§4.12.2), stating the company-level fältkoder for the
  period — at least FK487 (`total_employer_contributions`) and FK497
  (`total_tax_withheld`). A huvuduppgift is filed once per
  redovisningsperiod for the whole company.
- An `Employer Tax Declaration` concept MUST include an
  `# Individuppgift` body section (§4.12.2), with one row per
  betalningsmottagare: FK215 (personnummer/samordningsnummer), FK011
  (kontant ersättning som är underlag för arbetsgivaravgifter), any
  FK012/FK013 (skattepliktiga förmåner), FK001 (avdragen skatt), and —
  when the arbetsgivare has more than one arbetsställe — FK060
  (arbetsställenummer), resolved to a specific arbetsställe via the
  `Organization` concept (§4.1). SFL 26 kap. requires an individuppgift
  per betalningsmottagare; a declaration that states only period totals
  does not meet that bar.

#### 4.12.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `Employer Tax
Declaration` concepts SHOULD use:

| Heading            | Purpose                                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `# Period`         | The redovisningsperiod and its filing deadline.                                                                  |
| `# Huvuduppgift`   | The period's company-level fältkoder (FK487, FK497, and underlag). REQUIRED.                                     |
| `# Individuppgift` | One row per betalningsmottagare (FK215, FK011, FK012/FK013, FK001), each linked to its `Employee` (§4.8)/`Payslip` (§4.9). REQUIRED. |
| `# Derivation`     | How the huvuduppgift and individuppgifter were derived from the period's `Payslip` concepts and löneutbetalning `Verification`(s). |
| `# Citations`      | As OKF §8 — the legal or documentary basis, if not obvious from context.                                         |

#### 4.12.3 Example

```markdown
---
type: Employer Tax Declaration
period: "2026-06"
organization_number: "559999-9991"
status: draft
total_employer_contributions: 10240.00 SEK
total_tax_withheld: 8100.00 SEK
filing_deadline: 2026-07-12
payslips: ["payslips/2026/anna-svensson-2026-06"]
verifications: ["verifications/2026/000201"]
title: Arbetsgivardeklaration — juni 2026
timestamp: 2026-07-01T09:00:00Z
---

Arbetsgivardeklaration för Company AB (org.nr 559999-9991) avseende
redovisningsperioden juni 2026. Härledd från månadens enda
lönespecifikation och den bokförda löneutbetalningen. Ännu inte lämnad
till Skatteverket (`status: draft`).

# Period

Redovisningsperiod 2026-06 (2026-06-01 – 2026-06-30). Ska enligt SFL
26 kap. lämnas senast 2026-07-12 (den 12:e i månaden efter perioden).

# Huvuduppgift

En huvuduppgift lämnas per redovisningsperiod, för hela företaget.

| Fältkod | Beskrivning                        | Belopp        |
| ------- | ----------------------------------- | -------------: |
| FK006   | Redovisningsperiod                  | 2026-06        |
| FK201   | Arbetsgivarens organisationsnummer  | 559999-9991    |
| FK487   | Summa arbetsgivaravgifter och SLF   | 10 240.00 SEK  |
| FK497   | Summa avdragen skatt                | 8 100.00 SEK   |

# Individuppgift

En individuppgift per betalningsmottagare, härledd ur månadens
[`Payslip`](/payslips/2026/anna-svensson-2026-06.md)-koncept.

| Betalningsmottagare                          | FK215         | FK011         | FK001        |
| --------------------------------------------- | ------------- | -------------: | -----------: |
| [Anna Svensson](/employees/anna-svensson.md)  | 19850612-1234 | 32 000.00 SEK  | 8 100.00 SEK |

# Derivation

FK011 = lönespecifikationens bruttolön (32 000.00 SEK); FK001 =
Payslip-fältet `tax_withheld` (8 100.00 SEK); FK487 =
`employer_contributions` (10 240.00 SEK) — samtliga hämtade ur
[payslips/2026/anna-svensson-2026-06](/payslips/2026/anna-svensson-2026-06.md).
Huvuduppgiftens FK497 (8 100.00 SEK) stäms av mot personalskatten och
FK487 mot de sociala avgifterna i
[verifications/2026/000201](/verifications/2026/000201.md).

# Citations

[1] Skatteförfarandelagen (SFL) 26 kap.
[2] Skatteverket, "Så fyller du i arbetsgivardeklarationen – ruta för
    ruta":
    https://www.skatteverket.se/foretag/arbetsgivare/lamnaarbetsgivardeklaration/safyllerduiarbetsgivardeklarationen.4.2cf1b5cd163796a5c8b66a8.html
```

---

### 4.13 `VAT Declaration`

A `VAT Declaration` concept represents exactly one momsdeklaration: the
periodic mervärdesskattedeklaration a momsregistrerat företag must file
with Skatteverket for one redovisningsperiod, reporting the period's
momspliktiga försäljning, utgående moms, momspliktiga inköp med omvänd
betalningsskyldighet, momsfri försäljning, and avdragsgill ingående moms
(SFL 26 kap.). A momsregistrerat företag files one for every period even
when there is no moms to declare.

It stands in the same relation to `Chart of Accounts` (§4.10) that
`Employer Tax Declaration` (§4.12) stands in to `Payslip` (§4.9), but
built the other way round. The `Chart of Accounts`' account-to-fält
mapping is what lets tooling *create* a momsdeklaration — summing
`Verification` (§4.2) postings per account and rolling the sums up into
the numbered fält of Skatteverket's blankett. A `VAT Declaration` is the
artefakt that creation produces: the declaration as assembled for a
specific period, avstämd against the bokföring, arkiverad, and lämnad to
Skatteverket. The mapping can be re-run at any time and will yield the
same fält; it cannot record that a declaration was in fact filed, on what
date, for what belopp, or that it was later rättad. That is what this
concept type is for.

A filed momsdeklaration is therefore never edited in place. When an
amount turns out to be wrong, producers file a rättelse: a new `VAT
Declaration` concept for the same `period`, pointing back at the one it
supersedes via `replaces`, while the superseded concept's `status`
becomes `corrected`. The bundle keeps both, so the filing history of a
period stays readable.

Concept ID convention: place VAT declarations under a
`vat-declarations/` subdirectory, one file per redovisningsperiod, e.g.
`vat-declarations/2026-02.md` (månad), `vat-declarations/2026-Q1.md`
(kvartal), or `vat-declarations/2026.md` (beskattningsår). Producers
SHOULD name the file after the `period` so the declaration for a given
period can be located without opening it, and SHOULD suffix a rättelse
with its ordinal, e.g. `vat-declarations/2026-02-rattelse-1.md`, so it
does not collide with the declaration it supersedes.

#### 4.13.1 Frontmatter

```yaml
---
type: VAT Declaration                # REQUIRED (OKF §4.1)
period: <YYYY-MM | YYYY-Qn | YYYY>   # REQUIRED
period_type: månad | kvartal | beskattningsår  # REQUIRED
organization_number: <string>        # REQUIRED
vat_number: <string>                 # REQUIRED
status: draft | final | corrected    # REQUIRED
accounting_method: fakturametoden | kontantmetoden  # REQUIRED
total_output_vat: <decimal> <ISO 4217 code>  # REQUIRED
total_input_vat: <decimal> <ISO 4217 code>   # REQUIRED
vat_to_pay: <decimal> <ISO 4217 code>        # REQUIRED
submitted_date: <ISO 8601 date>      # REQUIRED when status: final | corrected
replaces: <Concept ID>               # REQUIRED when the declaration is a rättelse
filing_deadline: <ISO 8601 date>     # Recommended
verifications: [<Concept ID>, …]     # Recommended
chart_of_accounts: <Concept ID>      # Recommended
title: <Optional display name>       # Recommended (OKF §4.1)
description: <Optional one-line summary>  # Recommended (OKF §4.1)
resource: <Optional URI to source document>  # Recommended (OKF §4.1)
tags: [<tag>, …]                     # Optional (OKF §4.1)
timestamp: <ISO 8601 datetime>       # Recommended (OKF §4.1)
---
```

The generic OKF fields (`type`, `title`, `description`, `resource`,
`tags`, `timestamp`) keep their OKF §4.1 meaning.

**Required**, per SFL 26 kap. and Skatteverkets blankett för
mervärdesskattedeklaration:

- `period` — the redovisningsperiod the declaration covers, written to
  match `period_type`: `YYYY-MM` for a kalendermånad, `YYYY-Qn` for a
  kalenderkvartal, `YYYY` for ett helt beskattningsår.
- `period_type` — whether the redovisningsperiod is a kalendermånad
  (`månad`), a kalenderkvartal (`kvartal`), or hela beskattningsåret
  (`beskattningsår`). Which of these a company may use depends on its
  beskattningsunderlag: helårsredovisning is open only below 1 mkr,
  kvartalsredovisning below 40 mkr, and a company above 40 mkr must
  redovisa per månad. The period type also governs the
  deklarationstidpunkt, so it cannot be inferred from `period` alone —
  `2026-02` is a valid month for a company on either månads- or
  kvartalsredovisning.
- `organization_number` — the company's organisationsnummer, the same one
  recorded once, bundle-wide, in the `Organization` concept (§4.1).
- `vat_number` — the company's momsregistreringsnummer, likewise from the
  `Organization` concept (§4.1). Required here, rather than "required when
  applicable" as in §4.1.1, because only a momsregistrerat företag files a
  momsdeklaration at all: a declaration without one describes a company
  that had no duty to file it.
- `status` — whether the declaration is still being assembled (`draft`),
  has been lämnad to Skatteverket (`final`), or has been lämnad and
  subsequently superseded by a rättelse (`corrected`). Extends the
  `draft`/`final` pair used by `Employer Tax Declaration.status` (§4.12.1)
  and `Fiscal Year.status` (§4.3.1) with the third state a filed
  momsdeklaration can reach.
- `accounting_method` — the redovisningsmetod (§3) applied for this
  period: `fakturametoden` or `kontantmetoden`. Restates, per declaration,
  the metod the `Organization` concept (§4.1.1) records bundle-wide,
  because the metod decides which affärshändelser belong to this
  redovisningsperiod at all — under kontantmetoden an obetald
  leverantörsfaktura contributes nothing until it is paid, whereas under
  fakturametoden it contributes on receipt. A reader cannot check the
  period's avgränsning without it.
- `total_output_vat` — the period's summa utgående moms, including
  currency: fält 10–12 (försäljning), 30–32 (inköp med omvänd
  betalningsskyldighet), and 60–62 (import) taken together.
- `total_input_vat` — the period's ingående moms att dra av (fält 48),
  including currency.
- `vat_to_pay` — moms att betala eller få tillbaka (fält 49), including
  currency: `total_output_vat` minus `total_input_vat`. A negative value
  is a momsfordran — moms att få tillbaka — rather than an error. Fält 49
  is filled in for every period, so producers MUST state it even when it
  is zero.

**Required when applicable**:

- `submitted_date` — the date the declaration was lämnad to Skatteverket.
  Required once `status` is `final` or `corrected`, mirroring
  `Employer Tax Declaration.submitted_date` (§4.12.1). It SHOULD fall on
  or before `filing_deadline`; momsen ska dessutom vara inbetald och
  bokförd på skattekontot senast samma dag.
- `replaces` — the Concept ID of the `VAT Declaration` this one rättar.
  Required whenever the declaration is a rättelse rather than a period's
  first filing. The superseded concept SHOULD in turn carry
  `status: corrected`, so the relation is readable from either end.

**Recommended**:

- `filing_deadline` — the date by which the declaration must be lämnad.
  Unlike `Employer Tax Declaration.filing_deadline` (§4.12.1), this is
  *not* derivable from the period alone: it follows from `period_type`
  together with whether the company's beskattningsunderlag exceeds 40
  mkr, which this profile does not record anywhere. For månads- and
  kvartalsredovisning the deadline is normally den 12:e i den andra
  månaden efter redovisningsperioden (den 17:e for the January and August
  deadlines); a company above 40 mkr instead files den 26:e i månaden
  efter perioden (den 27:e in December); helårsredovisning falls den 12
  maj året efter beskattningsårets utgång, or den 26 februari for a
  company with EU-handel. Producers SHOULD populate the field so tooling
  can check the deadline without reconstructing which of these cases
  applies.
- `verifications` — the Concept IDs of the `Verification` concepts (§4.2)
  the declaration is avstämd against: at minimum the omföring that emptied
  the moms accounts into momsredovisningskontot (§4.13.2, `# Avstämning`).
- `chart_of_accounts` — the Concept ID of the `Chart of Accounts` concept
  (§4.10) whose account-to-fält mapping the fält were rolled up through,
  so a reader can re-run the derivation against the same mapping. A bundle
  has exactly one (§4.10), but naming it makes the dependency explicit
  rather than implied.

**Rutor**, per Skatteverkets blankett för mervärdesskattedeklaration:

The declaration's fält are per-fält data, not a single scalar, so — like
an `Employer Tax Declaration`'s individuppgifter (§4.12.1) or a `Chart of
Accounts`' accounts (§4.10.1) — they belong in the body as a table, not in
frontmatter:

- A `VAT Declaration` concept MUST include a `# Rutor` body section
  (§4.13.2), with one row per ifyllt fält: fältnummer, the fält's
  beskrivning, and belopp. The three frontmatter totals are aggregates and
  do not stand in for it — fält 05–08 (momspliktig försäljning) and 35–42
  (försäljning undantagen från moms) carry beskattningsunderlag rather
  than moms, so they contribute to no total yet must still be declared. A
  declaration stating only `vat_to_pay` does not reflect the blankett, for
  the same reason §4.12.1 rejects an arbetsgivardeklaration stating only
  period totals.
- Fält belopp are stated as they are declared: öresbelopp avrundas nedåt
  ("öretal bortfaller"), which is why the fält in `# Rutor` may differ by
  ören from the exact kontosaldon the `# Derivation` section (§4.13.2)
  sums. Producers SHOULD say where that differens was booked — typically
  konto 3740, öresutjämning.

**Avstämning**, per BFL 5 kap. 1 § (systemdokumentation) and the
kontoplan's moms accounts (§4.10):

- A `VAT Declaration` concept MUST include an `# Avstämning` body section
  (§4.13.2), recording the omföring that reconciles the declaration to the
  bokföring: the utgående-moms accounts (261x–263x) and ingående-moms
  account (264x) tömda for the period, and the differens between them
  booked to momsredovisningskontot — 2650 for a momsskuld, or 1650 when
  the company regularly carries a momsfordran or holds one at bokslutet.
  Without it, the fält in `# Rutor` assert amounts that no `Verification`
  (§4.2) accounts for, and the declaration floats free of the löpande
  bokföring that BFL 5 kap. 1 § requires it to connect back to. Producers
  SHOULD perform the avstämning before the next redovisningsperiod
  begins, so a balansrapport for the period shows nollställda moms
  accounts and a single belopp on 2650 or 1650.

#### 4.13.2 Conventional body sections

In addition to the OKF §4.2 conventional headings, `VAT Declaration`
concepts SHOULD use:

| Heading         | Purpose                                                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `# Period`      | The redovisningsperiod, its period_type, the deklarationstidpunkt, and the redovisningsmetod governing the period's avgränsning.        |
| `# Rutor`       | One row per ifyllt fält of Skatteverkets blankett: fältnummer, beskrivning, belopp. REQUIRED.                                          |
| `# Derivation`  | Which accounts rolled up into which fält, via the `Chart of Accounts`' (§4.10) account-to-fält mapping.                                |
| `# Avstämning`  | The omföring of 261x–263x and 264x to momsredovisningskontot (2650/1650), the öresavrundning, and the `Verification` that booked it. REQUIRED. |
| `# Rättelse`    | When the declaration rättar an earlier one: what was wrong, and what changed. Present whenever `replaces` is set.                      |
| `# Citations`   | As OKF §8 — the legal or documentary basis, if not obvious from context.                                                              |

#### 4.13.3 Example

```markdown
---
type: VAT Declaration
period: "2026-02"
period_type: månad
organization_number: "559999-9991"
vat_number: "SE559999999101"
status: final
accounting_method: fakturametoden
total_output_vat: 32000.00 SEK
total_input_vat: 21500.00 SEK
vat_to_pay: 10500.00 SEK
submitted_date: 2026-04-10
filing_deadline: 2026-04-13
verifications: ["verifications/2026/000144"]
chart_of_accounts: "chart-of-accounts"
title: Momsdeklaration — februari 2026
timestamp: 2026-04-10T14:30:00Z
---

Momsdeklaration för Company AB (org.nr 559999-9991, momsreg.nr
SE559999999101) avseende redovisningsperioden februari 2026. Härledd ur
periodens verifikationer via kontoplanens fältmappning
([chart-of-accounts](/chart-of-accounts.md), §4.10) och lämnad till
Skatteverket 2026-04-10.

# Period

Redovisningsperiod 2026-02 (2026-02-01 – 2026-02-28), månadsredovisning.
Deklarationstidpunkt: den 12:e i den andra månaden efter perioden, dvs
2026-04-12 — en söndag, varför fristen infaller nästkommande vardag
2026-04-13. Momsen ska vara inbetald och bokförd på skattekontot senast
samma dag.

Företaget tillämpar fakturametoden: moms redovisas när kund- och
leverantörsfakturor skickas respektive mottas, inte när betalning sker.
Obetalda fakturor utställda eller mottagna i februari ingår därför i
denna period.

# Rutor

| Fält | Beskrivning                                              | Belopp         |
| ---- | -------------------------------------------------------- | -------------: |
| 05   | Momspliktig försäljning som inte ingår i fält 06, 07, 08  | 120 000 SEK    |
| 10   | Utgående moms 25 %                                       | 30 000 SEK     |
| 21   | Inköp av tjänster från annat EU-land, huvudregeln         | 8 000 SEK      |
| 30   | Utgående moms 25 % på inköp i fält 20–24                 | 2 000 SEK      |
| 48   | Ingående moms att dra av                                 | 21 500 SEK     |
| 49   | Moms att betala eller få tillbaka                        | 10 500 SEK     |

# Derivation

Fälten är summerade per konto och upprullade via kontoplanens *VAT
Declaration Field*-mappning ([chart-of-accounts](/chart-of-accounts.md)):

| Konto  | Kontonamn                                    | Fält | Saldo februari |
| ------ | -------------------------------------------- | ---- | --------------: |
| 3001   | Försäljning inom Sverige, 25 % moms          | 05   | 120 000.00 SEK  |
| 2611   | Utgående moms på försäljning inom Sverige    | 10   | 30 000.00 SEK   |
| 4535   | Inköp av tjänster från annat EU-land, 25 %   | 21   | 8 000.00 SEK    |
| 2614   | Utgående moms omvänd skattskyldighet, 25 %   | 30   | 2 000.00 SEK    |
| 2640   | Ingående moms                                | 48   | 21 500.00 SEK   |

Fält 49 = (30 000 + 2 000) − 21 500 = 10 500 SEK att betala.

# Avstämning

Momskontona tömdes per 2026-02-28, innan mars påbörjades. Utgående moms
[2611] 30 000 kr och [2614] 2 000 kr debiterades, ingående moms [2640]
21 500 kr krediterades, och mellanskillnaden 10 500 kr bokfördes som
momsskuld på [2650] i väntan på betalning — se
[verifications/2026/000144](/verifications/2026/000144.md). Efter
omföringen är 2611, 2614 och 2640 nollställda i balansrapporten för
perioden.

Inga öresdifferenser uppstod denna period; hade de gjort det skulle de
ha bokförts mot öresutjämning [3740], eftersom öretal bortfaller i
momsdeklarationen.

# Citations

[1] Skatteförfarandelagen (SFL) 26 kap.; Mervärdesskattelagen (ML)
[2] Bokföringslagen (BFL) 5 kap. 1 § — avstämningen mot den löpande
    bokföringen
[3] Skatteverket, "Fylla i momsdeklarationen":
    https://www.skatteverket.se/foretag/moms/deklareramoms/fyllaimomsdeklarationen.4.3a2a542410ab40a421c80004214.html
```

---

## 5. Archive

The concept types in §4 describe affärshändelser and the parties to
them; they are not the underlag those descriptions rest on. A kvitto, a
mottagen leverantörsfaktura, a kontoutdrag, an inlämnad
deklarationsfil, or the SIE-, CSV-, or Excel-fil an earlier
bokföring was imported from is räkenskapsinformation in its own right,
and BFL requires it to be preserved — "i ordnat skick och på
betryggande och överskådligt sätt" for seven years after the end of the
kalenderår in which the räkenskapsår ended (7 kap. 1–2 §§) — and each
verifikation to state "var de finns tillgängliga" (5 kap. 6–7 §§).

This profile answers both with one convention: a bundle keeps that
material in an `archive/` directory at its root.

```
bundle/
├── index.md
├── organization.md
├── chart-of-accounts.md
├── verifications/2026/000123.md
├── expenses/2026/anna-svensson-2026-06-03.md
└── archive/
    ├── leverantorsfakturor/2026/KV-88213.pdf
    ├── kvitton/2026/anna-svensson-kontorsmaterial-2026-06-03.pdf
    ├── kontoutdrag/2026/2026-06.csv
    └── import/2024-2025-sie4.se
```

**Archived files are not concepts.** OKF §3.1 makes every non-reserved
`.md` file a concept document; an arkivfil is a PDF, CSV, XLSX, SIE,
XML, or image and therefore falls outside that model entirely — it has
no frontmatter and no `type`, and consumers reach it by path rather
than by Concept ID. To keep that distinction decidable without parsing,
producers MUST NOT place concept documents under `archive/`. A bundle
remains OKF-conformant either way: OKF §9 constrains `.md` files only.

**Referencing an archived file.** Concepts point into the arkiv with a
bundle-relative path (OKF §5.1) — `/archive/kvitton/2026/…pdf` — both
in `resource` and in ordinary markdown links in the body. This is the
recommended form for the same reason OKF gives: it survives the bundle
being cloned, zipped, or moved, which a `file:///` URI into the
producer's own filesystem does not. A concept MAY carry an external URI
instead when the original is held in a system outside the bundle, but
the bundle then no longer carries its own räkenskapsinformation.

**When the underlag is required.** Where this profile promotes
`resource` from OKF's Recommended to **Required** — today `Expense`
(§4.11.1), whose kvitto is what distinguishes an utlägg from taxable
lön — the value MUST be a bundle-relative path under `archive/`
resolving to a file that is present in the bundle. An external URI does
not satisfy the requirement: the rule exists to establish that the
kvitto is preserved, not that it was seen once.

**Organizing the arkiv.** Subdirectories SHOULD mirror the concept
directories they serve — `archive/leverantorsfakturor/2026/` alongside
`supplier-invoices/2026/`, `archive/kvitton/2026/` alongside
`expenses/2026/` — and filenames SHOULD reuse the referencing concept's
business identifier (`KV-88213.pdf`) or its Concept ID slug
(`anna-svensson-2026-06-03.pdf`), so a file and the concept describing
it can be found from each other. Beyond that this profile fixes no
taxonomy; an `archive/import/` holding the filer an earlier bokföring
was imported from is as legitimate a subdirectory as one named after a
concept type.

**Preservation.** An arkivfil inherits the arkiveringsplikt of the
verifikation that references it: `Verification.retention_until`
(§4.2.1) covers the verifikation *and* the underlag it names, since BFL
7 kap. 2 § counts both as räkenskapsinformation. A scanned pappersfaktura
placed in the arkiv is an överföring to another form under BFL 7 kap.
6 §, which is what permits the mottagna originalet to be destroyed
before the seven years are up — provided the transfer was done "på ett
betryggande sätt", i.e. the scan is legible, complete, and kept.

---

## 6. Conformance

A bundle is conformant with this profile if it satisfies OKF v0.1
conformance (OKF §9) **and**, additionally:

- every concept with `type: Organization` has `title` and
  `organization_number`, plus `vat_number` whenever the company is
  registered for VAT and `workplace_number` whenever the company has been
  assigned an arbetsställenummer; and includes an `# Arbetsställen` body
  section (§4.1.2) whenever the company has more than one arbetsställe
  (§4.1.1).
- every concept with `type: Verification` has all fields listed as
  "Required" in §4.2.1, plus `supporting_documents` whenever the
  underlying affärshändelse in fact had a referenced agreement or
  document;
- every concept with `type: Fiscal Year` has all fields listed as
  "Required" in §4.3.1, plus `closing_date` and `closing_method`
  whenever `status` is `closed`; includes an `# Opening Balances` body
  section (§4.3.2); and includes a `# Closing Balances` body section
  (§4.3.2) whenever `status` is `closed`.
- every concept with `type: Supplier` has `company_number` and
  `vat_number` whenever the underlying leverantör in fact has such a
  number, and at least one of `bankgiro`, `plusgiro`, or
  `bank_account` whenever the supplier is paid electronically (§4.4.1).
- every concept with `type: Supplier Invoice` has all fields listed as
  "Required" in §4.5.1, plus `vat_amount` whenever the purchase carries
  Swedish VAT, `payment_date` whenever `payment_status` is `paid`, and
  `currency`/`exchange_rate` whenever the invoice is issued in a
  foreign currency (§4.5.1).
- every concept with `type: Customer` has `title`, plus
  `customer_number`, `company_number`, and `vat_number` whenever the
  underlying kund in fact has such an identifier (§4.6.1).
- every concept with `type: Customer Invoice` has all fields listed as
  "Required" in §4.7.1, plus `vat_amount` whenever the sale carries
  Swedish VAT, `payment_date` whenever `payment_status` is `paid`, and
  `currency`/`exchange_rate` whenever the invoice is issued in a
  foreign currency (§4.7.1).
- every concept with `type: Employee` has `title`, plus
  `personal_number`, `address`, `tax_table`, `tax_adjustment`, and
  `bank_account` whenever the underlying anställd in fact has such
  data on file; `tax_column` whenever `tax_table` is present; and
  `end_date` whenever the anställning has ended (§4.8.1).
- every concept with `type: Payslip` has all fields listed as
  "Required" in §4.9.1, plus `other_deductions` whenever a deduction
  beyond `tax_withheld` was made (§4.9.1).
- every concept with `type: Chart of Accounts` includes an `# Accounts`
  body section (§4.10.2) listing every account number and account name
  the bookkeeping system uses, with the VAT Declaration Field populated
  for every account whose transactions map to a field of the periodic
  mervärdesskattedeklaration (§4.10.1).
- every concept with `type: Expense` has all fields listed as
  "Required" in §4.11.1 — including `resource`, promoted from OKF's
  generic Recommended — plus `vat_amount` whenever the utlägg carried
  Swedish VAT, `reimbursement_date` whenever `reimbursement_status` is
  `paid`, and `currency`/`exchange_rate` whenever the utlägg was paid
  in a foreign currency (§4.11.1); and its `resource` is a
  bundle-relative path under `archive/` resolving to a file present in
  the bundle (§5).
- every concept with `type: Employer Tax Declaration` has all fields
  listed as "Required" in §4.12.1, plus `submitted_date` whenever
  `status` is `final`; includes a `# Huvuduppgift` body section
  (§4.12.2); and includes an `# Individuppgift` body section (§4.12.2)
  with one row per betalningsmottagare (§4.12.1).
- every concept with `type: VAT Declaration` has all fields listed as
  "Required" in §4.13.1, plus `submitted_date` whenever `status` is
  `final` or `corrected` and `replaces` whenever the declaration rättar an
  earlier one; includes a `# Rutor` body section (§4.13.2) with one row
  per ifyllt fält, fält 49 among them in every period; and includes an
  `# Avstämning` body section recording the omföring to
  momsredovisningskontot (§4.13.1).
- no concept document (`.md`) is placed under `archive/`, and every
  bundle-relative `resource` or `supporting_documents` path pointing
  into `archive/` resolves to a file present in the bundle (§5).

As with OKF itself (OKF §9), consumers MUST NOT reject a
`Verification`, `Fiscal Year`, `Supplier`, `Supplier Invoice`,
`Customer`, `Customer Invoice`, `Employee`, `Payslip`, `Chart of
Accounts`, `Expense`, `Employer Tax Declaration`, `VAT Declaration`, or
`Organization` concept over missing "Recommended" fields — only over
missing "Required" (or applicable "Required when applicable") fields.

---

## 7. Citations

The requirements in §4.2, §4.4, §4.5, §4.6, and §4.7 are drawn directly
from the Bokföringslag (BFL, SFS 1999:1078); for `Supplier`'s and
`Customer`'s VAT numbers and `Supplier Invoice`'s/`Customer Invoice`'s
invoice-content fields, the Mervärdesskattelag (ML, SFS 2023:200); for
`Supplier Invoice`'s and `Customer Invoice`'s foreign-currency fields,
the Årsredovisningslag (ÅRL, SFS 1995:1554); for `Supplier
Invoice`'s `received_date`/`sequence_number` and `Customer`'s
`customer_number`, Bokföringsnämndens allmänna råd om bokföring (BFNAR
2013:2); for `Employee`'s identifying and tax-withholding fields
(§4.8), the Skatteförfarandelag (SFL, SFS 2011:1244) and, for the
`tax_table` exception, Lag (1991:586) om särskild inkomstskatt för
utomlands bosatta (SINK); for `Payslip`'s ersättnings- and
skatteavdrag fields (§4.9), the same Bokföringslag provisions as §4.2
and the same Skatteförfarandelag provisions as §4.8; for `Chart of
Accounts` (§4.10), the Bokföringslag's systemdokumentation requirement
for the concept type's existence, and the Mervärdesskattelag together
with the Skatteförfarandelag's periodic skattedeklaration provisions
for the VAT-declaration-field mapping itself; for `Expense`'s
kvitto and reimbursement fields (§4.11), the same Bokföringslag
provisions as §4.2; and for `Employer Tax Declaration`'s huvuduppgift
and individuppgift fields (§4.12), the Skatteförfarandelag's
arbetsgivardeklaration provisions (SFL 26 kap., the same chapter as
§4.8's AGI reference) together with Skatteverkets fältkoder for the
declaration's blankett; for `VAT Declaration` (§4.13), the
Mervärdesskattelag together with the Skatteförfarandelag's periodic
skattedeklaration provisions — the same pairing as §4.10's fält mapping,
here as the basis for the filed declaration itself — with the fält
numbering and the deklarationstidpunkter taken from Skatteverkets
blankett and vägledning; and for `Organization` (§4.1), the same
Skatteförfarandelag arbetsgivardeklaration provisions (SFL 26 kap.) for
the organisationsnummer (FK201) and arbetsställenummer (FK060), together
with Statistiska centralbyråns Företagsregister for the arbetsställenummer
(CFAR-nummer) itself; and for the `archive/` directory (§5), the
Bokföringslag's arkiveringsbestämmelser (BFL 7 kap.) together with the
same 5 kap. 6–7 §§ provisions as §4.2 for the duty to state where an
underlag is available:

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
     exception in §4.8.1.
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
[15] BFL 5 kap. 6–7 §§ — same provision as [2]: an utlägg's kvitto is
     the handling that legat till grund för affärshändelsen, and its
     absence is why an unsubstantiated utlägg fails to evidence a real
     verifikationsunderlag, as illustrated by a bookkeeping guide's own
     worked example of Skatteverket requalifying an undocumented utlägg
     as taxable lön.
[16] SFL 26 kap. — same chapter as [10], viewed here as the basis for
     the `Employer Tax Declaration` concept type as a whole: the duty to
     file an arbetsgivardeklaration per redovisningsperiod, comprising a
     huvuduppgift for the company and an individuppgift per
     betalningsmottagare, and the tidpunkt för lämnande (normally the
     12th of the month after the redovisningsperiod, the 17th for the
     January and August periods).
[17] Skatteverket, "Så fyller du i arbetsgivardeklarationen – ruta för
     ruta" — the fältkoder (FK006, FK201, FK011, FK012, FK013, FK001,
     FK215, FK487, FK497, …) used in the huvuduppgift and individuppgift.
     As with [6] and [14], the specific fältkod numbering is set by
     Skatteverket's blankett, not by a paragraf in SFL, so this citation
     is at the form level.
     https://www.skatteverket.se/foretag/arbetsgivare/lamnaarbetsgivardeklaration/safyllerduiarbetsgivardeklarationen.4.2cf1b5cd163796a5c8b66a8.html
[18] SFL 26 kap. — same chapter as [10] and [16], the basis for
     `Organization`'s arbetsgivardeklaration-relaterade fält: the
     arbetsgivarens organisationsnummer (FK201) in the huvuduppgift, and
     the arbetsställenummer (FK060) reported per betalningsmottagare in the
     individuppgift when the arbetsgivare has more than one arbetsställe.
[19] Statistiska centralbyrån (SCB), Företagsregistret — the
     arbetsställenummer (CFAR-nummer) assigned to each arbetsställe. As
     with [6], [14], and [17], the numbering is set by an authority's
     register/blankett rather than by a paragraf in law, so this citation
     is at the register level.
[20] ML, together with SFL 26 kap. — same provisions as [14], viewed here
     as the basis for the `VAT Declaration` concept type as a whole: the
     duty of a momsregistrerat företag to lämna a mervärdesskatte-
     deklaration for every redovisningsperiod, even when there is no moms
     to declare; the redovisningsperiod being en kalendermånad, ett
     kalenderkvartal, or hela beskattningsåret according to the company's
     beskattningsunderlag (1 mkr and 40 mkr being the thresholds); the
     redovisningsmetod (fakturametoden or kontantmetoden) governing when
     utgående and ingående moms become redovisningsbara; and the
     deklarationstidpunkt per period type.
[21] Skatteverket, "Fylla i momsdeklarationen" — the fält (rutor) of the
     blankett and their grouping: A. Momspliktig försäljning eller uttag
     (05–08), B. Utgående moms på försäljning eller uttag (10–12),
     C. Momspliktiga inköp vid omvänd betalningsskyldighet (20–24),
     D. Utgående moms på inköp i fält 20–24 (30–32), E. Försäljning m.m.
     som är undantagen från moms (35–42), F. Ingående moms (48),
     G. Moms att betala eller få tillbaka (49), and H. Import (50,
     60–62). As with [6], [14], and [17], the fält numbering is set by
     Skatteverkets blankett rather than by a paragraf in ML or SFL, so
     this citation is at the form level.
     https://www.skatteverket.se/foretag/moms/deklareramoms/fyllaimomsdeklarationen.4.3a2a542410ab40a421c80004214.html
[22] BFL 5 kap. 1 § — same provision as [13], applied in §4.13 to the
     `# Avstämning` section: the omföring emptying the utgående- and
     ingående-moms accounts to momsredovisningskontot (2650/1650) is what
     keeps "sambanden mellan systemdokumentationen och den löpande
     bokföringen" readable from a filed momsdeklaration back to the
     verifikationer it summarises.
[23] BFL 7 kap. 1–2 §§ — the forms räkenskapsinformation may be
     preserved in (dokument, mikroskrift, maskinläsbart medium), and the
     duty to preserve it "i ordnat skick och på betryggande och
     överskådligt sätt" until the seventh year after the end of the
     kalenderår in which the räkenskapsår ended. This is the same
     seven-year duty §4.2.1's `retention_until` makes checkable, applied
     in §5 to the underlag a verifikation references rather than to the
     verifikation itself.
[24] BFL 7 kap. 6 § — överföring av räkenskapsinformation to another
     form: material received from someone else may be destroyed from the
     fourth year after the end of the kalenderår in which the
     räkenskapsår ended, provided the information has been transferred
     "på ett betryggande sätt" to the form the company preserves it in.
     This is what a scanned pappersfaktura placed in the arkiv (§5) is.
