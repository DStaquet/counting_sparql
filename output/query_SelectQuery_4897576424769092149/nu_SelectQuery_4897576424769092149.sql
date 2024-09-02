INSERT INTO nu_prep_SelectQuery_4897576424769092149 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM SelectQuery_4897576424769092149;

INSERT INTO nu_prep_SelectQuery_4897576424769092149 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM delta_SelectQuery_4897576424769092149;

INSERT INTO nu_SelectQuery_4897576424769092149 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       SUM(k_count) AS k_count
FROM nu_prep_SelectQuery_4897576424769092149
GROUP BY label,
         product,
         value1;

DELETE
FROM nu_SelectQuery_4897576424769092149
WHERE k_count <= 0;