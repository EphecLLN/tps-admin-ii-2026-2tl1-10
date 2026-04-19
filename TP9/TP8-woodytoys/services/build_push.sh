#/bin/bash

set -e

default_version="3"
version=${1:-"$default_version"}


docker build -t gloutamax/woody_api:"$version" api 
docker tag gloutamax/woody_api:"$version" gloutamax/woody_api:latest

docker build -t gloutamax/woody_rp:"$version" reverse-proxy
docker tag gloutamax/woody_rp:"$version" gloutamax/woody_rp:latest

docker build -t gloutamax/woody_database:"$version" database
docker tag gloutamax/woody_database:"$version" gloutamax/woody_database:latest

docker build -t gloutamax/woody_front:"$version" front
docker tag gloutamax/woody_front:"$version" gloutamax/woody_front:latest


# avec le "set -e" du début, je suis assuré que rien ne sera pushé si un seul build ne c'est pas bien passé

docker push gloutamax/woody_api:"$version"
docker push gloutamax/woody_api:latest

docker push gloutamax/woody_rp:"$version"
docker push gloutamax/woody_rp:latest

docker push gloutamax/woody_front:"$version"
docker push gloutamax/woody_front:latest

docker push gloutamax/woody_database:"$version"
docker push gloutamax/woody_database:latest
