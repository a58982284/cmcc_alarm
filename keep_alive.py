# coding:utf-8
import sys
import time
import commands

from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender


def main():
    vm_uuid = sys.argv[1]
    region_status, region = commands.getstatusoutput(
        "grep \"region_name\" /etc/watchmen/watchmen-producer.conf | cut -d\"=\" -f2")
    count = 0
    # commands.getstatusoutput("source /var/cmcc-la/data/openrc")
    commands.getstatusoutput("source /root/openrc")
    # get curr status
    vm_curr_status_num, vm_curr_status = commands.getstatusoutput(
        "nova list --all-tenants --fields status | grep %s | awk -F\"|\" '{print $3}' | tr -d ' '" % (vm_uuid))

    if "X{}".format(vm_curr_status) == "XSHUTOFF":
        print "start vm to keep it alive"
        count = 0
        nova_start_status, nova_start = commands.getstatusoutput("nova start {}".format(vm_uuid))
        retValue = nova_start_status
        count += 1
        while count <= 3 and retValue != 0:
            nova_start_status, nova_start = commands.getstatusoutput("nova start {}".format(vm_uuid))
            retValue = nova_start_status
            count = count + 1
            time.sleep(5)
    elif "X{}".format(vm_curr_status) == "XERROR":
        print "restore vm to keep it alive"
        time.sleep(50)
        count = 0
        nova_start_status, nova_start = commands.getstatusoutput("nova  reset-state --active {}".format(vm_uuid))
        retValue = nova_start_status
        count += 1
        while count <= 2 and retValue != 0:
            nova_start_status, nova_start = commands.getstatusoutput("nova  reset-state --active {}".format(vm_uuid))
            retValue = nova_start_status
            count += 1
            time.sleep(5)

        if retValue != 0:
            # restore failed, generate alarm
            print "restore failed , raise event"
            tenant_uuid_status, tenant_uuid = commands.getstatusoutput(
                "nova list --all-tenants --fields tenant_id | grep fb5b124a-8bd2-4faf-b50b-64ca64fe5c78 | awk -F\"|\" '{print $3}' | tr -d ' '")
            evnet_sender = EventSender()
            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_uuid, vm_uuid)
            event = FmEvent(
                True,
                source_one,
                193,
                2032702,
                enums.FM_ACTIVE_SEVERITY.WARNING,
                enums.FM_EVENT_TYPE.other,
                enums.FM_PROBABLE_CAUSE.enums.FM_PROBABLE_CAUSE.m3100LossOfSignal,
                "VM Restore Failed",
            )
            evnet_sender.create_new_fm_event(event)

            '''
            restore_failed_status, restore_failed = commands.getstatusoutput(
                "/etc/ceesi/scripts/mysql_create_event.sh create-event -sl -src Region=%s,CeeFunction=1,Tenant=%s,VM=%s -ma 193 -mi 2032702 -s WARNING -e other -p m3100Indeterminate   -sp \"VM Restore Failed\"" % (
                    region, tenant_uuid, vm_uuid))
            print(restore_failed)
            print"/etc/ceesi/scripts/mysql_create_event.sh create-event -sl -src Region=$region,CeeFunction=1,Tenant=$tenant_uuid,VM=$vm_uuid -ma 193 -mi 2032702 -s WARNING -e other -p m3100Indeterminate   -sp \"VM Restore Failed\""
            '''


if __name__ == '__main__':
    main()
