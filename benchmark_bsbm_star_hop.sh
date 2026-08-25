echo 'Running star shape query'
python3 main.py Queries/hops/star_bsbm.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/100k_product/base.csv -dl bsbm_data/output_data/100k_product -nf bsbm_data/output_data/100k_product -m -r 5 -s -icsv -ocsv measurements/output_bsbm.csv > measurements/star_shape_query_bsbm_100k.txt


echo 'Running hop shape query'
python3 main.py Queries/hops/hop_bsbm.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/100k_product/base.csv -dl bsbm_data/output_data/100k_product -nf bsbm_data/output_data/100k_product -m -r 5 -s -icsv -ocsv measurements/output_bsbm.csv > measurements/hop_shape_query_bsbm_100k.txt