INSERT INTO Project_8990059759388970832(s, x, k_count)
SELECT s,
       x,
       SUM(k_count) AS k_count
FROM BGP_5631193804359433266
GROUP BY s,
         x;