INSERT INTO delta_prep_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT G4.o AS label,
       G1.s AS product,
       G5.o AS value1,
       G1.k_count
FROM delta_G G1,
     G G2,
     G G3,
     G G4,
     G G5
WHERE G1.p = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType16'
  AND G1.s = G2.s
  AND G2.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G2.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature701'
  AND G1.s = G3.s
  AND G3.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G3.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature707'
  AND G1.s = G4.s
  AND G4.p = 'http://www.w3.org/2000/01/rdf-schema#label'
  AND G1.s = G5.s
  AND G5.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productPropertyNumeric1';


INSERT INTO delta_prep_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT G4.o AS label,
       G1.s AS product,
       G5.o AS value1,
       G2.k_count
FROM nu_G G1,
     delta_G G2,
     G G3,
     G G4,
     G G5
WHERE G1.p = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType16'
  AND G1.s = G2.s
  AND G2.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G2.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature701'
  AND G1.s = G3.s
  AND G3.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G3.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature707'
  AND G1.s = G4.s
  AND G4.p = 'http://www.w3.org/2000/01/rdf-schema#label'
  AND G1.s = G5.s
  AND G5.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productPropertyNumeric1';


INSERT INTO delta_prep_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT G4.o AS label,
       G1.s AS product,
       G5.o AS value1,
       G3.k_count
FROM nu_G G1,
     nu_G G2,
     delta_G G3,
     G G4,
     G G5
WHERE G1.p = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType16'
  AND G1.s = G2.s
  AND G2.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G2.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature701'
  AND G1.s = G3.s
  AND G3.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G3.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature707'
  AND G1.s = G4.s
  AND G4.p = 'http://www.w3.org/2000/01/rdf-schema#label'
  AND G1.s = G5.s
  AND G5.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productPropertyNumeric1';


INSERT INTO delta_prep_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT G4.o AS label,
       G1.s AS product,
       G5.o AS value1,
       G4.k_count
FROM nu_G G1,
     nu_G G2,
     nu_G G3,
     delta_G G4,
     G G5
WHERE G1.p = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType16'
  AND G1.s = G2.s
  AND G2.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G2.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature701'
  AND G1.s = G3.s
  AND G3.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G3.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature707'
  AND G1.s = G4.s
  AND G4.p = 'http://www.w3.org/2000/01/rdf-schema#label'
  AND G1.s = G5.s
  AND G5.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productPropertyNumeric1';


INSERT INTO delta_prep_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT G4.o AS label,
       G1.s AS product,
       G5.o AS value1,
       G5.k_count
FROM nu_G G1,
     nu_G G2,
     nu_G G3,
     nu_G G4,
     delta_G G5
WHERE G1.p = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
  AND G1.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType16'
  AND G1.s = G2.s
  AND G2.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G2.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature701'
  AND G1.s = G3.s
  AND G3.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature'
  AND G3.o = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature707'
  AND G1.s = G4.s
  AND G4.p = 'http://www.w3.org/2000/01/rdf-schema#label'
  AND G1.s = G5.s
  AND G5.p = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productPropertyNumeric1';


INSERT INTO delta_BGP_1397345390056075867 (label, product, value1, k_count)
SELECT label,
       product,
       value1,
       SUM(k_count) AS k_count
FROM delta_prep_BGP_1397345390056075867
GROUP BY label,
         product,
         value1;