WITH daily AS (
    SELECT transaction_date, supplier_key, cost_center,
        COUNT(*) AS group_size, SUM(gross_pence) AS group_total_pence,
        COUNT(DISTINCT gross_pence) AS distinct_amount_count,
        DENSE_RANK() OVER (
            ORDER BY transaction_date, supplier_key, cost_center
        ) AS group_number
    FROM transactions
    WHERE analysis_eligible = 1 AND gross_pence > 0
      AND TRIM(COALESCE(cost_center, '')) <> ''
    GROUP BY transaction_date, supplier_key, cost_center
    HAVING COUNT(*) >= 3
)
SELECT t.record_id, t.source_file, t.source_sha256, t.source_record_no,
    t.transaction_date, t.supplier_raw, t.supplier_key, t.cost_center,
    t.expense_code, t.expense_type, t.gross_pence,
    t.gross_pence / 100.0 AS gross_gbp,
    d.group_size, d.group_total_pence / 100.0 AS group_total_gbp,
    d.distinct_amount_count,
    t.source_sha256 || ':R2_N3:' || printf('%05d', d.group_number) AS group_id,
    'R2' AS rule_id, 'r2_daily_n3_v1' AS rule_version,
    'At least 3 positive transactions for the same supplier and cost center on one day' AS reason,
    d.group_size AS observed_value, 3 AS threshold_value,
    'transactions_in_group' AS value_unit, '>=' AS comparison_operator
FROM transactions AS t
JOIN daily AS d ON t.transaction_date = d.transaction_date
    AND t.supplier_key = d.supplier_key AND t.cost_center = d.cost_center
WHERE t.analysis_eligible = 1 AND t.gross_pence > 0
ORDER BY d.group_size DESC, t.transaction_date, t.supplier_key, t.record_id;
