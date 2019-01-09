#[root@fuel files]# cat libvirtevent.sh
#!/bin/bash
declare -A timeStamp
delayTime=30
org_host=$(hostname)
region=`grep region_name /etc/watchmen/watchmen-producer.conf | cut -d"=" -f2`
DIR=`dirname $0`
CUR_DIR=`pwd $DIR`
LOG_FILE=/var/log/libvirt/libvirtevent.log
to_capture_fault_restored=n

source /root/openrc

# EXEC=libvirtevent.sh
# if { ps aux|grep ${EXEC}|grep -v 'grep' ; } >/dev/null 2>&1 ; then
#    echo "${EXEC} is running"
#    exit 1
# fi

#virsh event --event watchdog --loop >/dev/null 2>&1
#virsh event --all --loop >/dev/null 2>&1

#stdbuf -i0 -o0 -e0  virsh event --event watchdog --loop | while IFS= read -r line

stdbuf -i0 -o0 -e0  virsh event --all --loop | while IFS= read -r line		#轮询,并按行读取virsh event
do
  eptime=$(date +%s)		
  tstime=$(date +%Y-%m-%d" "%H:%M:%S:%3N)
  echo $tstime:$line >> $LOG_FILE							#之后将时间和读取到的值输出到log文件
  myInstance=$(echo $line | awk '{print $5}' | sed 's/://')		#对读取到的值进行正则匹配
  myReason=$(echo $line | awk -F":" '{print $2}' | tr -d ' ')	#对读取到的值进行正则匹配
  myKey=$(echo $myInstance | sed 's/-//g')						#对读取到的值进行正则匹配
  eventType=$(echo $line | awk '{print $2}' | sed "s/'$//" | sed "s/^'//")	##对读取到的值进行正则匹配

  nodeName=$(grep "nova:name" /etc/libvirt/qemu/$myInstance.xml | sed 's/^\s*<nova:name>//' | sed 's/<\/nova:name>//')	#正则匹配nova:name
  tenant_id=$(grep "nova:project" /etc/libvirt/qemu/$myInstance.xml | cut -d"\"" -f2)		#正则匹配tenant_id
  ## for the cic or atlas vm
  [ -z $nodeName ] && nodeName=$myInstance			#nodeName的长度为0且nodename=$myInstance
  uuid=$(grep "<uuid>" /etc/libvirt/qemu/$myInstance.xml | sed 's/^\s*<uuid>//' | sed 's/<\/uuid>//')		#正则出vm_uuid
  deltatime=$((eptime - timeStamp[$myKey]))		#一个时间的差值
  if [[ $deltatime -gt $delayTime ]]	#如果$deltatime>$delayTime
  then
    #reset timestamp
    echo "$tstime:event type - domainName - $myInstance, nodeName - $nodeName, eventType - $eventType, myReason - $myReason" >> $LOG_FILE	#将一堆值输入到log文件里
    timeStamp[$myKey]="$eptime"		#重置了时间戳
    if [[ X$eventType = Xreboot && $myInstance =~ ^instance ]]	#如果$eventType==reboot且$myInstance =~ ^instance
    then
      minor_id=2032696		#赋值
	#从libvirt-event-time.conf中读数据然后正则,估计匹配出的是个time
      time=$(cat /var/cmcc-la/data/libvirt-event-time.conf | grep $uuid | grep $minor_id | awk '{print $3}')	
      if [[ -n $time &&  $time -gt 0 ]]			#如果$time非空且>0
      then
        wa_timestamp=$(date -d "$time second ago" +%Y-%m-%d" "%H:%M:%S.%6N -u)	#拼接时间戳	
        echo "Adjust $time second ahead for $uuid, $tstime==>$wa_timestamp" >> $LOG_FILE		#将一堆值输入到log文件里
      fi

      echo "$tstime VM $nodeName($uuid): Detected Virtual Machine OS Fault,possible reason: kernel panic" >> $LOG_FILE		#输入log文件然后报警
      echo watchmen-client create-event -sf -src Region="$region",CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032696 -s CRITICAL -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine OS Fault" -t "VM $nodeName($uuid):$myReason" >> $LOG_FILE
      watchmen-client create-event -sf -src Region="$region",CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032696 -s CRITICAL -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine OS Fault" -t "VM $nodeName($uuid):$myReason"

      ## ++WA below
      if [ -n "$wa_timestamp" ]		#如果$wa_timestamp非空串
      then
        python /var/cmcc-la/scripts/watchmen-fmevent-operate.py watchmen $minor_id $uuid "$wa_timestamp"		#运行一个python脚本 watchmen-fmevent-operate.py
      fi
      ## Workaround below , second alarm was just for tricky workaround to resolve rabbitmq
      #watchmen-client create-event -sf -src Region="$region",CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032696 -s CRITICAL -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine OS Fault" -t "VM $nodeName($uuid):$myReason"
      ## Workaround above
      to_capture_fault_restored=n		#?

      sleep 10
		#告警
      echo watchmen-client create-event -sf -src Region="$region",CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032696 -s CLEARED -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine OS Fault" -t "VM $nodeName($uuid):$myReason"  >> $LOG_FILE
      watchmen-client create-event -sf -src Region="$region",CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032696 -s CLEARED -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine OS Fault" -t "VM $nodeName($uuid):$myReason"
      ## Workaround below , second alarm was just for tricky workaround for rabbitmq
      #watchmen-client create-event -sf -src Region="$region",CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032696 -s CLEARED -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine OS Fault" -t "VM $nodeName($uuid):$myReason"
      ## Workaround above
    # If event type is lifecycle and reason is "Shutdown Finished" meanings qemu has been killed.
    elif [[ X$eventType == Xlifecycle && X$myReason == XShutdownFinished && $myInstance =~ ^instance || X$eventType == Xlifecycle && X$myReason == XStoppedFailed && $myInstance =~ ^instance ]];			#判断条件
    then
      ## kill <qemu process> shutdown finished
      ## kill -9 <qemu process> Stopped Failed
      ## if qemu had been protected , not generate alarm ,but restore it immediately
      #grep $myInstance /etc/ceesi/scripts/qemu-protected.conf
      #if [ $? -eq 0 ]
      #then
      #  echo "$myInstance was protected"
      #else
      minor_id=2032697
      echo "$tstime VM $nodeName($uuid): Detected Virtual Machine Running Fault , possible reason : qemu process had been killed" >> $LOG_FILE		#输出到log然后创建告警
      echo watchmen-client create-event -sl -src Region=$region,CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032697 -s WARNING -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine Running Fault" -t "VM $nodeName($uuid):$myReason" >>$LOG_FILE
      watchmen-client create-event -sl -src Region=$region,CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032697 -s WARNING -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine Running Fault" -t "VM $nodeName($uuid):$myReason"
    elif [[ X$eventType = Xlifecycle && $myInstance =~ ^instance && X$myReason == XStoppedDestroyed ]]	#判断条件
    then
      ## vm virsh destory :2017-09-08 15:00:18:598:event 'lifecycle' for domain instance-0000001b: Stopped Destroyed		
       echo "$tstime VM $nodeName($uuid): Detected Virtual Machine Running Fault , possible reason : vm been powered off or shutdown abnormal" >> $LOG_FILE	#输出到log然后创建告警
       echo watchmen-client create-event -sl -src Region=$region,CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032697 -s WARNING -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine Running Fault" -t "VM $nodeName($uuid):$myReason" >>$LOG_FILE
       watchmen-client create-event -sl -src Region=$region,CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032697 -s WARNING -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine Running Fault" -t "VM $nodeName($uuid):$myReason"
    fi

    if [ X$to_capture_fault_restored = Xy ]		#判断条件
    then
      #nohup /etc/ceesi/scripts/check_fault_restored.sh $minor_id $nodeName $uuid "$myReason" 2>&1&
      nohup /etc/ceesi/scripts/check_fault_restored.sh $minor_id $myInstance $uuid 2>&1&				#运行一个脚本	check_fault_restored.sh
    fi
  else				#最初的if中的else
    timeStamp[$myKey]="$eptime"
  fi

  sleep 1
done
