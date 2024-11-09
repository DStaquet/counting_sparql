INSERT INTO delta_BGP_2874745891700759920_2 (t1, t3, x, t4, t2, t5, y, k_count)
SELECT (CASE
            WHEN R1.t1 NOT NULL THEN R1.t1
            ELSE R2.t1
        END) AS t1,
       (CASE
            WHEN R1.t3 NOT NULL THEN R1.t3
            ELSE R2.t3
        END) AS t3,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.t4 NOT NULL THEN R1.t4
            ELSE R2.t4
        END) AS t4,
       (CASE
            WHEN R1.t2 NOT NULL THEN R1.t2
            ELSE R2.t2
        END) AS t2,
       (CASE
            WHEN R1.t5 NOT NULL THEN R1.t5
            ELSE R2.t5
        END) AS t5,
       (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_2874745891700759920_1 AS R1
FULL OUTER JOIN delta_BGP_2874745891700759920_2 AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;

INSERT INTO delta_BGP_2874745891700759920_3 (t1, t3, x, t4, t2, t5, y, k_count)
SELECT (CASE
            WHEN R1.t1 NOT NULL THEN R1.t1
            ELSE R2.t1
        END) AS t1,
       (CASE
            WHEN R1.t3 NOT NULL THEN R1.t3
            ELSE R2.t3
        END) AS t3,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.t4 NOT NULL THEN R1.t4
            ELSE R2.t4
        END) AS t4,
       (CASE
            WHEN R1.t2 NOT NULL THEN R1.t2
            ELSE R2.t2
        END) AS t2,
       (CASE
            WHEN R1.t5 NOT NULL THEN R1.t5
            ELSE R2.t5
        END) AS t5,
       (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_2874745891700759920_2 AS R1
FULL OUTER JOIN delta_BGP_2874745891700759920_3 AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;

INSERT INTO delta_BGP_2874745891700759920_4 (t1, t3, x, t4, t2, t5, y, k_count)
SELECT (CASE
            WHEN R1.t1 NOT NULL THEN R1.t1
            ELSE R2.t1
        END) AS t1,
       (CASE
            WHEN R1.t3 NOT NULL THEN R1.t3
            ELSE R2.t3
        END) AS t3,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.t4 NOT NULL THEN R1.t4
            ELSE R2.t4
        END) AS t4,
       (CASE
            WHEN R1.t2 NOT NULL THEN R1.t2
            ELSE R2.t2
        END) AS t2,
       (CASE
            WHEN R1.t5 NOT NULL THEN R1.t5
            ELSE R2.t5
        END) AS t5,
       (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_2874745891700759920_3 AS R1
FULL OUTER JOIN delta_BGP_2874745891700759920_4 AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;

INSERT INTO delta_BGP_2874745891700759920_5 (t1, t3, x, t4, t2, t5, y, k_count)
SELECT (CASE
            WHEN R1.t1 NOT NULL THEN R1.t1
            ELSE R2.t1
        END) AS t1,
       (CASE
            WHEN R1.t3 NOT NULL THEN R1.t3
            ELSE R2.t3
        END) AS t3,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.t4 NOT NULL THEN R1.t4
            ELSE R2.t4
        END) AS t4,
       (CASE
            WHEN R1.t2 NOT NULL THEN R1.t2
            ELSE R2.t2
        END) AS t2,
       (CASE
            WHEN R1.t5 NOT NULL THEN R1.t5
            ELSE R2.t5
        END) AS t5,
       (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_2874745891700759920_4 AS R1
FULL OUTER JOIN delta_BGP_2874745891700759920_5 AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;

CREATE TABLE delta_BGP_2874745891700759920 AS
SELECT (CASE
            WHEN R1.t1 NOT NULL THEN R1.t1
            ELSE R2.t1
        END) AS t1,
       (CASE
            WHEN R1.t3 NOT NULL THEN R1.t3
            ELSE R2.t3
        END) AS t3,
       (CASE
            WHEN R1.x NOT NULL THEN R1.x
            ELSE R2.x
        END) AS x,
       (CASE
            WHEN R1.t4 NOT NULL THEN R1.t4
            ELSE R2.t4
        END) AS t4,
       (CASE
            WHEN R1.t2 NOT NULL THEN R1.t2
            ELSE R2.t2
        END) AS t2,
       (CASE
            WHEN R1.t5 NOT NULL THEN R1.t5
            ELSE R2.t5
        END) AS t5,
       (CASE
            WHEN R1.y NOT NULL THEN R1.y
            ELSE R2.y
        END) AS y,
       (CASE
            WHEN R1.k_count IS NULL THEN R2.k_count
            WHEN R2.k_count IS NULL THEN R1.k_count
            ELSE R1.k_count + R2.k_count
        END) AS k_count
FROM delta_BGP_2874745891700759920_5 AS R1
FULL OUTER JOIN delta_BGP_2874745891700759920_6 AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;