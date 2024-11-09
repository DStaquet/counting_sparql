INSERT INTO Project_6725609393674109187(label, product, k_count)
SELECT label,
       product,
       SUM(k_count) AS k_count
FROM Filter_2470482819316668795
GROUP BY label,
         product;