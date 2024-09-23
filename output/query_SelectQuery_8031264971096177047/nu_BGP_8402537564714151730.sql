INSERT INTO nu_prep_BGP_8402537564714151730 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM BGP_8402537564714151730;

INSERT INTO nu_prep_BGP_8402537564714151730 (x, y, z, k_count)
SELECT x,
       y,
       z,
       k_count
FROM delta_BGP_8402537564714151730;

INSERT INTO nu_BGP_8402537564714151730 (x, y, z, k_count)
SELECT x,
       y,
       z,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_8402537564714151730
GROUP BY x,
         y,
         z;

DELETE
FROM nu_BGP_8402537564714151730
WHERE k_count <= 0;