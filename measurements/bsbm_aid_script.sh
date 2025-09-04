echo 'Run the 1000 products BSBM queries'

python3 main.py benchmarker/Queries/BSBM/Query1/query1.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -icsv -ocsv measurements/query1_output_bsbm1k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query2/query2.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -icsv -ocsv measurements/query2_output_bsbm1k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query3/query3.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -icsv -ocsv measurements/query3_output_bsbm1k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query4/query4.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/1000_product/base.csv -dl bsbm_data/output_data/1000_product -nf bsbm_data/output_data/1000_product -m -r 5 -s -icsv -ocsv measurements/query4_output_bsbm1k_new.csv



echo 'Run the 10K products BSBM queries'

python3 main.py benchmarker/Queries/BSBM/Query1/query1.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/10k_product/base.csv -dl bsbm_data/output_data/10k_product -nf bsbm_data/output_data/10k_product -m -r 5 -s -icsv -ocsv measurements/query1_output_bsbm10k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query2/query2.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/10k_product/base.csv -dl bsbm_data/output_data/10k_product -nf bsbm_data/output_data/10k_product -m -r 5 -s -icsv -ocsv measurements/query2_output_bsbm10k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query3/query3.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/10k_product/base.csv -dl bsbm_data/output_data/10k_product -nf bsbm_data/output_data/10k_product -m -r 5 -s -icsv -ocsv measurements/query3_output_bsbm10k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query4/query4.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/10k_product/base.csv -dl bsbm_data/output_data/10k_product -nf bsbm_data/output_data/10k_product -m -r 5 -s -icsv -ocsv measurements/query4_output_bsbm10k_new.csv




echo 'Run the 15K products BSBM queries'

python3 main.py benchmarker/Queries/BSBM/Query1/query1.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/15k_product/base.csv -dl bsbm_data/output_data/15k_product -nf bsbm_data/output_data/15k_product -m -r 5 -s -icsv -ocsv measurements/query1_output_bsbm15k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query2/query2.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/15k_product/base.csv -dl bsbm_data/output_data/15k_product -nf bsbm_data/output_data/15k_product -m -r 5 -s -icsv -ocsv measurements/query2_output_bsbm15k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query3/query3.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/15k_product/base.csv -dl bsbm_data/output_data/15k_product -nf bsbm_data/output_data/15k_product -m -r 5 -s -icsv -ocsv measurements/query3_output_bsbm15k_new.csv
python3 main.py benchmarker/Queries/BSBM/Query4/query4.sparql temp_tests/chain_benchmark -d bsbm_data/output_data/15k_product/base.csv -dl bsbm_data/output_data/15k_product -nf bsbm_data/output_data/15k_product -m -r 5 -s -icsv -ocsv measurements/query4_output_bsbm15k_new.csv