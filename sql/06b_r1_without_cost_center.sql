-- Giữ bộ lọc giống R1 gốc, chỉ bỏ cost_center khỏi nhóm so sánh.
WITH candidates AS (
    SELECT *,
        COUNT(*) OVER (
            PARTITION BY transaction_date, supplier_key, gross_pence, expense_code
        ) AS group_size,
        DENSE_RANK() OVER (
            ORDER BY transaction_date, supplier_key, gross_pence, expense_code
        ) AS group_number
    FROM transactions
    WHERE analysis_eligible = 1 AND gross_pence > 0
      AND TRIM(COALESCE(cost_center, '')) <> ''
      AND TRIM(COALESCE(expense_code, '')) <> ''
)
SELECT record_id, source_file, source_sha256, source_record_no,
    transaction_date, supplier_raw, supplier_key, cost_center, expense_code,
    expense_type, gross_pence, gross_pence / 100.0 AS gross_gbp,
    group_size,
    source_sha256 || ':R1_WIDE:' || printf('%05d', group_number) AS group_id,
    'R1' AS rule_id, 'r1_without_cost_center_v1' AS rule_version,
    'Same day, supplier, positive amount and expense code; cost center omitted' AS reason,
    group_size AS observed_value, 2 AS threshold_value,
    'transactions_in_group' AS value_unit, '>=' AS comparison_operator
FROM candidates
WHERE group_size >= 2
ORDER BY group_size DESC, transaction_date, supplier_key, record_id;
