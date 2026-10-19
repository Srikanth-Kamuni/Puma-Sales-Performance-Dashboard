-- Use a temporary table so source tables remain intact.
CREATE TEMP TABLE practice_targets AS SELECT * FROM monthly_targets;
BEGIN TRANSACTION;
UPDATE practice_targets SET TargetNetSalesEUR=ROUND(TargetNetSalesEUR*1.05,2)
WHERE MonthStart='2024-01-01' AND Region='EMEA';
SELECT * FROM practice_targets WHERE MonthStart='2024-01-01';
ROLLBACK;
SELECT * FROM practice_targets WHERE MonthStart='2024-01-01';
DROP TABLE practice_targets;
