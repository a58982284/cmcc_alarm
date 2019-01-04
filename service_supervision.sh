#!/bin/bash


while getopts "s:u:" arg
do
    case $arg in
        s)
          service=$OPTARG
          ;;
        u)
          user=$OPTARG
          ;;
        *)
          echo "incorrect parameter"
          exit 1
          ;;
    esac
done


[ -z $service ] && echo "provide the service name to monitor" && exit 1

region=`grep "region_name" /etc/watchmen/watchmen-producer.conf | cut -d"=" -f2`
CMCC_LA_DATA_DIR="/var/cmcc-la/data"
NODE=`hostname | sed 's/\..*$//g'`

while [ true ]
do
  ps -ef | grep $service | grep ^$user | grep -v grep > /dev/null

  if [ $? -ne 0 ] 
  then
    echo "raise alert"
    watchmen-client create-event -sl -src "Region=$region,CeeFunction=1,Node=$NODE,Service=$service process" -ma 193 -mi 2031710 -s MAJOR -e other -p m3100Indeterminate   -sp "Service stopped" -t "On node:$NODE service: $service has been stopped. "

    sleep 120
  fi

  sleep 1
done


