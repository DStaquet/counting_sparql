INSERT INTO nu_prep_Filter_6053215694347634662 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM Filter_6053215694347634662;

INSERT INTO nu_prep_Filter_6053215694347634662 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM delta_Filter_6053215694347634662;

INSERT INTO nu_Filter_6053215694347634662 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       SUM(k_count) AS k_count
FROM nu_prep_Filter_6053215694347634662
GROUP BY label,
         product,
         value1;

DELETE
FROM nu_Filter_6053215694347634662
WHERE k_count <= 0;