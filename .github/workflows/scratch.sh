
IFS='-'     # hyphen (-) is set as delimiter
read -ra ADDR <<< "Deploy with CircleCI-raft"   # str is read into an array as tokens separated by IFS
for i in "${ADDR[@]}"; do   # access each element of array
    echo "$i"
done
echo $ADDR
DEPLOY_ENV="${ADDR[1]}"
echo $DEPLOY_ENV

IFS=' '
