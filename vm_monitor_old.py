# coding:utf-8
import sys
import time
import commands
import os
import copy

from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSende


def main():
    SCRIPTS_DIR = "/var/cmcc-la/scripts"
    DATA_DIR = "/var/cmcc-la/data"
    vm_last_status_file = "%s/vm_last_status.txt" % (DATA_DIR)
    region_status, region = commands.getstatusoutput(
        "grep \"region_name\" /etc/watchmen/watchmen-producer.conf | cut -d\"=\" -f2")

    # if no such source, the nova list will report error that must provide a user name or user id
    # commands.getstatusoutput("source /var/cmcc-la/data/openrc")
    commands.getstatusoutput("source /root/openrc")

    if os.access("{}".format(vm_last_status_file), os.F_OK) == False:
        # create the vm status file
        commands.getstatusoutput("nova list --all 2>/dev/null | grep ^\"|\" | grep -v ID | while read line;   do    vm_uuid=`echo \"$line\" | awk -F\"|\" '{print $2}' | tr -d ' '`;    vm_name=`echo \"$line\" | awk -F\"|\" '{print $3}' | tr -d ' ' `;    vm_last_status=`echo \"$line\" | awk -F\"|\" '{print $5}' | tr -d ' ' `;    echo \"$vm_name,$vm_uuid,$vm_last_status\" >> $%s;   done"%(vm_last_status_file))

    while True:
        commands.getstatusoutput("cp -p ${%s} ${%s}.bak"%(vm_last_status_file,vm_last_status_file))
        nova_list_status, nova_list =commands.getstatusoutput("nova list --all 2>/dev/null | grep ^\"|\" | grep -v ID")
        if nova_list_status !=0:
            continue
            nova_list_per=nova_list.split("\n")
            for i in nova_list_per:
                b = i.split("|")
                vm_uuid = b[1]
                vm_uuid_split = vm_uuid.split(" ")
                vm_uuid_rel = vm_uuid_split[1]
                vm_name = b[2]
                vm_name_split = vm_name.split(" ")
                vm_name_rel = vm_name_split[1]
                vm_curr_status = b[4]
                vm_curr_status_split = vm_curr_status.split(" ")
                vm_curr_status_rel = vm_curr_status_split[1]
                #vm_last_status_file = vm_name_rel + ',' + vm_uuid_rel + ',' + vm_last_status_rel
                tenant_id =b[3]
                tenant_id_split = tenant_id.split(" ")
                tenant_id_rel = tenant_id_split[1]
                vm_last_status = commands.getstatusoutput("cat ${%s} | grep %s | awk -F, '{print $3}'"%(vm_last_status_file,vm_uuid_rel))
                status_changed = ""


if __name__ == '__main__':
    main()
