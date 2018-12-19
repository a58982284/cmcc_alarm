# coding:utf-8
import sys
import time
import commands


def main():
    vm_uuid = sys.argv[1]
    time.sleep(30)
    # commands.getstatusoutput("source /var/cmcc-la/data/openrc")
    commands.getstatusoutput("source /root/openrc")
    commands.getstatusoutput("nova migrate %s" % (vm_uuid))
    ginal_host_status, original_host = commands.getstatusoutput(
        "nova show %s | grep status | grep -v host_status | awk -F \"|\" '{print $3}' | tr -d ' '" % (vm_uuid))
    xvm_status = "X{}".format(original_host)

    while xvm_status != "XVERIFY_RESIZE":
        time.sleep(5)
        commands.getstatusoutput(
            "nova show %s | grep status | grep -v host_status | awk -F \"|\" '{print $3}' | tr -d ' '"%(vm_uuid))

    commands.getstatusoutput("nova resize-confirm {}".format(vm_uuid))
    commands.getstatusoutput("nova start {}".format(vm_uuid))

    print("{} had been migrated and keep alive".format(vm_uuid))


if __name__ == '__main__':
    main()
