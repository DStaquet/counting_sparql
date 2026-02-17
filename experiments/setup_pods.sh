#npx @solid/community-server -p 3003 &
#npx @solid/community-server &
#npx @solid/community-server -p 3001 &
#npx @solid/community-server -p 3002 &
# npx @solid/community-server -p 3004

ports=3000
for i in $(seq 1 5);
do
    port=$((ports+i))
    trap 'kill $BGPID; exit' INT
    npx @solid/community-server -p $port &
done
BPGID=$!
npx @solid/community-server -p $ports