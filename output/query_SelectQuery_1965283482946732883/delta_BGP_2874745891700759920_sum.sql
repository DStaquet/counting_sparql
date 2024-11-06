CREATE TABLE delta_BGP_2874745891700759920 AS
SELECT t1,
       t2,
       t3,
       t4,
       t5,
       x,
       y,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_2874745891700759920
GROUP BY t1,
         t2,
         t3,
         t4,
         t5,
         x,
         y;