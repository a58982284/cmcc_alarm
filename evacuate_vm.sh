#!/bin/bash

vm_uuid=$1
sleep 30
source /var/cmcc-la/data/openrc

original_host=`nova show $vm_uuid | grep hypervisor_hostname | awk -F"|" '{print $3}' | tr -d ' '`
ping -c 1 $original_host
while [ $? -eq 0 ]
do
  sleep 10
  ping -c 1 $original_host
done

count=0
while [ $count -lt 3 ]
do
  ping -c 1 $original_host
  [ $? -ne 0 ] && let count=$count+1
  sleep 5
done

nova evacuate $vm_uuid

echo "$vm_uuid had been evacuated"
