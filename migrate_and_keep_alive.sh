#migrate_and_keep_alive.sh
#!/bin/bash

source /var/cmcc-la/data/openrc
vm_uuid=$1
echo "migrate and keep alive for vm - $vm_uuid"
sleep 30
nova migrate $vm_uuid
vm_status=`nova show $vm_uuid | grep status | grep -v host_status | awk -F "|" '{print $3}' | tr -d ' '`
while [ X"$vm_status" != XVERIFY_RESIZE ]
do
 sleep 5
  vm_status=`nova show $vm_uuid | grep status | grep -v host_status | awk -F "|" '{print $3}' | tr -d ' '`
done

nova resize-confirm $vm_uuid
nova start $vm_uuid

echo "$vm_uuid had been migrated and keep alive"

