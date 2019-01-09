#!/bin/bash

org_host=$(hostname)
region=`grep "region_name" /etc/watchmen/watchmen-producer.conf | cut -d"=" -f2`
CMCC_LA_DIR=/var/cmcc-la/
CMCC_LA_DATA_DIR=${CMCC_LA_DIR}/data

for pid in `ps -ef | grep generate_compute_instance_with_volume.sh | grep -v grep | awk '{print $2}'`
do
  kill -9 $pid
done

nohup $CMCC_LA_DIR/scripts/generate_compute_instance_with_volume.sh >/dev/null 2>&1 & 

sleep 120

source /var/cmcc-la/data/openrc
while [ true ] 
do
  #step 1 , find out the compute that two storage port was down
  for compute in `watchmen-client active-alarm-list  | grep "Ethernet Port Aggregator Fault" | grep storage | sed 's/^.*Node=//g' | sed 's/,.*$//g'`
  do
    ##step 2 ,find the instance located in this compute with external storage
    grep $compute $CMCC_LA_DATA_DIR/compute_instance_with_volume.out | while read line
    do
      uuid=`echo $line | awk '{print $2}'`
  
      [ -f $CMCC_LA_DATA_DIR/.${compute}.${uuid}.storage_alarm.raised ] && continue
      ## raise alarm
      tenant_id=`echo $line | awk '{print $3}'`
      watchmen-client create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$uuid -ma 193 -mi 2032707 -s MAJOR -e equipmentAlarm -p m3100Indeterminate -sp "VM External Storage Fault" -t "Pyhsical Storage Network Fault on $compute"

      touch $CMCC_LA_DATA_DIR/.${compute}.${uuid}.storage_alarm.raised
    done
  done

  ## check for the alarm clear
  for i in `ls $CMCC_LA_DATA_DIR/.*.storage_alarm.raised 2>/dev/null`
  do
    compute=`echo $i | awk -F"." '{print $2}'`
    watchmen-client  active-alarm-list | grep "Ethernet Port Aggregator Fault" | grep storage | grep $compute

    if [ $? -ne 0 ]
    then
       uuid=`echo $i | awk -F"." '{print $3}'`
       [ ! -f $CMCC_LA_DATA_DIR/.${compute}.${uuid}.storage_alarm.raised ] && continue

       ## clear alarm
       tenant_id=`nova show $uuid | grep tenant_id | awk -F"|" '{print $3}' | tr -d ' '`
       watchmen-client create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$uuid -ma 193 -mi 2032707 -s CLEARED -e equipmentAlarm -p m3100Indeterminate -sp "VM External Storage Fault" -t "Pyhsical Storage Network Fault on $compute"

       rm $CMCC_LA_DATA_DIR/.${compute}.${uuid}.storage_alarm.raised
    fi

  done


  sleep 1
done
