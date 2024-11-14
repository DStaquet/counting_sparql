CREATE TEMP TABLE nu_prep_BGP_4313253051102226119 (x, y, k_count INT) AS
SELECT x,
       y,
       k_count
FROM BGP_4313253051102226119;

INSERT INTO nu_prep_BGP_4313253051102226119 (x, y, k_count)
SELECT x,
       y,
       k_count
FROM delta_BGP_4313253051102226119;

CREATE TABLE nu_BGP_4313253051102226119 (x, y, k_count INT) AS
SELECT x,
       y,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_4313253051102226119
GROUP BY x,
         y
HAVING SUM(k_count) > 0;