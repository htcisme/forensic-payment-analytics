-- Giữ nhóm thiếu tên riêng; không gộp nhầm với một tên thật.
WITH labelled AS (
    SELECT *,
        CASE WHEN TRIM(COALESCE(cost_center, '')) = '' THEN 1 ELSE 0 END
            AS cost_center_missing,
        NULLIF(TRIM(cost_center), '') AS cost_center_key
    FROM transactions
    WHERE analysis_eligible = 1
)
SELECT
    cost_center_missing,
    CASE WHEN cost_center_missing = 1 THEN '[MISSING COST CENTER]'
         ELSE cost_center_key END AS cost_center,
    COUNT(*) AS transaction_count,
    SUM(CASE WHEN gross_pence > 0 THEN gross_pence ELSE 0 END) / 100.0
        AS positive_spend_gbp,
    SUM(CASE WHEN gross_pence < 0 THEN gross_pence ELSE 0 END) / 100.0
        AS negative_entries_gbp,
    SUM(gross_pence) / 100.0 AS net_spend_gbp
FROM labelled
GROUP BY cost_center_missing, cost_center_key
ORDER BY positive_spend_gbp DESC, cost_center_missing, cost_center_key;
