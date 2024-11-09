INSERT INTO Project_8565702497549226448(label, product, k_count)
SELECT label,
       product,
       SUM(k_count) AS k_count
FROM Filter_6053215694347634662
GROUP BY label,
         product;