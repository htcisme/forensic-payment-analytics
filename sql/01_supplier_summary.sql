-- Group by suppiler_key, count all their transaction, and gross pence
SELECT
    supplier_key,
    COUNT(*) AS transaction_count,
    SUM(CASE WHEN gross_pence > 0 THEN gross_pence ELSE 0 END) / 100.0
        AS positive_spend_gbp,
    SUM(CASE WHEN gross_pence < 0 THEN gross_pence ELSE 0 END) / 100.0
        AS negative_entries_gbp,
    SUM(gross_pence) / 100.0 AS net_spend_gbp

FROM transactions
WHERE analysis_eligible = 1
GROUP BY supplier_key
ORDER BY positive_spend_gbp DESC;
