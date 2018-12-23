#coding:utf-8
import commands
import sys
import urllib2
import json

def main():
    if not sys.argv[3]:
        print "Usage: $0 <operation> <vm uuid> <alarm_minor_id> [<time_in_seconds>]"
        print "        "
        print "       operation: value of 'set' or 'clear'"
        print "       time_in_seconds: to adjust <time_in_seconds> ahead for the specified vm"
        print "       alarm_minor_id: alarm minor id to represent the alarm, for example, 2032696 for Virtual Machine OS Fault"
        sys.exit(1)

operation=sys.argv[1]
vm_uuid=sys.argv[2]
minor_id=sys.argv[3]

if "X{}".format(operation) == "Xset":
    time = sys.argv[4]

commands.getstatusoutput("source /root/openrc")


identity_url = 'https://cic.ericsson.se:5000/v2.0'
metering_url = 'http://[fd00::c0a8:2a1c]:8774'

def curl_keystone():
    url = identity_url + '/tokens'
    values = {"auth": {"passwordCredentials": {"username": "admin", "password": "admin"}, "tenantName": "admin"}}
    params = json.dumps(values)
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    req = urllib2.Request(url, params, headers)
    response = urllib2.urlopen(req)
    data = response.read()
    ddata = json.loads(data)
    token = ddata['access']['token']['id']
    return token


def curl_get_kpi_show(vm_uuid):     #需要从调用他的脚本中传这个uuid
    xtoken = curl_keystone()
    url = metering_url + '/v2.1/servers/%s ' % (vm_uuid)
    req = urllib2.Request(url)
    req.add_header('X-Auth-Token', xtoken)
    response = urllib2.urlopen(req)
    data = response.read()
    ddata = json.loads(data)
    return ddata

#由于暂时没有环境校准,暂时先用命令行的形式写

compute_status,compute = commands.getstatusoutput("nova show %s | grep OS-EXT-SRV-ATTR:hypervisor_hostname  | awk '{print $4}'"%(vm_uuid))

if "X{}".format(operation) == "Xset":   #原作者写错了吗
    time = sys.argv[4]
    commands.getstatusoutput("ssh -i /var/cmcc-la/data/id_rsa.fuel -o StrictHostKeyChecking=no %s \"sed -i \"/^%s/d\" /var/cmcc-la/data/libvirt-event-time.conf; echo '%s %s %s' >>/var/cmcc-la/data/libvirt-event-time.conf\" 2>/dev/null"%(compute,vm_uuid,vm_uuid,minor_id,time))

elif "X{}".format(operation) == "Xclear":
    commands.getstatusoutput("ssh -i /var/cmcc-la/data/id_rsa.fuel -o StrictHostKeyChecking=no %s \"sed -i \"/^%s/d\" /var/cmcc-la/data/libvirt-event-time.conf\" 2>/dev/null"%(compute,vm_uuid))

if __name__ == '__main__':
    main()