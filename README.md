# Forensic Payment Analytics

A reproducible Python and SQL project for reviewing procurement-card expenditure, identifying transactions that warrant further examination, and documenting evidence-based follow-up checks.

The project combines data profiling, SQLite analysis, three configurable review rules, sensitivity comparisons, and a source-traceable review queue. It uses publicly available Cambridge City Council expenditure data.

> **Interpretation:** A flagged record is a review candidate. The project does not establish duplicate payments, supplier misconduct, fraud, or financial loss.

## Project objectives

The analysis addresses four questions:

1. How is expenditure distributed across suppliers, cost centers, expense types and observed months?
2. Which recorded transactions meet explicit review criteria?
3. How does the review workload change when grouping keys or thresholds change?
4. What can be established from published records, and what additional evidence is required?

## Implementation status

| Component | Status |
|---|---|
| Data profiling and quality notes | Implemented |
| Traceable data preparation and SQLite storage | Implemented |
| Supplier, monthly, cost-center and expense-type SQL summaries | Implemented |
| Supplier trend analysis with window functions | Implemented |
| R1/R2/R3 and alternative configurations | Implemented |
| Combined alerts and unique transaction review queue | Implemented |
| CSV/PDF review example | Documented |
| Automated semantic tests | 8 tests passing |
| Dataset exported for Tableau | Implemented |
| Tableau data export and step-by-step build guide | Implemented |
| Tableau workbook and dashboard screenshots | Pending authoring and validation in Tableau |

## Dataset

