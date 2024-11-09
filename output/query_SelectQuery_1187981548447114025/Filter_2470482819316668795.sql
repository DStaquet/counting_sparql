INSERT INTO Filter_2470482819316668795(label, product, value1, k_count)
SELECT label,
       product,
       value1,
       k_count
FROM BGP_4185401599073693870
WHERE CAST(value1 AS INT) > CAST(209 AS INT);