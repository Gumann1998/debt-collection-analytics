-- 1. Gesamtüberblick
SELECT
    COUNT(*) AS total_cases,
    ROUND(SUM(claim_amount), 2) AS total_claim_amount,
    ROUND(SUM(recovered_amount), 2) AS total_recovered,
    ROUND(
        SUM(recovered_amount) * 100.0 / SUM(claim_amount),
        2
    ) AS recovery_rate_pct
FROM claims;


-- 2. Kundensegmente
SELECT
    customer_segment,
    COUNT(*) AS total_cases,
    ROUND(AVG(settled) * 100, 2) AS settlement_rate_pct,
    ROUND(
        SUM(recovered_amount) * 100.0 /
        SUM(claim_amount), 2
    ) AS weighted_recovery_rate_pct
FROM claims
GROUP BY customer_segment
ORDER BY weighted_recovery_rate_pct DESC;


-- 3. Forderungsalter
SELECT
    claim_age_bucket,
    COUNT(*) AS total_cases,
    ROUND(AVG(settled) * 100, 2) AS settlement_rate_pct,
    ROUND(
        SUM(recovered_amount) * 100.0 /
        SUM(claim_amount), 2
    ) AS weighted_recovery_rate_pct
FROM claims
GROUP BY claim_age_bucket
ORDER BY
    CASE claim_age_bucket
        WHEN '0-30 Tage' THEN 1
        WHEN '31-90 Tage' THEN 2
        WHEN '91-180 Tage' THEN 3
        WHEN '181-360 Tage' THEN 4
    END;


-- 4. Kontaktkanäle
SELECT
    contact_channel,
    COUNT(*) AS total_cases,
    ROUND(AVG(settled) * 100, 2) AS settlement_rate_pct,
    ROUND(
        SUM(recovered_amount) * 100.0 /
        SUM(claim_amount), 2
    ) AS weighted_recovery_rate_pct
FROM claims
GROUP BY contact_channel
ORDER BY weighted_recovery_rate_pct DESC;