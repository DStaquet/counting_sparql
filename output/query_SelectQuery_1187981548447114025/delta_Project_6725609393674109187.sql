INSERT INTO delta_Project_6725609393674109187(label, product, k_count)
SELECT label,
       product,
       SUM(k_count) AS k_count
FROM delta_Filter_2470482819316668795
GROUP BY label,
         product;