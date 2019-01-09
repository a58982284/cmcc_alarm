#!/bin/bash

CMCC_LA_DIR=/var/cmcc-la
output=$CMCC_LA_DIR/data/compute_instance_with_volume.out
temp_output=$CMCC_LA_DIR/compute_instance_with_volume.tempout

source /var/cmcc-la/data/openrc

touch $output
while [ true ]
do
  nova list --all --fields host,tenant_id | grep compute | awk '{print $2,$4,$6}' | while read line
  do
    compute=`echo $line | awk '{print $2}' | awk -F"." '{print $1}'`
    uuid=`echo $line | awk '{print $1}'`
    tenant_id=`echo $line | awk '{print $3}'`
    cinder list | grep in-use | grep $uuid >/dev/null

    if [ $? -eq 0 ]
    then
      echo $compute $uuid $tenant_id >> $temp_output
    fi
  done

  if [ -f $output ]
  then
    sum1=`md5sum $output | awk '{print $1}'`
    sum2=`md5sum $temp_output | awk '{print $1}'`

    if [ X"$sum1" != X"$sum2" ]
    then
      cp -p $temp_output $output
    fi
  fi

  rm -rf $temp_output
  sleep 60
done
