#coding:utf-8
from subprocess import call
import commands
def check_node_status():
    hostname_status, hostname = commands.getstatusoutput("hostname")
    status,output = commands.getstatusoutput("crm_mon -1 >/dev/null")
    if status !=0:
        return 0
    else:
        status, master_cluster_node = commands.getstatusoutput("crm_mon -1 | grep -i \"Current DC\" | sed 's/Current DC://g' | awk '{print $1}'")
    if master_cluster_node == hostname:
        return 2
    else:
        return 1




def main():
    check_node_status()
    #print "echo is {}" .format(check_node_status())
    print check_node_status()

if __name__ == '__main__':
    main()