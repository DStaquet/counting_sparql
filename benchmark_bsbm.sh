#!/usr/bin/env bash

echo 'Installing pip requirements.'
python3 -m pip install -r requirements.txt

echo 'Constructing 100k products for the BSBM queries'
python3 example_constructor/bsbm_setup.py bsbm_data/input_data/chain_100k.ttl bsbm_data/input_data/chain_update_100k.nt bsbm_data/output_data/100k_product


echo 'Running the benchmark for Query1 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query1/query1.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/100k_product/base.csv -dl bsbm_data/output_data/100k_product -nf bsbm_data/output_data/100k_product -m -r 5 -s -icsv -ocsv measurements/output_bsbm.csv > measurements/bsbm_query1_100k.txt

echo 'Running the benchmark for Query2 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query2/query2.sparql temp_tests/chain_benchmark_temp -d bsbm_data/output_data/100k_product/base.csv -dl bsbm_data/output_data/100k_product -nf bsbm_data/output_data/100k_product -m -r 5 -s -ocsv measurements/output_bsbm.csv > measurements/bsbm_query2_100k.txt

echo 'Running the benchmark for Query3 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query3/query3.sparql temp_tests/chain_benchmark_temp -d bsbm_data/output_data/100k_product/base.csv -dl bsbm_data/output_data/100k_product -nf bsbm_data/output_data/100k_product -m -r 5 -s -ocsv measurements/output_bsbm.csv > measurements/bsbm_query3_100k.txt

echo 'Running the benchmark for Query4 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query4/query4.sparql temp_tests/chain_benchmark_temp -d bsbm_data/output_data/100k_product/base.csv -dl bsbm_data/output_data/100k_product -nf bsbm_data/output_data/100k_product -m -r 5 -s -ocsv measurements/output_bsbm.csv > measurements/bsbm_query4_100k.txt