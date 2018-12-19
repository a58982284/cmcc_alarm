#[root@fuel files]# vim traffic-link-monitor.sh
#!/bin/bash
org_host=$(hostname)
region=`grep region_name /etc/watchmen/watchmen-producer.conf | cut -d"=" -f2`
CMCC_LA_DATA_DIR=/var/cmcc-la/data
alarm_raised=$CMCC_LA_DATA_DIR/.traffic_link_monitor_alarm_raised

while [ true ]
do
  dpdk_down_count=`ovs-ofctl dump-ports-desc br-prv | grep -A 2 dpdk | grep state | grep LINK_DOWN | wc -l `

  if [[ $dpdk_down_count -eq 2 && ! -f $alarm_raised ]]
  then
    ## raise alarm
    for instance in `virsh list | grep instance | awk '{print $2}'`
    do
      uuid=`ps -ef | grep qemu | grep $instance | sed 's/^.*uuid=//g' | sed 's/,.*$//g'`
      tenant_id=$(grep "nova:project" /etc/libvirt/qemu/$instance.xml | cut -d"\"" -f2)
      watchmen-client create-event -sf -src Region=$region,CeeFunction="1",Tenant="$tenant_id",VM=$uuid -ma 193 -mi 2032705 -s CRITICAL -e communicationsAlarm  -p m3100Indeterminate -sp "Virtual Machine Traffic Link Fault" -t "Physical Network Fault on $org_host"
    done

    touch $alarm_raised
  elif [[ $dpdk_down_count -lt 2 && -f $alarm_raised ]]
  then
    ## clear alarm
    for instance in `virsh list | grep instance | awk '{print $2}'`
    do
      uuid=`ps -ef | grep qemu | grep $instance | sed 's/^.*uuid=//g' | sed 's/,.*$//g'`
      tenant_id=$(grep "nova:project" /etc/libvirt/qemu/$instance.xml | cut -d"\"" -f2)