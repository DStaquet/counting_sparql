INSERT INTO nu_prep_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM BGP_1397345390056075867;

INSERT INTO nu_prep_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM delta_BGP_1397345390056075867;

INSERT INTO nu_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       SUM(k_count) AS k_count
FROM nu_prep_BGP_1397345390056075867
GROUP BY label,
         product,
         value1;

DELETE
FROM nu_BGP_1397345390056075867
WHERE k_count <= 0;