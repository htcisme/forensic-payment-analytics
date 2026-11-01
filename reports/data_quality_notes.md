# Data Profiling Report — Forensic Payment Analytics

**Report date:** 1 November 2026  
**Dataset:** `procurement-card-transactions-2026-27.csv`  
**Basis:** Profiling results supplied by the project author in JSON format.

## 1. Objective and scope

This report reviews the dataset structure, date and amount parsing, negative and zero amounts, and repeated rows before data preparation and expenditure analysis.

The findings are limited to the metrics included in the supplied JSON. Column-level missing-value checks across the entire dataset, supporting-document reconciliation, and fraud verification have not been provided.

## 2. Dataset overview

| Item                       | Result            |
| -------------------------- | ----------------- |
| Number of rows             | 913               |
| Number of columns          | 11                |
| Earliest transaction date  | 1 April 2026      |
| Latest transaction date    | 20 September 2026 |
| Date field checked         | `Date`            |
| Gross amount field checked | `Inclusive`       |

The columns are: `Body Name`, `Date`, `Period`, `Amount`, `Exclusive`, `Inclusive`, `Supplier Name`, `Serivce Area`, `Subjective Account`, `Expense Type`, and `Cost Center Name`.

File SHA256:

```text
b477e61ca2dd3c53359188cb9e7926c76d115e639d3eab0e11a3ae8a755a19a9
```

The hash identifies the dataset version used for reproducibility and comparison. It does not verify the business accuracy of individual transactions.

## 3. Findings

### 3.1. Transaction dates

The value of `invalid_or_missing_dates` is **0**, indicating that the script found no missing or unparseable dates. The observed date range is **1 April–20 September 2026**.

The dates can be used for time-based queries after their format is standardized. Successful parsing does not establish that the source dates match supporting documents. The date range also does not establish that all transactions for each month are included. Comparisons involving September should account for the fact that the latest observed transaction date is 20 September.

### 3.2. Transaction amounts

| Metric for `Inclusive`         | Rows | Percentage of 913 rows |
| ------------------------------ | ---: | ---------------------: |
| Missing or unparseable amounts |    0 |                  0.00% |
| Negative amounts               |   20 |                  2.19% |
| Zero amounts                   |    1 |                  0.11% |

No gross amount parsing issues were identified within the checks performed. However, **21 rows have nonpositive amounts** and should be retained for further business review.

Negative amounts may represent refunds, returns, or adjustments, but the profiling results do not establish their cause. The zero-value entry should also be checked against the source. These records should not be automatically removed, and negative values should not be converted to positive values, as either action would change expenditure figures.

The supplied JSON does not include separate validation results for `Amount` and `Exclusive`, amount totals, distributions, or reconciliation across the three amount columns. No conclusions are drawn on those matters.

### 3.3. Missing values

No missing or unparseable values were reported for the two checked fields: transaction date and gross amount.

**The available results do not establish that all 11 columns are complete.** A column-level count of nulls, empty strings, and whitespace-only values should be added, particularly for `Supplier Name`, `Cost Center Name`, `Expense Type`, and `Subjective Account`.

### 3.4. Repeated rows

| Metric                      |    Result | Interpretation                                              |
| --------------------------- | --------: | ----------------------------------------------------------- |
| `rows_in_repeated_groups`   |   94 rows | All rows in repeated groups, including the first occurrence |
| `repeated_rows_after_first` |   52 rows | Repeated occurrences after the first row in each group      |
| Derived number of groups    | 42 groups | 94 minus 52, using the same set of rows                     |

**10.30% of all rows** belong to repeated groups. Repeated occurrences after the first account for **5.70% of the dataset**. These percentages describe different quantities and should not be used interchangeably.

For example, a group containing three identical rows contributes one group, three rows in repeated groups, and two repeated occurrences after the first.

These records warrant review but do not establish duplicate payments or fraud. Possible explanations include legitimate purchases with identical recorded details, publication errors, or payment issues requiring investigation. Invoice numbers, payment references, or supporting documents are needed to distinguish between these explanations.

## 4. Recommended actions

| Priority | Action                                                                               | Purpose                                                                             |
| -------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| 1        | Preserve the original file and SHA256; add source record numbers to the working copy | Maintain traceability to the source                                                 |
| 2        | Export the 94 rows in 42 repeated groups with group identifiers                      | Review each group before deciding how to treat it                                   |
| 3        | Export the 20 negative entries and one zero-value entry separately                   | Establish their business meaning and treatment in expenditure totals                |
| 4        | Check missing values in every column                                                 | Complete the data quality assessment                                                |
| 5        | Validate `Amount`, `Exclusive`, and `Inclusive` separately                           | Select the appropriate analytical field while preserving reconciliation information |
| 6        | Standardize dates and text in a working copy while preserving the source             | Prepare the data for SQL and further analysis                                       |

## 5. Conclusion

The supplied profiling results show no missing or unparseable values in the transaction date and gross amount fields. Items requiring further review include **20 negative amounts, one zero-value amount, and 42 groups of repeated rows**.

Data preparation and SQL loading can proceed while preserving the flagged records and completing missing-value checks across all columns. The current findings describe data quality and dataset characteristics; they do not confirm incorrect payments, fraud, or financial losses.
