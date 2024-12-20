
echo 'Constructing 1000 products for the BSBM queries'
python3 example_constructor/bsbm_setup.py bsbm_data/input_data/chain_1000.ttl bsbm_data/input_data/short_1000.nt bsbm_data/output_data/1000_product


echo 'Running the benchmark for Query1 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query1/query1.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -icsv -ocsv measurements/output_bsbm.csv > measurements/bsbm_query1.txt

echo 'Running the benchmark for Query2 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query2/query2.sparql temp_tests/chain_benchmark_temp -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -ocsv measurements/output_bsbm.csv > measurements/bsbm_query2.txt

echo 'Running the benchmark for Query3 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query3/query3.sparql temp_tests/chain_benchmark_temp -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -ocsv measurements/output_bsbm.csv > measurements/bsbm_query3.txt

echo 'Running the benchmark for Query4 with 1000 products'
python3 main.py benchmarker/Queries/BSBM/Query4/query4.sparql temp_tests/chain_benchmark_temp -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -ocsv measurements/output_bsbm.csv > measurements/bsbm_query4.txt