# SQL and review-rule results

## Scope

This report describes the prepared Cambridge procurement-card snapshot with SHA256 `b477e61ca2dd3c53359188cb9e7926c76d115e639d3eab0e11a3ae8a755a19a9`. There are 913 source records, all marked generally eligible by the preparation step, including 892 positive entries, 20 negative entries and one zero entry. Rule-specific applicability is narrower.

The analysis is retrospective. Source records, including repeated rows, have not been deleted. No verified fraud labels or approval policies are available.

## SQL summaries

- `03_cost_center_spend.csv` aggregates transaction count, positive amounts, negative amounts and net expenditure by cost center. Missing names are tracked separately from actual names.
- `04_expense_type_spend.csv` provides the same financial measures by expense type, including distinct expense codes.
- `05_supplier_trend.csv` compares each supplier's monthly net amount with its previous observed month. `month_gap` identifies skipped calendar months. Percentage change is not calculated when the previous net amount is absent or nonpositive.

The sum of counts in each summary preserves all 913 eligible records. Net totals reconcile to £74,845.31. The snapshot's latest transaction date is 20 September 2026; the available dates do not establish complete monthly coverage.

## Rule results and sensitivity

| Rule | Configuration                        | Flagged transactions | Flagged groups | Unique flagged transaction value |
| ---- | ------------------------------------ | -------------------: | -------------: | -------------------------------: |
| R1   | With cost center                     |                   92 |             41 |                        £7,283.97 |
| R1   | Without cost center; same population |                   98 |             44 |                        £8,721.97 |
| R2   | At least 3 per day                   |                  252 |             31 |                        £8,563.55 |
| R2   | At least 5 per day                   |                  208 |             18 |                        £5,093.89 |
| R3   | Q3 + 1.5×IQR; minimum 20             |                   57 |              7 |                       £22,027.64 |
| R3   | Q3 + 3×IQR; minimum 20               |                   32 |              6 |                       £16,601.13 |

Amounts within each row count unique transactions for that configuration. Rows across this table overlap and must not be added together. R3 groups are expense-code peer categories, while R1/R2 groups are daily purchasing groups, so group counts represent different units.

### R1: why wider grouping adds alerts

Omitting cost center from the grouping adds six records across three groups:

| Date             | Supplier key      | Amount per record | Different cost centers in the wider group        |
| ---------------- | ----------------- | ----------------: | ------------------------------------------------ |
| 9 April 2026     | TVLICENSING.CO.UK |           £180.00 | Trumpington Pavilion; Clay Farm Community Centre |
| 6 May 2026       | MOJ OSPT ECOM     |            £40.00 | City Homes Expenditure; Temporary Accommodation  |
| 3 September 2026 | AMAZON            |           £499.00 | Grand Arcade Car Park; Cambridge Crematorium     |

All other R1 eligibility filters are unchanged. Each pair shares the other recorded grouping fields, but different cost centers may indicate separate operational needs. Therefore, the additional alerts do not establish better detection. The baseline keeps cost center; the wider version is retained for comparison.

R1 does not have the same definition as exact raw-row duplication in profiling. Its positive-amount restriction and selected comparison fields mean that R1 counts need not equal profiling duplicate counts.

### R2: effect of the daily count threshold

Raising the threshold from 3 to 5 removes 44 flagged transactions and reduces selected daily groups from 31 to 18. This measures a change in review volume. It does not measure a reduction in false positives, because the cases have not been adjudicated.

### R3: applicability and amount thresholds

Of 68 expense codes with eligible positive entries, 9 have at least 20 observations and a nonzero IQR. These applicable categories contain 635 records. The other 59 categories have insufficient observations and receive no R3 flags. No sufficiently large category in this snapshot has IQR=0, but the code explicitly handles that condition.

Raising the IQR multiplier from 1.5 to 3 reduces the number of flagged transactions from 57 to 32. For example, expense code 61703 has 203 positive observations and a baseline upper threshold of £289.515. A threshold can contain fractions of a penny because quantile interpolation is used; the script compares unrounded values. Three of the largest entries flagged in that category are £2,180.00, £2,000.00 and £1,340.00. Further document review is needed to assess their business context.

## Combined baseline review queue

The combined table uses only R1 with cost center, R2 at 3 transactions and R3 at 1.5×IQR:

- **401** transaction–rule pairs in `alert_details.csv`.
- **327** unique flagged source records in `flagged_transactions.csv`.
- **253** records trigger one rule; **74** trigger two; no record triggers all three in this snapshot.
- Unique flagged transaction value: **£32,774.91**.

Adding amounts across the many-rule table would produce £37,875.16 because overlapping transactions appear more than once. The unique queue prevents that double counting. Neither amount is an estimate of fraud or loss.

The review queue is sorted by rule count, then individual transaction amount, descending. The relatively broad initial settings produce a substantial queue; the next analytical step is contextual review and comparison of configurations, rather than treating the queue as confirmed wrongdoing.

## Evidence review and limitations

`cases/CASE_001.md` documents one R1 group checked against the original CSV and page 1 of the source PDF. It identifies matching published details, information not shown in the PDF, alternative explanations and the additional documents required to reach a conclusion.

Unresolved limitations include missing independent payment identifiers, invoices and approval records; lightly standardized supplier aliases; potentially repeated publication records; small peer groups; and incomplete knowledge of monthly coverage. Findings should be described as review candidates and statistical outliers, not confirmed fraud.
