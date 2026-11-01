from pathlib import Path
import hashlib
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
source = BASE_DIR / "data/raw/procurement-card-transactions-2026-27.csv"
reports = BASE_DIR / "reports"
reports.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source, skiprows=2, dtype="string", encoding="utf-8-sig")
df.columns = df.columns.str.strip()

required = {"Date", "Inclusive", "Supplier Name", "Serivce Area",
            "Subjective Account", "Expense Type", "Cost Center Name"}
if not required.issubset(df.columns):
    raise ValueError(f"Schema changed: {df.columns.tolist()}")

dates = pd.to_datetime(df["Date"], format="%d/%m/%y", errors="coerce")
gross = pd.to_numeric(df["Inclusive"].str.replace(",", "", regex=False), errors="coerce")
blank_or_missing = df.apply(lambda s: s.isna() | s.str.strip().eq(""))

summary = {
    "source_file": source.name,
    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "rows": len(df),
    "columns": df.columns.tolist(),
    "date_min": str(dates.min().date()) if dates.notna().any() else None,
    "date_max": str(dates.max().date()) if dates.notna().any() else None,
    "invalid_or_missing_dates": int(dates.isna().sum()),
    "invalid_or_missing_gross": int(gross.isna().sum()),
    "negative_gross_rows": int(gross.lt(0).sum()),
    "zero_gross_rows": int(gross.eq(0).sum()),
    "repeated_rows_after_first": int(df.duplicated().sum()),
    "rows_in_repeated_groups": int(df.duplicated(keep=False).sum()),
}

(reports / "profile_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)
blank_or_missing.sum().rename("blank_or_missing_count").to_csv(
    reports / "missing_values.csv", encoding="utf-8-sig"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
print(df.head().to_string(index=False))
