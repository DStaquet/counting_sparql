CREATE TABLE delta_Union_2519498395300192749_schema_388442962187960249 AS
SELECT (CASE
            WHEN r1.x IS NOT NULL THEN r1.x
            ELSE r2.x
        END) AS x,
       (CASE
            WHEN r1.z IS NOT NULL THEN r1.z
            ELSE r2.z
        END) AS z,
       coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) AS k_count
FROM delta_Union_8520143739185799797_schema_388442962187960249 AS r1
FULL OUTER JOIN delta_BGP_2727124371284701244 AS r2 ON r1.x = r2.x
AND r1.z = r2.z;


CREATE TABLE delta_Union_2519498395300192749_schema_3615708767843743351 AS
SELECT w,
       y,
       k_count
FROM delta_Union_8520143739185799797_schema_3615708767843743351;