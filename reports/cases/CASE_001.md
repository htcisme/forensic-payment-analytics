# CASE_001 — Same-day transport entries with matching recorded details

**Review date:** 1 November 2026  
**Status:** Needs additional evidence  
**Rule:** R1, `r1_with_cost_center_v1`

## 1. Reason for selection

Two positive source records share a transaction date, lightly standardized supplier name, amount, cost center and expense code. R1 identifies them as a two-member review group. This is an example of how to inspect an alert, not a verified irregular payment.

## 2. Evidence and source references

- CSV snapshot SHA256: `b477e61ca2dd3c53359188cb9e7926c76d115e639d3eab0e11a3ae8a755a19a9`.
- Source record numbers: **2 and 3**, counted from the first data record after the header. These are not bank transaction identifiers.
- Group ID: `b477e61ca2dd3c53359188cb9e7926c76d115e639d3eab0e11a3ae8a755a19a9:R1:00005`.
- Full record IDs: the CSV snapshot hash above followed by `:2` and `:3`.
- Publication page: https://www.cambridge.gov.uk/procurement-card-spend
- PDF inspected: https://www.cambridge.gov.uk/media/hvkp24wv/procurement-card-transactions-2026-27.pdf
- PDF snapshot SHA256: `247134f6f9b7a0d2e7f38c07cca0da68ede696e68176083e1b78c0b3fa99669b`.
- PDF location: **page 1**, second and third data rows below the header, following the HUWS GRAY CAMBRIDGE entry. The downloaded PDF has 163 pages.

The corresponding source records were inspected in the CSV, and page 1 of the PDF was both text-extracted and visually checked. The source PDF and rendered page are not bundled in this code package; use the link and hash to identify the inspected publication.

## 3. Recorded observations

| Source record | Date         | Supplier            | Gross amount | Expense code | Cost center in CSV                                   |
| ------------- | ------------ | ------------------- | -----------: | ------------ | ---------------------------------------------------- |
| 2             | 1 April 2026 | STAGECOACH SERVICES |      £140.00 | 60914        | Asylum Seekers and Refugee Resettlements (Community) |
| 3             | 1 April 2026 | STAGECOACH SERVICES |      £140.00 | 60914        | Asylum Seekers and Refugee Resettlements (Community) |

Both records have the expense type `Public Transport For Staff And Members`. Their combined recorded value is £280.00. That value is not a calculated loss or an estimate of an incorrect payment.

## 4. CSV/PDF comparison

The two entries are also visible on page 1 of the PDF. The date, supplier, Inclusive amount and expense code agree with the CSV for these records. The PDF uses a four-digit year, while the CSV displays a two-digit year.

The inspected PDF page does **not display the Cost Center Name column**. The shared cost center used by R1 is supported by the CSV only; it has not been verified from the PDF. The PDF also does not provide an invoice number or independent payment reference for these entries.

This comparison confirms that the repeated recorded characteristics appear in both published formats. These are two representations of published information, not independent confirmation of two bank payments or a duplicate payment.

## 5. Possible explanations

- Separate, legitimate transport purchases with the same price and accounting classification.
- A repeated entry in the publication or its preparation process.
- A duplicate underlying payment requiring verification.

The available fields do not distinguish between these possibilities. No supplier misconduct is established.

## 6. Information required

| Additional evidence                                   | Question it would address                     |
| ----------------------------------------------------- | --------------------------------------------- |
| Invoice/receipt numbers and purchase descriptions     | Do the records relate to different purchases? |
| Payment or card transaction references                | Were there two distinct underlying payments?  |
| Purchase/service dates and relevant order records     | Were separate services or tickets supplied?   |
| Supporting accounting entries, corrections or refunds | Was either entry reversed or corrected?       |

These are proposed follow-up checks. No request has been sent to the council or supplier as part of this portfolio exercise.

## 7. Assessment

Retain both records and the R1 alert. The records warrant document-level follow-up, but current evidence is insufficient to conclude that a duplicate payment or fraud occurred. No financial loss is reported.
