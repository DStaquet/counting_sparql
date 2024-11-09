CREATE TABLE delta_BGP_4313253051102226119 AS
SELECT x,
       y,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_4313253051102226119
GROUP BY x,
         y;