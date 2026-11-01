"""Run retrospective procurement review rules against a read-only SQLite DB."""
from pathlib import Path
import hashlib
import json
import platform
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SQL_FILES = [
    "03_cost_center_spend.sql", "04_expense_type_spend.sql", "05_supplier_trend.sql",
    "06_r1_similar_payments.sql", "06b_r1_without_cost_center.sql",
    "07_r2_daily_frequency_3.sql", "08_r2_daily_frequency_5.sql",
]
EVIDENCE = ["record_id", "source_file", "source_sha256", "source_record_no",
            "transaction_date", "supplier_raw", "supplier_key", "cost_center",
            "expense_code", "expense_type", "gross_pence"]
ALERT_COLUMNS = EVIDENCE + ["gross_gbp", "rule_id", "rule_version", "group_id",
    "reason", "observed_value", "threshold_value", "value_unit",
    "comparison_operator", "group_size"]


def present(series):
    return series.fillna("").astype(str).str.strip().ne("")


def load_transactions(db_path):
    db_path = Path(db_path).resolve()
    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}. Run 02_prepare_database.py first.")
    # A missing path must never create an empty DB by accident.
    with sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True) as con:
        tx = pd.read_sql_query("SELECT * FROM transactions", con)
    required = set(EVIDENCE + ["analysis_eligible"])
    if not required.issubset(tx.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(tx.columns))}")
    if tx.empty or not tx["record_id"].is_unique or not present(tx["record_id"]).all():
        raise ValueError("Expected nonempty data with unique, nonblank record_id values.")
    if not present(tx["source_sha256"]).all() or tx["source_sha256"].nunique() != 1:
        raise ValueError("Use exactly one source snapshot per run; do not concatenate snapshots.")
    if not tx["analysis_eligible"].isin([0, 1]).all():
        raise ValueError("analysis_eligible must contain 0 or 1.")
    money = pd.to_numeric(tx["gross_pence"], errors="coerce")
    good = tx["analysis_eligible"].eq(1)
    if (money[good].isna().any() or (money[good] % 1 != 0).any()
            or not present(tx.loc[good, "supplier_key"]).all()):
        raise ValueError("Eligible rows require integer gross_pence and a supplier key.")
    text_dates = tx.loc[good, "transaction_date"].astype(str)
    date_ok = text_dates.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    dates = pd.to_datetime(text_dates, format="%Y-%m-%d", errors="coerce")
    if not date_ok.all() or dates.isna().any():
        raise ValueError("Eligible rows require ISO dates, YYYY-MM-DD.")
    tx["gross_pence"] = money.astype("Int64")
    return tx


def execute_sql_reports(db_path, sql_dir, output):
    results = {}
    with sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True) as con:
        for name in SQL_FILES:
            query = (Path(sql_dir) / name).read_text(encoding="utf-8")
            table = pd.read_sql_query(query, con)
            table.to_csv(output / f"{Path(name).stem}.csv", index=False, encoding="utf-8-sig")
            results[Path(name).stem] = table
    return results


def evaluate_r3(tx, k=1.5, minimum=20):
    """Return alerts, all category thresholds and a row-level applicability audit."""
    positive = tx["analysis_eligible"].eq(1) & tx["gross_pence"].gt(0).fillna(False)
    eligible = positive & present(tx["expense_code"])
    subset = tx.loc[eligible]
    stats = subset.groupby("expense_code", sort=True)["gross_pence"].agg(
        n_positive="count", q1_pence=lambda s: s.quantile(.25, interpolation="linear"),
        q3_pence=lambda s: s.quantile(.75, interpolation="linear")
    ).reset_index()
    stats["iqr_pence"] = stats["q3_pence"] - stats["q1_pence"]
    stats["threshold_pence"] = stats["q3_pence"] + k * stats["iqr_pence"]
    stats["evaluation_status"] = "applied"
    stats.loc[stats["iqr_pence"].eq(0), "evaluation_status"] = "zero_iqr"
    stats.loc[stats["n_positive"].lt(minimum), "evaluation_status"] = "insufficient_observations"
    stats["iqr_multiplier"] = k
    stats["minimum_observations"] = minimum
    stats["quantile_method"] = "pandas_linear"
    stats["scope"] = "retrospective_full_snapshot"
    for name in ["q1", "q3", "iqr", "threshold"]:
        stats[f"{name}_gbp"] = stats[f"{name}_pence"] / 100.0

    audit = tx[EVIDENCE + ["analysis_eligible"]].merge(
        stats, on="expense_code", how="left", validate="many_to_one")
    audit["r3_status"] = audit["evaluation_status"].fillna("not_evaluated")
    audit.loc[~present(audit["expense_code"]), "r3_status"] = "missing_expense_code"
    audit.loc[audit["gross_pence"].le(0).fillna(False), "r3_status"] = "nonpositive_amount"
    audit.loc[audit["analysis_eligible"].ne(1), "r3_status"] = "ineligible_record"
    audit["flagged"] = (audit["r3_status"].eq("applied")
        & audit["gross_pence"].gt(audit["threshold_pence"]).fillna(False)).astype(int)
    flagged = audit.loc[audit["flagged"].eq(1)].copy()
    if flagged.empty:
        return pd.DataFrame(columns=ALERT_COLUMNS), stats, audit
    token = str(k).replace(".", "_")
    version = f"r3_iqr_k{token}_min{minimum}_v1"
    flagged["gross_gbp"] = flagged["gross_pence"] / 100.0
    flagged["rule_id"] = "R3"
    flagged["rule_version"] = version
    flagged["group_id"] = flagged.apply(lambda r: str(r["source_sha256"]) + ":R3:" +
        hashlib.sha256(str(r["expense_code"]).encode()).hexdigest()[:20], axis=1)
    flagged["reason"] = flagged.apply(lambda r:
        f"Amount exceeds Q3 + {k:g} * IQR for expense code {r['expense_code']}; n={int(r['n_positive'])}", axis=1)
    flagged["observed_value"] = flagged["gross_pence"] / 100.0
    flagged["threshold_value"] = flagged["threshold_pence"] / 100.0
    flagged["value_unit"] = "GBP"
    flagged["comparison_operator"] = ">"
    flagged["group_size"] = flagged["n_positive"].astype(int)
    return flagged.reindex(columns=ALERT_COLUMNS), stats, audit


