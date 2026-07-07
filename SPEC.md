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
**required**, for one concept type: `Verification`.

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

## 5. Conformance

A bundle is conformant with this profile if it satisfies OKF v0.1
conformance (OKF §9) **and**, additionally, every concept with
`type: Verification` has all fields listed as "Required" in §4.1.1,
plus `supporting_documents` whenever the underlying affärshändelse in
fact had a referenced agreement or document.

As with OKF itself (OKF §9), consumers MUST NOT reject a
`Verification` concept over missing "Recommended" fields — only over
missing "Required" (or applicable "Required when applicable") fields.

---

## 6. Citations

The requirements in §4.1 are drawn directly from the Bokföringslag
(BFL, SFS 1999:1078):

[1] BFL 1 kap. 2 §, 6–7 p. — definitions of *affärshändelse* and
    *verifikation*.
[2] BFL 5 kap. 6–7 §§ — required content and dating of a
    verifikation.
