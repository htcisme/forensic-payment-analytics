SELECT
    substr(transaction_date, 1, 7) AS transaction_month,
    COUNT(*) AS transaction_count,
    SUM(gross_pence) / 100.0 AS net_spend_gbp
FROM transactions
WHERE analysis_eligible = 1
GROUP BY substr(transaction_date, 1, 7)
ORDER BY transaction_month;