def comparison_row(rule, configuration, alerts, denominator, denominator_description):
    unique = alerts.drop_duplicates("record_id")
    return {
        "rule_id": rule, "configuration": configuration,
        "eligible_transactions": int(denominator),
        "denominator_description": denominator_description,
        "flagged_transactions": len(unique),
        "flagged_groups": int(alerts["group_id"].nunique()),
        "flagged_pct_of_eligible": round(len(unique) * 100 / denominator, 2) if denominator else None,
        "flagged_value_pence": int(unique["gross_pence"].sum()),
        "flagged_value_gbp": int(unique["gross_pence"].sum()) / 100.0,
    }


def run_pipeline(db_path, output_dir, sql_dir=None):
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    sensitivity = output / "sensitivity"
    sensitivity.mkdir(exist_ok=True)
    sql_dir = Path(sql_dir) if sql_dir else ROOT / "sql"
    tx = load_transactions(db_path)
    tables = execute_sql_reports(db_path, sql_dir, output)
    r1 = tables["06_r1_similar_payments"]
    r1_wide = tables["06b_r1_without_cost_center"]
    r2 = tables["07_r2_daily_frequency_3"]
    r2_n5 = tables["08_r2_daily_frequency_5"]
    r3, thresholds, audit = evaluate_r3(tx, 1.5, 20)
    r3_k3, thresholds_k3, audit_k3 = evaluate_r3(tx, 3.0, 20)
    for name, table in {
        "r3_alerts_k1_5.csv": r3, "r3_thresholds_k1_5.csv": thresholds,
        "r3_evaluation_k1_5.csv": audit,
    }.items():
        table.to_csv(output / name, index=False, encoding="utf-8-sig")
    for name, table in {
        "r3_alerts_k3.csv": r3_k3, "r3_thresholds_k3.csv": thresholds_k3,
        "r3_evaluation_k3.csv": audit_k3,
    }.items():
        table.to_csv(sensitivity / name, index=False, encoding="utf-8-sig")

    # Only the baseline of each rule enters the combined alert table.
    # Sensitivity runs remain separate, preserving one (record_id, rule_id) pair.
    frames = [r1.reindex(columns=ALERT_COLUMNS), r2.reindex(columns=ALERT_COLUMNS), r3]
    nonempty = [frame for frame in frames if not frame.empty]
    details = (pd.concat(nonempty, ignore_index=True) if nonempty
               else pd.DataFrame(columns=ALERT_COLUMNS))
    if details.duplicated(["record_id", "rule_id"]).any():
        raise AssertionError("A transaction/rule pair appears more than once.")
    details = details.sort_values(["record_id", "rule_id"])
    details.to_csv(output / "alert_details.csv", index=False, encoding="utf-8-sig")

    dashboard = tx.copy()
    dashboard["gross_gbp"] = dashboard["gross_pence"] / 100.0
    for rule in ["R1", "R2", "R3"]:
        ids = set(details.loc[details["rule_id"].eq(rule), "record_id"])
        dashboard[f"flagged_{rule.lower()}"] = dashboard["record_id"].isin(ids).astype(int)
    flags = ["flagged_r1", "flagged_r2", "flagged_r3"]
    dashboard["rule_count"] = dashboard[flags].sum(axis=1)
    dashboard["any_flag"] = dashboard["rule_count"].gt(0).astype(int)
    rules_by_id = details.groupby("record_id")["rule_id"].agg(lambda s: ",".join(sorted(s)))
    dashboard["triggered_rules"] = dashboard["record_id"].map(rules_by_id).fillna("")
    dashboard.to_csv(output / "transactions_for_dashboard.csv", index=False, encoding="utf-8-sig")
    queue = dashboard.loc[dashboard["any_flag"].eq(1)].sort_values(
        ["rule_count", "gross_pence", "transaction_date", "record_id"],
        ascending=[False, False, True, True]).reset_index(drop=True)
    queue.insert(0, "review_rank", range(1, len(queue) + 1))
    queue.to_csv(output / "flagged_transactions.csv", index=False, encoding="utf-8-sig")

    positive = tx["analysis_eligible"].eq(1) & tx["gross_pence"].gt(0).fillna(False)
    r1_population = positive & present(tx["cost_center"]) & present(tx["expense_code"])
    r2_population = positive & present(tx["cost_center"])
    comparisons = pd.DataFrame([
        comparison_row("R1", "with_cost_center", r1, r1_population.sum(),
                       "positive eligible rows with cost center and expense code"),
        comparison_row("R1", "without_cost_center_same_population", r1_wide,
                       r1_population.sum(), "same population as baseline R1"),
        comparison_row("R2", "minimum_3", r2, r2_population.sum(),
                       "positive eligible rows with cost center"),
        comparison_row("R2", "minimum_5", r2_n5, r2_population.sum(),
                       "same population as baseline R2"),
        comparison_row("R3", "iqr_1.5_min20", r3, audit["r3_status"].eq("applied").sum(),
                       "positive eligible rows in categories with n>=20 and IQR>0"),
        comparison_row("R3", "iqr_3_min20", r3_k3, audit_k3["r3_status"].eq("applied").sum(),
                       "same population as baseline R3"),
    ])
    comparisons.to_csv(sensitivity / "rule_comparison.csv", index=False, encoding="utf-8-sig")
    comparisons.loc[comparisons["configuration"].isin(
        ["with_cost_center", "minimum_3", "iqr_1.5_min20"])].to_csv(
            output / "rule_summary.csv", index=False, encoding="utf-8-sig")
    added = r1_wide.loc[~r1_wide["record_id"].isin(r1["record_id"])].copy()
    added.to_csv(sensitivity / "r1_additional_transactions.csv", index=False, encoding="utf-8-sig")
    cost_counts = r1_wide.groupby("group_id")["cost_center"].nunique()
    crossed = r1_wide.loc[r1_wide["group_id"].isin(cost_counts[cost_counts > 1].index)]
    crossed.to_csv(sensitivity / "r1_cross_cost_center_groups.csv", index=False, encoding="utf-8-sig")

    # Financial totals use the unique transaction queue, never the many-rule table.
    assert len(dashboard) == len(tx)
    assert queue["record_id"].is_unique
    assert set(details["record_id"]) == set(queue["record_id"])
    assert len(details) == int(queue["rule_count"].sum())
    assert set(r1["record_id"]).issubset(set(r1_wide["record_id"]))
    assert set(r2_n5["record_id"]).issubset(set(r2["record_id"]))
    assert set(r3_k3["record_id"]).issubset(set(r3["record_id"]))
    eligible_count = int(tx["analysis_eligible"].eq(1).sum())
    metadata = {
        "pipeline_version": "p1_rules_v1",
        "snapshot_sha256": tx["source_sha256"].iloc[0],
        "source_files": sorted(tx["source_file"].unique().tolist()),
        "source_rows": len(tx), "analysis_eligible_rows": eligible_count,
        "combined_alert_rows": len(details), "unique_flagged_transactions": len(queue),
        "flagged_value_pence_unique": int(queue["gross_pence"].sum()),
        "flagged_value_gbp_unique": int(queue["gross_pence"].sum()) / 100.0,
        "all_rows_net_value_pence": int(tx["gross_pence"].sum()),
        "baseline": {"R1": "with_cost_center", "R2": "minimum_3", "R3": "iqr_1.5_min20"},
        "analysis_scope": "retrospective_full_snapshot",
        "priority": "rule_count descending, gross_pence descending, date and record_id ascending",
        "python_version": platform.python_version(), "pandas_version": pd.__version__,
        "sqlite_version": sqlite3.sqlite_version,
        "sql_sha256": {name: hashlib.sha256((sql_dir / name).read_bytes()).hexdigest()
                       for name in SQL_FILES},
        "engine_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": {"source_rows_preserved": True, "unique_record_rule_pairs": True,
                   "unique_transaction_queue": True, "sensitivity_subset_checks": True},
    }
    (output / "run_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata
