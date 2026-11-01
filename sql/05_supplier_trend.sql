-- LAG so với THÁNG QUAN SÁT TRƯỚC của cùng supplier.
-- Không điền tháng vắng thành 0; month_gap làm rõ khoảng cách thời gian.
WITH monthly AS (
    SELECT supplier_key,
        substr(transaction_date, 1, 7) AS transaction_month,
        COUNT(*) AS transaction_count,
        SUM(gross_pence) AS net_pence,
        SUM(CASE WHEN gross_pence > 0 THEN gross_pence ELSE 0 END) AS positive_pence,
        SUM(CASE WHEN gross_pence < 0 THEN gross_pence ELSE 0 END) AS negative_pence
    FROM transactions
    WHERE analysis_eligible = 1
    GROUP BY supplier_key, substr(transaction_date, 1, 7)
), previous AS (
    SELECT *,
        LAG(transaction_month) OVER (
            PARTITION BY supplier_key ORDER BY transaction_month
        ) AS previous_observed_month,
        LAG(net_pence) OVER (
            PARTITION BY supplier_key ORDER BY transaction_month
        ) AS previous_net_pence
    FROM monthly
), gaps AS (
    SELECT *,
        (CAST(substr(transaction_month, 1, 4) AS INTEGER) * 12
         + CAST(substr(transaction_month, 6, 2) AS INTEGER))
        - (CAST(substr(previous_observed_month, 1, 4) AS INTEGER) * 12
           + CAST(substr(previous_observed_month, 6, 2) AS INTEGER)) AS month_gap
    FROM previous
)
SELECT supplier_key, transaction_month, transaction_count,
    positive_pence / 100.0 AS positive_spend_gbp,
    negative_pence / 100.0 AS negative_entries_gbp,
    net_pence / 100.0 AS net_spend_gbp,
    previous_observed_month, month_gap,
    CASE WHEN month_gap = 1 THEN 1 ELSE 0 END AS consecutive_month,
    previous_net_pence / 100.0 AS previous_net_spend_gbp,
    (net_pence - previous_net_pence) / 100.0 AS change_vs_previous_observed_gbp,
    CASE WHEN previous_net_pence > 0
         THEN ROUND((net_pence - previous_net_pence) * 100.0 / previous_net_pence, 2)
         ELSE NULL END AS change_vs_previous_observed_pct
FROM gaps
ORDER BY supplier_key, transaction_month;
