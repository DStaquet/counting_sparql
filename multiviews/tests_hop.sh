echo 'Average hop for 8k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 1000 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 10 -pc 0.1

echo 'Average hop for 44k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 100 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 10 -pc 0.1

echo 'Average hop for 84k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 50 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 10 -pc 0.1

echo 'Average hop for 118k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 35 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 10 -pc 0.1

echo 'Average hop for 164k triples distributed over 80 pods'
python3 multiviews.py -v 1000 -e 25 -b 4 -p 3000 3079 -qd multiviews/views -q multiviews/queries/standard.sparql -t hop -ed 10 -r 10 -pc 0.1