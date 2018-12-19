#!/bin/bash

region=$(grep region_name /etc/watchmen/watchmen-producer.conf | cut -d'=' -f2)
hostname=`hostname | cut -d '.' -f1`
sriov_1=$(ip l | grep -B 2 vf | grep eth | grep state | head -1 | awk -F":" '{print $2}' | tr -d ' ')
sriov_2=$(ip l | grep -B 2 vf | grep eth | grep state | tail -1 | awk -F":" '{print $2}' | tr -d ' ')

monitor_sriov_port()
{
  eth_name=$1

  sriov_state=$(ip l | grep "${eth_name}:" | sed 's/^.*state //g' | awk '{print $1}'  |  tr '[a-z]' '[A-Z]' )

  if [[ -f /var/cmcc-la/data/sriov_fault_raised.$eth_name  && X$sriov_state = XUP ]]
  then
    echo "clear alarm $eth_name"
    ## clear alarm
    /usr/bin/watchmen-client create-event -sf -src     Region=$region,CeeFunction=1,Node=$hostname,Network=SR-IOV,Aggregator=sriov,EthernetPort=$eth_name -ma 193 -mi 2031681 -s CLEARED  -e communicationsAlarm -p m3100LossOfSignal   -sp "Ethernet Port Fault" -t "Network=SR-IOV,Aggregator=sriov,EthernetPort=$eth_name"

    rm -rf /var/cmcc-la/data/sriov_fault_raised.$eth_name
  elif [[ ! -f /var/cmcc-la/data/sriov_fault_raised.$eth_name  && X$sriov_state = XDOWN ]]
  then
    echo "raise alarm $eth_name"
    ## raise alarm
    /usr/bin/watchmen-client create-event -sf -src
#source-----------------	
	Region=$region,CeeFunction=1,Node=$hostname,Network=SR-IOV,Aggregator=sriov,EthernetPort=$eth_name 
	#communicationsAlarm -p m3100LossOfSignal other -sp falied
	-ma 193 
	-mi 2031681 -s MAJOR  -e communicationsAlarm -p m3100LossOfSignal   -sp "Ethernet Port Fault" -t "Network=SR-IOV,Aggregator=sriov,EthernetPort=$eth_name"

    touch /var/cmcc-la/data/sriov_fault_raised.$eth_name

  fi
}

while [ true ]
do
  ovs-vsctl show | grep dpdk | grep error >/dev/null
  if [ $? -eq 0 ]
  then
 ## dpdk to sriov patch deployed
    monitor_sriov_port $sriov_1
    monitor_sriov_port $sriov_2
  fi

  sleep 1

done
