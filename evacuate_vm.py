# coding:utf-8
import sys
import time
import commands


def main(a):
    vm_uuid = a
    time.sleep(30)
    # commands.getstatusoutput("source /var/cmcc-la/data/openrc")
    commands.getstatusoutput("source /root/openrc")
    original_host_status, original_host = commands.getstatusoutput(
        "nova show %s | grep hypervisor_hostname | awk -F\"|\" '{print $3}' | tr -d ' '" % (vm_uuid))
    ping_status, ping_output = commands.getstatusoutput("ping -c 1 %s" % (original_host))
    while ping_status == 0:
        time.sleep(10)
        commands.getstatusoutput("ping -c 1 %s" % (original_host))

    count = 0
    while count < 3:
        commands.getstatusoutput("ping -c 1 %s" % (original_host))
        if ping_status != 0:
            count += 1
            time.sleep(5)

    commands.getstatusoutput("nova evacuate %s"%(vm_uuid))
    #print("nova evacuate simulate")
    print("%s had been evacuated" % (vm_uuid))


if __name__ == '__main__':
    main()
