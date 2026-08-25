echo 'Average hop for 7k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 1000 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 5 -pc 0.1 > multiviews/hops_1k_1k.txt

echo 'Average hop for 34k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 100 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 5 -pc 0.1 > multiviews/hops_1k_100.txt

echo 'Average hop for 64k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 50 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 5 -pc 0.1 > multiviews/hops_1k_50.txt

echo 'Average hop for 89k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 35 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 5 -pc 0.1 > multiviews/hops_1k_35.txt

echo 'Average hop for 124k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 25 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 5 -pc 0.1 > multiviews/hops_1k_25.txt

echo 'Average hop for 379k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 8 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 5 -pc 0.1 > multiviews/hops_1k_8.txt