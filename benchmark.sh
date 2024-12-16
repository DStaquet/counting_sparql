#!/usr/bin/env bash

# Tri_hop query

# Run the benchmark for the tri_hop query with 1000 nodes and 10, 20 and 50 delta values
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_1000.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_1000_10.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_1000_10.csv -r 250 > benchmarker/data/tri_hop_1000_10.txt
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_1000.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_1000_20.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_1000_20.csv -r 250 > benchmarker/data/tri_hop_1000_20.txt
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_1000.csv -dl data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_delta_1000_50.csv -nf data/exemplary_data/hop_graphs_n_1000/graph_chain_tri_hop_nu_1000_50.csv -r 250 > benchmarker/data/tri_hop_1000_50.txt

# Run the benchmark for the tri_hop query with 100 nodes and 10, 20 and 50 delta values
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_100.csv -dl data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_delta_100_10.csv -nf data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_nu_100_10.csv -r 50 > benchmarker/data/tri_hop_100_10.txt
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_100.csv -dl data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_delta_100_20.csv -nf data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_nu_100_20.csv -r 50 > benchmarker/data/tri_hop_100_20.txt
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_100.csv -dl data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_delta_100_50.csv -nf data/exemplary_data/hop_graphs_n_100/graph_chain_tri_hop_nu_100_50.csv -r 50 > benchmarker/data/tri_hop_100_50.txt

# Run the benchmark for the tri_hop query with 50 nodes and 10, 20 and 50 delta values
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_50.csv -dl data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_delta_50_10.csv -nf data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_nu_50_10.csv -r 25 > benchmarker/data/tri_hop_50_10.txt
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_50.csv -dl data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_delta_50_20.csv -nf data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_nu_50_20.csv -r 25 > benchmarker/data/tri_hop_50_20.txt
python3 main.py Queries/hops/tri_hop.sparql temp_tests -d data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_50.csv -dl data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_delta_50_50.csv -nf data/exemplary_data/hop_graphs_n_50/graph_chain_tri_hop_nu_50_50.csv -r 25 > benchmarker/data/tri_hop_50_50.txt