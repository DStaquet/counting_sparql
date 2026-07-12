echo 'Average hospital for 8k triples distributed over 80 pods'
python3 multiviews.py -p 3000 3079 -t we_are -qd temp_views -q multiviews/queries/hospital_score.sparql -tr 100 -ho 100 -pc 0.1 -ed 10 > multiviews/avg_hosp_100_100.txt

echo 'Average hospital for 80k triples distributed over 80 pods'
python3 multiviews.py -p 3000 3079 -t we_are -qd temp_views -q multiviews/queries/hospital_score.sparql -tr 1000 -ho 100 -pc 0.1 -ed 10 > multiviews/avg_hosp_1k_100.txt

echo 'Average hospital for 400k triples distributed over 80 pods'
python3 multiviews.py -p 3000 3079 -t we_are -qd temp_views -q multiviews/queries/hospital_score.sparql -tr 5000 -ho 100 -pc 0.1 -ed 10 > multiviews/avg_hosp_5k_100.txt

echo 'Average hospital for 800k triples distributed over 80 pods'
python3 multiviews.py -p 3000 3079 -t we_are -qd temp_views -q multiviews/queries/hospital_score.sparql -tr 10000 -ho 100 -pc 0.1 -ed 10 > multiviews/avg_hosp_10k_100.txt