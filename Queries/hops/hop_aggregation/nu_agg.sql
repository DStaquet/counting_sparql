CREATE TABLE nu_Agg AS
SELECT COUNT(x) AS x,
       y,
       1 AS k_count
FROM nu_Project_8618330694388824078
GROUP BY y;