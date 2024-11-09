INSERT INTO nu_prep_Project_8565702497549226448 (label, product, k_count)
SELECT label,
       product,
       k_count
FROM Project_8565702497549226448;

INSERT INTO nu_prep_Project_8565702497549226448 (label, product, k_count)
SELECT label,
       product,
       k_count
FROM delta_Project_8565702497549226448;

INSERT INTO nu_Project_8565702497549226448 (label, product, k_count)
SELECT label,
       product,
       SUM(k_count) AS k_count
FROM nu_prep_Project_8565702497549226448
GROUP BY label,
         product;

DELETE
FROM nu_Project_8565702497549226448
WHERE k_count <= 0;