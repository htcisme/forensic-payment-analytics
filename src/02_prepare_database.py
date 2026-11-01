from pathlib import Path
from decimal import Decimal, InvalidOperation
import hashlib
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
source = BASE_DIR / "data/raw/procurement-card-transactions-2026-27.csv"
output = BASE_DIR / "data/processed"
output.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(source, skiprows=2, dtype="string", encoding="utf-8-sig")
df.columns = df.columns.str.strip()
rename = {
    "Body Name": "body_name", "Date": "date_raw", "Period": "period_raw",
    "Amount": "amount_raw", "Exclusive": "exclusive_raw",
    "Inclusive": "inclusive_raw", "Supplier Name": "supplier_raw",
    "Serivce Area": "service_area", "Subjective Account": "expense_code",
    "Expense Type": "expense_type", "Cost Center Name": "cost_center",
}
if set(df.columns) != set(rename):
    raise ValueError("Schema đã đổi; kiểm tra trước khi chuẩn hóa.")
df = df.rename(columns=rename)

# digest to get unique id
digest = hashlib.sha256(source.read_bytes()).hexdigest()
df.insert(0, "source_record_no", range(1, len(df) + 1))
df.insert(0, "record_id", [f"{digest}:{i}" for i in df["source_record_no"]])
df["source_file"] = source.name
df["source_sha256"] = digest

df["transaction_date"] = pd.to_datetime(
    df["date_raw"], format="%d/%m/%y", errors="coerce"
).dt.strftime("%Y-%m-%d")

df["supplier_key"] = (df["supplier_raw"].str.strip()
                      .str.replace(r"\s+", " ", regex=True).str.upper())
for col in ["service_area", "expense_code", "expense_type", "cost_center"]:
    df[col] = df[col].str.strip()

def to_pence(value):
    if pd.isna(value) or not str(value).strip():
        return pd.NA
    try:
        pounds = Decimal(str(value).replace(",", "").strip())
        pence = pounds * 100
        if not pounds.is_finite() or pence != pence.to_integral_value():
            return pd.NA
        return int(pence)
    except (InvalidOperation, ValueError):
        return pd.NA

df["gross_pence"] = df["inclusive_raw"].map(to_pence).astype("Int64")
df["analysis_eligible"] = (
    df["transaction_date"].notna() & df["gross_pence"].notna()
    & df["supplier_key"].fillna("").ne("")
).astype(int)

# Keep all rows
df.to_csv(output / "transactions_clean.csv", index=False, encoding="utf-8-sig")
#Write to sql
with sqlite3.connect(output / "forensic.sqlite") as con:
    df.to_sql("transactions", con, if_exists="replace", index=False)
print("Saved rows:", len(df))
print("Eligible rows:", int(df["analysis_eligible"].sum()))
