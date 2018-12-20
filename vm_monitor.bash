#!/bin/bash

#CUR_DIR=`pwd $0`
SCRIPTS_DIR=/var/cmcc-la/scripts
DATA_DIR=/var/cmcc-la/data
vm_last_status_file=${DATA_DIR}/vm_last_status.txt
region=`grep "region_name" /etc/watchmen/watchmen-producer.conf | cut -d"=" -f2`

## if no such source, the nova list will report error that must provide a user name or user id
source /var/cmcc-la/data/openrc

if [ ! -f  ${vm_last_status_file} ]
then
  ## create the vm status file
  #nova list --all 2>/dev/null | grep ^"|" | grep -v ID | while read line
  nova list --all 2>/dev/null | grep ^"|" | grep -v ID | while read line
  do
   vm_uuid=`echo "$line" | awk -F"|" '{print $2}' | tr -d ' '`
   vm_name=`echo "$line" | awk -F"|" '{print $3}' | tr -d ' ' `
   vm_last_status=`echo "$line" | awk -F"|" '{print $5}' | tr -d ' ' `
   echo "$vm_name,$vm_uuid,$vm_last_status" >> ${vm_last_status_file}
  done
fi

while [ ture ]
do
  cp -p ${vm_last_status_file} ${vm_last_status_file}.bak
  nova list --all 2>/dev/null |  grep ^"|" | grep -v ID | while read line
  do
    [ $? -ne 0 ] && continue

    vm_uuid=`echo $line | awk -F"|" '{print $2}' | tr -d ' '`
    vm_name=`echo $line | awk -F"|" '{print $3}' | tr -d ' '`
    tenant_id=`echo $line | awk -F"|" '{print $4}' | tr -d ' '`
    vm_curr_status=`echo $line | awk -F"|" '{print $5}' | tr -d '  '`
    vm_last_status=`cat ${vm_last_status_file} | grep $vm_uuid | awk -F, '{print $3}'`
    status_changed=
    #echo "$vm_uuid, last_status- $vm_last_status,curr status - $vm_curr_status"

    ## to find out the removed vm
    sed -i "/^$vm_name.*/d" ${vm_last_status_file}.bak

    if [ X$vm_last_status = X ]
    then
      #new added vm
      echo "`date`:$vm_name added to nova"
      echo "$vm_name,$vm_uuid,$vm_curr_status" >> $vm_last_status_file
    elif [ X"$vm_last_status" = X"$vm_curr_status" ]
    then
      continue;
    elif [ X"$vm_last_status" = XACTIVE -a X"$vm_curr_status" = XERROR ]
    then
       echo "raise event -to error "
       #/etc/ceesi/scripts/mysql_create_event.sh create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032692 -s CRITICAL -e equipmentAlarm -p m3100Indeterminate -sp "VM status became error" -t "VM $vm_name/$vm_uuid has changed to status error"
       watchmen-client create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032692 -s CRITICAL -e equipmentAlarm -p m3100Indeterminate -sp "VM status became error" -t "VM $vm_name/$vm_uuid has changed to status error"
       status_changed=y


       meta_data=`nova show $vm_uuid | grep metadata | awk -F"|" '{print $3}' | tr -d "{}\" "`
       echo $meta_data | grep "Auto_Restore:true"
       retValue=$?

       if [ $retValue -eq 0 ]
       then
         nohup $SCRIPTS_DIR/keep_alive.sh $vm_uuid &
       fi
    elif [ X"$vm_last_status" = XACTIVE -a X"$vm_curr_status" = XSHUTOFF ]
    then
       echo "raise event -to shutoff "
       #/etc/ceesi/scripts/mysql_create_event.sh create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032693 -s CRITICAL -e equipmentAlarm -p m3100Indeterminate -sp "VM status became shutoff" -t "VM $vm_name/$vm_uuid has changed to status shutoff"
       watchmen-client create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032693 -s CRITICAL -e equipmentAlarm -p m3100Indeterminate -sp "VM status became shutoff" -t "VM $vm_name/$vm_uuid has changed to status shutoff"
       status_changed=y

       ## get meta data for vm,
       ## if meta data:KeepAlive=true, it means keep it alive on same host
       ## if meta data:keepAlive=true && Alive_Policy=migration, it means keep it alive in a different host
       meta_data=`nova show $vm_uuid | grep metadata | awk -F"|" '{print $3}' | tr -d "{}\" "`
       echo $meta_data | grep "Keep_Alive:true"
       retValue1=$?
       echo $meta_data | grep "Alive_Policy:migration"
       retValue2=$?
       echo $meta_data | grep "Alive_Policy:evacuation"
       retValue3=$?

       if [ $retValue1 -eq 0 -a $retValue2 -eq 0 ]
       then
         #migrate and keep alive
         nohup $SCRIPTS_DIR/migrate_and_keep_alive.sh $vm_uuid &
       elif [ $retValue1 -eq 0 -a $retValue3 -eq 0 ]
       then
         #evacuate the vm for a DOWN host
         nohup $SCRIPTS_DIR/evacuate_vm.sh $vm_uuid &
       elif [ $retValue1 -eq 0 ]
       then
         #keep alive
         nohup $SCRIPTS_DIR/keep_alive.sh $vm_uuid &
       fi
    elif [ X"$vm_last_status" = XERROR -a X"$vm_curr_status" = XACTIVE ]
    then
       echo "clear event -error"
       #/etc/ceesi/scripts/mysql_create_event.sh create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032692 -s CLEARED -e equipmentAlarm -p m3100Indeterminate -sp "VM status became error" -t "VM $vm_name/$vm_uuid has changed to status error"
       watchmen-client create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032692 -s CLEARED -e equipmentAlarm -p m3100Indeterminate -sp "VM status became error" -t "VM $vm_name/$vm_uuid has changed to status error"
       status_changed=y
    elif [ X"$vm_last_status" = XSHUTOFF -a X"$vm_curr_status" = XACTIVE ]
    then
       echo "clear event - shutoff"
       #/etc/ceesi/scripts/mysql_create_event.sh create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032693 -s CLEARED -e equipmentAlarm -p m3100Indeterminate -sp "VM status became shutoff" -t "VM $vm_name/$vm_uuid has changed to status shutoff"
       watchmen-client create-event -sf -src Region=$region,CeeFunction=1,Tenant=${tenant_id},VM=$vm_uuid -ma 193 -mi 2032693 -s CLEARED -e equipmentAlarm -p m3100Indeterminate -sp "VM status became shutoff" -t "VM $vm_name/$vm_uuid has changed to status shutoff"
       status_changed=y
    fi

    if [ X"$status_changed"=Xy ]
    then
      echo "`date` :$vm_name status changed from $vm_last_status to $vm_curr_status"
      #sed -i "s/$vm_name,$vm_uuid,$vm_last_status/$vm_name,$vm_uuid,$vm_curr_status/g" ${vm_last_status_file}
      sed -i "/^$vm_name.*/d" ${vm_last_status_file}
      echo "$vm_name,$vm_uuid,$vm_curr_status" >> $vm_last_status_file

    fi
  done

  ## for the vm removed, remove the last_vm_status from file
  cat ${vm_last_status_file}.bak | while read line
  do
    vm_name=`echo $line | awk -F, '{print $1}'`
    echo "`date`:remove vm $vm_name"
    sed -i "/^$vm_name.*/d" ${vm_last_status_file}
  done

  sleep 1
done
