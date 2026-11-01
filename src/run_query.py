from pathlib import Path
import sqlite3
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
query_file = BASE_DIR / sys.argv[1]
report_file = BASE_DIR / "reports" / f"{query_file.stem}.csv"
report_file.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(BASE_DIR / "data/processed/forensic.sqlite") as con:
    result = pd.read_sql_query(query_file.read_text(encoding="utf-8"), con)

result.to_csv(report_file, index=False, encoding="utf-8-sig")
print(result.head(10).to_string(index=False))
print("Saved:", report_file)
