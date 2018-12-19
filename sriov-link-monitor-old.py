# coding:utf-8
import commands
import sys
import os
import time
from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender


def monitor_sriov_port(sriov_num):
    eth_name = sriov_num
    region_status, region = commands.getstatusoutput(
        "grep region_name /etc/watchmen/watchmen-producer.conf | cut -d'=' -f2")
    hostname_status, hostname = commands.getstatusoutput("hostname | cut -d '.' -f1")
    sriov_state_status, sriov_state = commands.getstatusoutput(
        "ip l | grep \"${%s}:\" | sed 's/^.*state //g' | awk '{print ${%s}}'  |  tr '[a-z]' '[A-Z]' " % (
            eth_name, eth_name))
    if os.access("/var/cmcc-la/data/sriov_fault_raised.{}".format(eth_name), os.F_OK) and (
            "X{}".format(sriov_state) == "XUP"):
        print ("clear alarm {}".format(eth_name))
        # clear alarm
        # watchmen部分先空着
        create_event_host_failed_clear(region, hostname, eth_name)
        commands.getstatusoutput("rm -rf /var/cmcc-la/data/sriov_fault_raised.{}".format(eth_name))
    elif os.access("/var/cmcc-la/data/sriov_fault_raised.{}".format(eth_name), os.F_OK) == False and (
            "X{}".format(sriov_state) == "XDOWN"):
        print("raise alarm {}".format(eth_name))
        # raise alarm
        # watchmen部分先空着
        create_event_host_failed_raise(region, hostname, eth_name)
        commands.getstatusoutput("touch /var/cmcc-la/data/sriov_fault_raised.{}".format(eth_name))
    else:
        return


def list_hypervisor():
    pass


def create_event_host_failed_raise(region, host_name, eth_name):
    source = "Region=%s,CeeFunction=1,Node=%s,Network=SR-IOV,Aggregator=sriov,EthernetPort=%s" % (
    region, host_name, eth_name)
    event = FmEvent(
        True,
        str(source),  # -src
        193,  # -ma
        2031681,  # -mi
        # enums.FM_ACTIVE_SEVERITY.MINOR,
        enums.FM_ACTIVE_SEVERITY.MAJOR,  # -s
        enums.FM_EVENT_TYPE.communicationsAlarm,  # -e
        # enums.FM_PROBABLE_CAUSE.m3100ReplaceableUnitProblem,
        enums.FM_PROBABLE_CAUSE.m3100LossOfSignal,  # -p
        "Ethernet Port Fault",  # -sp 如果后面还有-t的值,就','下一行,然后在""里写值即可
        "Network=SR-IOV,Aggregator=sriov,EthernetPort=${}".format(eth_name))  # -t
    EventSender().create_new_fm_event(event)


def create_event_host_failed_clear(region, host_name, eth_name):
    source = "Region=%s,CeeFunction=1,Node=%s,Network=SR-IOV,Aggregator=sriov,EthernetPort=%s" % (
    region, host_name, eth_name)
    event = FmEvent(
        True,
        str(source),  # -src
        193,  # -ma
        2031681,  # -mi
        # enums.FM_ACTIVE_SEVERITY.MINOR,
        enums.FM_ACTIVE_SEVERITY.CLEARED,  # -s
        enums.FM_EVENT_TYPE.communicationsAlarm,  # -e
        # enums.FM_PROBABLE_CAUSE.m3100ReplaceableUnitProblem,
        enums.FM_PROBABLE_CAUSE.m3100LossOfSignal,  # -p
        "Ethernet Port Fault",  # -sp 如果后面还有-t的值,就','下一行,然后在""里写值即可
        "Network=SR-IOV,Aggregator=sriov,EthernetPort=${}".format(eth_name))  # -t
    EventSender().create_new_fm_event(event)


def main():
    while True:
        status, output = commands.getstatusoutput("ovs-vsctl show | grep dpdk | grep error >/dev/null")
        sriov_1_status, sriov_1 = commands.getstatusoutput(
            "ip l | grep -B 2 vf | grep eth | grep state | head -1 | awk -F\":\" '{print $2}' | tr -d ' '")
        sriov_2_status, sriov_2 = commands.getstatusoutput(
            "ip l | grep -B 2 vf | grep eth | grep state | tail -1 | awk -F\":\" '{print $2}' | tr -d ' '")
        time.sleep(1)
        if status == 0:
            monitor_sriov_port(sriov_1)
            monitor_sriov_port(sriov_2)
        else:
            return


if __name__ == '__main__':
    main()
