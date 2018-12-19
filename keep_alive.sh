#!/bin/bash

vm_uuid=$1
region=`grep "region_name" /etc/watchmen/watchmen-producer.conf | cut -d"=" -f2`
count=0
source /var/cmcc-la/data/openrc

## get curr status
vm_curr_status=`nova list --all  --fields status | grep $vm_uuid | awk -F"|" '{print $3}' | tr -d ' '`

if [ X"$vm_curr_status" = XSHUTOFF ]
then
  echo "start vm to keep it alive"
  count=0
  nova start $vm_uuid

  retValue=$?
  let count=$count+1
  while [[ $count -le 3 && $retVale -ne 0 ]]
  do
    nova start $vm_uuid
    retValue=$?
    let count=$count+1
    sleep 5
  done
elif [ X"$vm_curr_status" = XERROR ]
then
  echo "restore vm to keep it alive"
  sleep 50

  count=0
  nova  reset-state --active $vm_uuid

  retValue=$?
  let count=$count+1
  while [[ $count -le 2 && $retValue -ne 0 ]]
  do
    nova  reset-state --active $vm_uuid

  retValue=$?
  let count=$count+1
  while [[ $count -le 2 && $retValue -ne 0 ]]
  do
    nova  reset-state --active $vm_uuid
    retValue=$?
    let count=$count+1
    sleep 5
  done

  if [ $retValue -ne 0 ]
  then
    ## restore failed, generate alarm
    echo "restore failed , raise event"
    echo /etc/ceesi/scripts/mysql_create_event.sh create-event -sl -src Region=$region,CeeFunction=1,Tenant=$tenant_uuid,VM=$vm_uuid -ma 193 -mi 2032702 -s WARNING -e other -p m3100Indeterminate   -sp "VM Restore Failed"
    /etc/ceesi/scripts/mysql_create_event.sh create-event -sl -src Region=$region,CeeFunction=1,Tenant=$tenant_uuid,VM=$vm_uuid -ma 193 -mi 2032702 -s WARNING -e other -p m3100Indeterminate   -sp "VM Restore Failed"
  fi
fi

