CREATE TEMP TABLE delta_join_BGP_2874745891700759920_2 AS
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
FROM
  (SELECT G1.s AS t1,
          G2.s AS t2,
          G3.s AS t3,
          G4.s AS t4,
          G5.s AS t5,
          G6.s AS x,
          G5.o AS y,
          G1.k_count
   FROM delta_G G1,
        G G2,
        G G3,
        G G4,
        G G5,
        G G6
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link'
     AND G2.o = G3.s
     AND G3.p = 'http://example.org/edges/link'
     AND G3.o = G4.s
     AND G4.p = 'http://example.org/edges/link'
     AND G4.o = G5.s
     AND G5.p = 'http://example.org/edges/link'
     AND G6.p = 'http://example.org/edges/link'
     AND G1.s = G6.o) AS R1
FULL OUTER JOIN
  (SELECT G1.s AS t1,
          G2.s AS t2,
          G3.s AS t3,
          G4.s AS t4,
          G5.s AS t5,
          G6.s AS x,
          G5.o AS y,
          G2.k_count
   FROM nu_G G1,
        delta_G G2,
        G G3,
        G G4,
        G G5,
        G G6
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link'
     AND G2.o = G3.s
     AND G3.p = 'http://example.org/edges/link'
     AND G3.o = G4.s
     AND G4.p = 'http://example.org/edges/link'
     AND G4.o = G5.s
     AND G5.p = 'http://example.org/edges/link'
     AND G6.p = 'http://example.org/edges/link'
     AND G1.s = G6.o) AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;

CREATE TEMP TABLE delta_join_BGP_2874745891700759920_3 AS
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
FROM delta_join_BGP_2874745891700759920_2 AS R1
FULL OUTER JOIN
  (SELECT G1.s AS t1,
          G2.s AS t2,
          G3.s AS t3,
          G4.s AS t4,
          G5.s AS t5,
          G6.s AS x,
          G5.o AS y,
          G3.k_count
   FROM nu_G G1,
        nu_G G2,
        delta_G G3,
        G G4,
        G G5,
        G G6
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link'
     AND G2.o = G3.s
     AND G3.p = 'http://example.org/edges/link'
     AND G3.o = G4.s
     AND G4.p = 'http://example.org/edges/link'
     AND G4.o = G5.s
     AND G5.p = 'http://example.org/edges/link'
     AND G6.p = 'http://example.org/edges/link'
     AND G1.s = G6.o) AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;

CREATE TEMP TABLE delta_join_BGP_2874745891700759920_4 AS
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
FROM delta_join_BGP_2874745891700759920_3 AS R1
FULL OUTER JOIN
  (SELECT G1.s AS t1,
          G2.s AS t2,
          G3.s AS t3,
          G4.s AS t4,
          G5.s AS t5,
          G6.s AS x,
          G5.o AS y,
          G4.k_count
   FROM nu_G G1,
        nu_G G2,
        nu_G G3,
        delta_G G4,
        G G5,
        G G6
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link'
     AND G2.o = G3.s
     AND G3.p = 'http://example.org/edges/link'
     AND G3.o = G4.s
     AND G4.p = 'http://example.org/edges/link'
     AND G4.o = G5.s
     AND G5.p = 'http://example.org/edges/link'
     AND G6.p = 'http://example.org/edges/link'
     AND G1.s = G6.o) AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;

CREATE TEMP TABLE delta_join_BGP_2874745891700759920_5 AS
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
FROM delta_join_BGP_2874745891700759920_4 AS R1
FULL OUTER JOIN
  (SELECT G1.s AS t1,
          G2.s AS t2,
          G3.s AS t3,
          G4.s AS t4,
          G5.s AS t5,
          G6.s AS x,
          G5.o AS y,
          G5.k_count
   FROM nu_G G1,
        nu_G G2,
        nu_G G3,
        nu_G G4,
        delta_G G5,
        G G6
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link'
     AND G2.o = G3.s
     AND G3.p = 'http://example.org/edges/link'
     AND G3.o = G4.s
     AND G4.p = 'http://example.org/edges/link'
     AND G4.o = G5.s
     AND G5.p = 'http://example.org/edges/link'
     AND G6.p = 'http://example.org/edges/link'
     AND G1.s = G6.o) AS R2 ON R1.t1 = R2.t1
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
FROM delta_join_BGP_2874745891700759920_5 AS R1
FULL OUTER JOIN
  (SELECT G1.s AS t1,
          G2.s AS t2,
          G3.s AS t3,
          G4.s AS t4,
          G5.s AS t5,
          G6.s AS x,
          G5.o AS y,
          G6.k_count
   FROM nu_G G1,
        nu_G G2,
        nu_G G3,
        nu_G G4,
        nu_G G5,
        delta_G G6
   WHERE G1.p = 'http://example.org/edges/link'
     AND G1.o = G2.s
     AND G2.p = 'http://example.org/edges/link'
     AND G2.o = G3.s
     AND G3.p = 'http://example.org/edges/link'
     AND G3.o = G4.s
     AND G4.p = 'http://example.org/edges/link'
     AND G4.o = G5.s
     AND G5.p = 'http://example.org/edges/link'
     AND G6.p = 'http://example.org/edges/link'
     AND G1.s = G6.o) AS R2 ON R1.t1 = R2.t1
AND R1.t3 = R2.t3
AND R1.x = R2.x
AND R1.t4 = R2.t4
AND R1.t2 = R2.t2
AND R1.t5 = R2.t5
AND R1.y = R2.y;