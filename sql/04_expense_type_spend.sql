-- Phân tích theo tên loại chi; mã chi có thể khác nhau trong cùng một tên.
WITH labelled AS (
    SELECT *,
        CASE WHEN TRIM(COALESCE(expense_type, '')) = '' THEN 1 ELSE 0 END
            AS expense_type_missing,
        NULLIF(TRIM(expense_type), '') AS expense_type_key
    FROM transactions
    WHERE analysis_eligible = 1
)
SELECT
    expense_type_missing,
    CASE WHEN expense_type_missing = 1 THEN '[MISSING EXPENSE TYPE]'
         ELSE expense_type_key END AS expense_type,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT expense_code) AS distinct_expense_codes,
    SUM(CASE WHEN gross_pence > 0 THEN gross_pence ELSE 0 END) / 100.0
        AS positive_spend_gbp,
    SUM(CASE WHEN gross_pence < 0 THEN gross_pence ELSE 0 END) / 100.0
        AS negative_entries_gbp,
    SUM(gross_pence) / 100.0 AS net_spend_gbp
FROM labelled
GROUP BY expense_type_missing, expense_type_key
ORDER BY positive_spend_gbp DESC, expense_type_missing, expense_type_key;