**Publisher:** Cambridge City Council  
**Source:** [Procurement card spend](https://www.cambridge.gov.uk/procurement-card-spend)

Download the CSV and corresponding PDF from the publisher's page. The CSV supplies the analytical records; the PDF provides another published representation for selected checks. The PDF is not an invoice or independent confirmation of an underlying payment.

### Reference snapshot

| Item | Value |
|---|---|
| Source CSV at download | `procurement-card-transactions-2026-27.csv` |
| Local input filename used by scripts | `procurement_card_2026_27.csv` |
| Records | 913 |
| Columns | 11 |
| Earliest observed date | 1 April 2026 |
| Latest observed date | 20 September 2026 |

SHA256:

```text
b477e61ca2dd3c53359188cb9e7926c76d115e639d3eab0e11a3ae8a755a19a9
```

The published files can change. Results in this README apply to this snapshot, not necessarily to a later download. Renaming the local file does not change its hash.

### Source fields

| Field | Use |
|---|---|
| `Body Name` | Publishing organization as recorded |
| `Date` | Transaction date |
| `Period` | Source period value, retained without assuming it is a calendar month |
| `Amount` | Original amount field retained for comparison |
| `Exclusive` | Original exclusive amount field |
| `Inclusive` | Gross amount used for expenditure analysis |
| `Supplier Name` | Recorded supplier name |
| `Serivce Area` | Service area; original spelling preserved during ingestion |
| `Subjective Account` | Expense code |
| `Expense Type` | Expense description; the source header has a trailing space |
| `Cost Center Name` | Cost center |

## Tools and methods

- **Python/pandas:** profiling, preparation, peer-group quantiles and report exports.
- **SQLite/SQL:** aggregation, CTEs, joins and window functions, including `LAG`, `COUNT OVER` and `DENSE_RANK`.
- **Decimal and integer pennies:** exact source-amount conversion and monetary totals.
- **unittest:** semantic checks using small, controlled examples.
- **Tableau:** intended visualization layer; transaction-level exports are available.

The pipeline was tested with Python 3.12.14, pandas 2.2.3 and SQLite 3.53.1. SQLite is accessed through Python's built-in `sqlite3` module; no database server is required. A virtual environment is recommended.

## Repository structure

| Path | Purpose |
|---|---|
| `src/01_profile.py` | Data profiling with outputs in `reports/data_quality/` |
| `src/02_prepare_database.py` | Prepare traceable records and write SQLite |
| `src/run_query.py` | Run an individual SQL file and export its results |
| `src/03_build_alerts.py` | Run SQL 03–08, R3, comparisons and combined outputs |
| `src/rule_engine.py` | Validation, R3 calculations, exports and consistency checks |
| `src/04_prepare_tableau.py` | One-row-per-record Tableau CSV, review rank and IQR context |
| `src/run_all.py` | All automated stages, from profiling through Tableau export and tests |
| `sql/` | Summary queries and R1/R2 configurations |
| `tests/test_rules.py` | Automated semantic tests |
| `docs/rules.md` | Rule definitions, applicability, interpretation and limitations |
| `reports/` | Generated outputs and written findings |
| `reports/sensitivity/` | Alternative configurations and comparisons |
| `reports/cases/CASE_001.md` | Baseline R1 source-record review |
| `reports/cases/CASE_002.md` | Wider R1 grouping across different cost centers |
| `reports/cases/CASE_003.md` | R3 equipment-category outlier review |
| `data/raw/` | Downloaded CSV/PDF, kept locally |
| `data/processed/` | Prepared CSV and SQLite database, kept locally |
| `dashboard/data/` | Generated Tableau input and validation totals |
| `dashboard/calculated_fields.md` | Tableau formulas and expected KPI values |
| `docs/tableau_step_by_step.md` | Worksheet-by-worksheet Tableau instructions |
| `docs/finish_project.md` | Analysis, case, README and completion workflow |
| `dashboard/` | Workbook/screenshots to create and validate in Tableau |

## Quick start — Windows PowerShell

Run commands from the repository root. All scripts from the profiling/preparation steps and the SQL/rules extension should be present in the paths listed above.

### 1. Create an environment

```powershell
python3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install pandas
```

No activation is required when using the virtual environment's Python executable directly.

### 2. Download the source files

Create `data/raw/` and save the files as:

- `data/raw/procurement_card_2026_27.csv`
- `data/raw/procurement_card_2026_27.pdf`

Keep the original file contents unchanged. The reference CSV contains two introductory rows before the header. The preparation script is written for that source layout and checks the expected columns.

### 3. Profile the data

```powershell
.\.venv\Scripts\python.exe src/01_profile.py
```

Read the generated profiling summary and missing-value report. This full project writes profiling outputs under `reports/data_quality/`. The rules pipeline reads the prepared database, not the profiling report files.

### 4. Prepare the database

```powershell
.\.venv\Scripts\python.exe src/02_prepare_database.py
```

Expected outputs:

- `data/processed/transactions_clean.csv`
- `data/processed/forensic.sqlite`, containing the `transactions` table.

### 5. Run the first two SQL summaries

```powershell
.\.venv\Scripts\python.exe src/run_query.py sql/01_supplier_summary.sql
.\.venv\Scripts\python.exe src/run_query.py sql/02_monthly_spend.sql
```

### 6. Run the remaining summaries and all review rules

```powershell
.\.venv\Scripts\python.exe src/03_build_alerts.py
```

This runs SQL 03–08, evaluates both R3 settings and creates the combined review outputs. It opens the database in read-only mode.

Optional arguments:

```powershell
.\.venv\Scripts\python.exe src/03_build_alerts.py --db data/processed/forensic.sqlite --output reports/run_01
```

The selected output directory is created if necessary. Files with matching output names are overwritten; use a separate directory to retain results from different runs. Written case reports and analysis notes are snapshot-specific and are not automatically rewritten when the dataset changes.

### 7. Prepare Tableau data

```powershell
.\.venv\Scripts\python.exe src/04_prepare_tableau.py
```

Connect Tableau to `dashboard/data/tableau_transactions.csv`. It preserves one row per source record and adds the review rank, reasons and R3 context. Do not physically join this source to the many-rule alert table.

### 8. Run the tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### One command for all automated stages

After installing pandas and placing the source CSV, the following command runs steps 3–8 in order, stopping if any step fails:

```powershell
.\.venv\Scripts\python.exe src/run_all.py
```

This command does not author Tableau worksheets or update written case conclusions. Complete those tasks using the workflow below.

## Data preparation and traceability

The preparation step:

- Reads source fields as strings and standardizes header whitespace.
- Parses dates into `YYYY-MM-DD`.
- Creates `supplier_key` by trimming, collapsing whitespace and converting to uppercase. Similar-looking aliases are not automatically merged.
- Retains the original amount columns and converts `Inclusive` to integer `gross_pence` using Decimal.
- Adds the source filename, SHA256, source record number and a project-generated `record_id`.
- Marks general analytical eligibility based on a valid date, valid gross amount and a nonblank supplier key.
- Preserves negative entries, zero entries and repeated source rows.

The record identifier combines the snapshot hash with the source record number. It supports traceability but is not a bank-issued transaction reference. Each rule applies its own additional field requirements.

## SQL analysis

| Query | Analytical purpose |
|---|---|
| `01_supplier_summary.sql` | Transaction count and positive, negative and net expenditure by supplier |
| `02_monthly_spend.sql` | Transaction count and net expenditure by observed month |
| `03_cost_center_spend.sql` | Expenditure by cost center, with missing names identified separately |
| `04_expense_type_spend.sql` | Transaction count, expenditure and distinct codes by expense type |
| `05_supplier_trend.sql` | Supplier/month totals and change from the previous observed month |

The trend query does not fill unobserved months with zeros. For example, if a supplier appears in April and June only, June is compared with April and `month_gap` is 2. Percentage changes are left null when the preceding net amount is absent or nonpositive.

## Review rules

Full definitions and output-field explanations are in [docs/rules.md](docs/rules.md).

| Rule | Baseline condition | Alternative configuration |
|---|---|---|
| **R1: Similar recorded payments** | At least two positive entries sharing date, supplier, amount, cost center and expense code | Omit cost center from grouping, retaining the same eligible population |
| **R2: Daily purchasing frequency** | At least three positive entries sharing date, supplier and cost center | Increase the count threshold to five |
| **R3: Large peer-group amount** | Positive amount above Q3 + 1.5×IQR within an expense code; at least 20 positive observations and IQR>0 | Increase the multiplier to 3 |

R3 uses pandas linear quantile interpolation over the complete historical snapshot. Thresholds may contain fractions of a penny and are compared without rounding. Groups with insufficient observations or zero IQR are not flagged by R3; their evaluation status is exported.

These are experimental review parameters. They are not verified approval limits, Cambridge policies or calibrated fraud probabilities.

## Reference results

### Profiling

| Check | Result |
|---|---:|
| Missing or unparseable dates | 0 |
| Missing or unparseable gross amounts | 0 |
| Negative gross amounts | 20 |
| Zero gross amounts | 1 |
| Rows in exact repeated groups | 94 |
| Repeated occurrences after the first | 52 |
| Exact repeated groups | 42 |

The two duplicate-row metrics describe different quantities. A three-row identical group contributes three rows in repeated groups and two repeated occurrences after the first. Raw-row duplication and R1 have different definitions, so their counts need not match.

### Rule sensitivity

| Rule | Configuration | Flagged transactions | Flagged groups |
|---|---|---:|---:|
| R1 | With cost center | 92 | 41 |
| R1 | Without cost center, same population | 98 | 44 |
| R2 | At least 3 per day | 252 | 31 |
| R2 | At least 5 per day | 208 | 18 |
| R3 | 1.5×IQR; minimum 20 | 57 | 7 |
| R3 | 3×IQR; minimum 20 | 32 | 6 |

R1/R2 groups describe daily purchasing groups; R3 groups describe expense-code peer categories. Their group counts are not directly equivalent. Rule-level flag rates also use different applicable populations, which are recorded in the comparison CSV.

Omitting cost center adds six R1 records across three groups. Raising R2's count threshold removes 44 flagged records; increasing R3's multiplier removes 25. These changes measure review workload, not detection accuracy.

### Combined baseline queue

The combined baseline uses R1 **with cost center**, R2 **count >=3** and R3 **multiplier 1.5**.

| Measure | Result |
|---|---:|
| Transaction–rule pairs | 401 |
| Unique flagged records | 327 |
| Records triggering one rule | 253 |
| Records triggering two rules | 74 |
| Records triggering all three | 0 |
| Unique flagged transaction value | £32,774.91 |

`alert_details.csv` contains one row per `(record_id, rule_id)`. A transaction triggering two rules appears twice. Financial totals therefore use the one-row-per-record queue, preventing cross-rule double counting.

The queue is ordered by rule count descending, then individual amount descending, followed by date and record ID. This ordering is a manual review priority, not a probability of fraud.

## Outputs to inspect

| Output | Purpose |
|---|---|
| `reports/rule_summary.csv` | Baseline rule counts and flagged values |
| `reports/sensitivity/rule_comparison.csv` | All six configurations and their denominators |
| `reports/sensitivity/r1_additional_transactions.csv` | Records added by the wider R1 grouping |
| `reports/sensitivity/r1_cross_cost_center_groups.csv` | Wider groups spanning multiple cost centers |
| `reports/r3_thresholds_k1_5.csv` | Category observations, quantiles, thresholds and applicability |
| `reports/r3_evaluation_k1_5.csv` | Record-level R3 evaluation and exclusion status |
| `reports/alert_details.csv` | Transaction–rule pairs with reasons and source references |
| `reports/flagged_transactions.csv` | Unique transaction review queue and ranking |
| `reports/transactions_for_dashboard.csv` | All source rows with individual rule flags and `any_flag` |
| `reports/run_metadata.json` | Source hash, configurations, environment and code hashes |
| [reports/analysis_notes.md](reports/analysis_notes.md) | Written findings and limitations for the reference snapshot |
| [reports/cases/CASE_001.md](reports/cases/CASE_001.md) | Example comparison of CSV records and the published PDF |
| [reports/verification.md](reports/verification.md) | Validation performed on the delivered implementation |

**Do not sum transaction amounts from the many-rule alert table.** Use the unique queue. R2's group total also repeats on each member row and must not be summed without deduplicating groups.

## Evidence review example

Three written case reports are included. CASE_001 examines two same-day transport entries of £140 each. Matching date, supplier, amount and expense code were checked against page 1 of the published PDF. The cost center is present in the CSV but is not displayed on that PDF page.

The review documents alternative explanations and requests for evidence that would distinguish separate legitimate purchases, publication errors and duplicate underlying payments. No external inquiry was made. Agreement between published CSV and PDF records does not independently establish that payments occurred.

CASE_002 examines two £180 TV-licence entries allocated to different cost centers and explains why the wider R1 configuration groups them. CASE_003 examines a £2,180 equipment-category entry above its IQR threshold. Published fields were checked against the CSV and PDF; neither case confirms an irregular payment.

## Build the Tableau dashboards and finish the written work

1. Run `src/run_all.py`, or run `src/04_prepare_tableau.py` after generating the rule reports.
2. Follow [the Tableau build guide](docs/tableau_step_by_step.md), using [the calculated fields](dashboard/calculated_fields.md).
3. Create **01 Spend Overview** and **02 Review Queue** in Tableau.
4. Reconcile unfiltered KPIs to `dashboard/data/tableau_validation.json`: 913 records, £74,845.31 net expenditure, 327 unique flagged records, £32,774.91 flagged value and a 35.82% flag rate.
5. Save the validated workbook locally and export actual dashboard screenshots.
6. Review [the analysis notes](reports/analysis_notes.md) and the three cases; update them if the snapshot or configuration changes.
7. Follow [the completion checklist](docs/finish_project.md), then update the dashboard status and add screenshot links in this README.

**Current delivery:** Code, report outputs, three written source checks, a Tableau-ready CSV and detailed authoring instructions are included. A native Tableau workbook and screenshots have not yet been created or validated. Do not mark them complete until they exist.

Written analysis and cases are snapshot-specific documents. The Python pipeline does not automatically regenerate their narrative findings.

## Validation

The eight semantic tests cover:

1. R1 cross-cost-center grouping and exclusions.
2. R2 frequency thresholds, distinct amounts and group totals.
3. R3 minimum observations, zero IQR and strict threshold comparison.
4. R3 when no categories are applicable.
5. Missing cost-center names versus an actual name matching the display label.
6. `LAG` across an unobserved calendar month.
7. Overlapping rules, empty queues, unique totals and repeatable CSV outputs.
8. Rejection of inputs containing multiple source snapshots.

On the reference snapshot, summary counts and net amounts reconcile to 913 records and £74,845.31. R1/R2 outputs were cross-checked with independent pandas grouping. R3 flags were cross-checked using sorted values and exact rational quantile calculations. These checks validate implementation and traceability, not fraud detection effectiveness.

## Limitations

- There are no verified fraud labels; precision, recall and confirmed losses are not measured.
- Invoices, bank references, cardholder details and approval records are unavailable.
- Negative amounts may reflect refunds or adjustments, but their causes are not established.
- Repeated source rows remain in the analysis and can influence counts and thresholds.
- Supplier aliases remain separate unless supported by a later entity-resolution review.
- Small expense-code groups are excluded from R3 rather than assigned unsupported scores.
- The historical IQR baseline uses the complete snapshot; a real-time application would require past-only thresholds.
- The observed date range does not establish complete monthly coverage.
- The relatively broad starting thresholds produce a substantial review queue and require contextual assessment.

## Source attribution

The source data is published by [Cambridge City Council](https://www.cambridge.gov.uk/procurement-card-spend). This repository is an independent educational portfolio project and is not affiliated with or endorsed by the council or the named suppliers.

Download source data from the publisher rather than treating the repository as the authoritative source. The source CSV/PDF and local SQLite database are not included as repository inputs; record the download details and hash when reproducing the analysis.
