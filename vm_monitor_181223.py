# coding:utf-8
import sys
import time
import commands
import json
import urllib2
import keep_alive
import evacuate_vm
import MySQLdb
import yaml
from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender

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


def curl_get_kpi():
    xtoken = curl_keystone()
    url = metering_url + '/v2.1/servers/detail?all_tenants=1 '
    req = urllib2.Request(url)
    req.add_header('X-Auth-Token', xtoken)
    response = urllib2.urlopen(req)
    data = response.read()
    ddata = json.loads(data)
    return ddata


def curl_get_kpi_show(vm_uuid):
    xtoken = curl_keystone()
    url = metering_url + '/v2.1/servers/%s ' % (vm_uuid)
    req = urllib2.Request(url)
    req.add_header('X-Auth-Token', xtoken)
    response = urllib2.urlopen(req)
    data = response.read()
    ddata = json.loads(data)
    return ddata


def main():
    SCRIPTS_DIR = "/var/cmcc-la/scripts"
    region_status, region = commands.getstatusoutput(
        "grep \"region_name\" /etc/watchmen/watchmen-producer.conf | cut -d\"=\" -f2")
    commands.getstatusoutput("source /root/openrc")

    res = curl_get_kpi()
    res = res["servers"]
    tenant_id = []  # list have same value,so use tenant_id[0]

    mysql_root_password = get_mysql_password()
    mysql_vip = "192.168.42.28"
    db = MySQLdb.connect(mysql_vip, "root", mysql_root_password)
    cursor = db.cursor()
    create_dase_sql = """create database if not exists om_datafree;"""
    cursor.execute(create_dase_sql)
    use_base_sql = """use om_datafree;"""
    cursor.execute(use_base_sql)
    create_table_sql = """create table if not exists vm_monitor (vm_uuid varchar(128) not null unique, vm_status varchar(32)) ENGINE=InnoDB;"""
    cursor.execute(create_table_sql)
    a = {}
    for i in res:
        vm_uuid = str(i.get('id'))
        vm_last_status = i.get('status')
        tenant_id_vm = i.get('tenant_id')
        tenant_id.append(tenant_id_vm)
        a[vm_uuid] = vm_last_status
        insert_sql = """insert ignore into vm_monitor values(\'%s\',\'%s\');""" % (vm_uuid, vm_last_status)
        cursor.execute(insert_sql)
        db.commit()
    db.close()

    while True:
        res_two = curl_get_kpi()
        res_two = res_two["servers"]
        b = {}
        for j in res_two:
            vm_uuid = str(j.get('id'))
            vm_curr_status = j.get('status')
            b[vm_uuid] = vm_curr_status
            dict4 = dict.fromkeys([x for x in b if x not in a])
            if dict4 != {}:
                for key_4 in dict4:
                    print('%s:%s added to nova' % (time.ctime(), key_4))
            dict3 = dict.fromkeys([x for x in a if x in b and a[x] != b[x]])
            if dict3 != {}:
                for k in dict3:
                    if a[k] == "ACTIVE" and b[k] == "ERROR":
                        print('raise event -to error %s' % k)
                        evnet_sender = EventSender()
                        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                        event = FmEvent(True, source_one, 193, 2032692, enums.FM_ACTIVE_SEVERITY.CRITICAL,
                                        enums.FM_EVENT_TYPE.equipmentAlarm,
                                        enums.FM_PROBABLE_CAUSE.enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                        "VM status became error", None, "VM %s has changed to status error" % (k))
                        evnet_sender.create_new_fm_event(event)
                        res = curl_get_kpi_show(k)
                        res = res["servers"]
                        for i in res:
                            metadata = i.get('metadata', '')
                            if metadata != '':
                                retValue_status, retValue = commands.getstatusoutput(
                                    "echo %s | grep \"Auto_Restore:true\"" % (k))
                                if retValue:
                                    keep_alive.main(k)  # restore vm
                    if a[k] == "ACTIVE" and b[k] == "SHUTOFF":
                        print('raise event -to shutoff %s' % k)
                        evnet_sender2 = EventSender()
                        source_two = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                        event2 = FmEvent(True, source_two, 193, 2032693, enums.FM_ACTIVE_SEVERITY.CRITICAL,
                                         enums.FM_EVENT_TYPE.equipmentAlarm,
                                         enums.FM_PROBABLE_CAUSE.enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                         "VM status became shutoff", None, "VM %s has changed to status shutoff" % (k))
                        evnet_sender2.create_new_fm_event(event2)
                        res = curl_get_kpi_show(k)
                        res = res["servers"]
                        for i in res:
                            metadata = i.get('metadata', '')
                            if metadata != '':
                                keep_Alive_status, keep_Alive1 = commands.getstatusoutput(
                                    "echo %s | grep \"Keep_Alive:true\"" % (metadata))
                                # migration_status, migration = commands.getstatusoutput(
                                #     "echo %s | grep \"Alive_Policy:migration\"" % (metadata))
                                # evacuation_status, evacuation = commands.getstatusoutput(
                                #     "echo %s | grep \"Alive_Policy:evacuation\"" % (metadata))
                                if keep_Alive1:
                                    # migrate and keep alive
                                    keep_alive.main(k)
                                # elif keep_Alive1 and evacuation:
                                #     # evacuate the vm for a DOWN host
                                #     evacuate_vm.main(k)
                                # elif keep_Alive1:
                                #     # keep alive
                                #     keep_alive.main(k)
                    if a[k] == "ERROR" and b[k] == "ACTIVE":
                        print('clear event -error %s' % k)
                        evnet_sender3 = EventSender()
                        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                        event3 = FmEvent(True, source_one, 193, 2032692, enums.FM_ACTIVE_SEVERITY.CLEARED,
                                         enums.FM_EVENT_TYPE.equipmentAlarm,
                                         enums.FM_PROBABLE_CAUSE.enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                         "VM status became ACTIVE", None, "VM %s has changed to status ACTIVE" % (k))
                        evnet_sender3.create_new_fm_event(event3)
                    if a[k] == "SHUTOFF" and b[k] == "ACTIVE":
                        print('clear event - shutoff %s' % k)
                        evnet_sender4 = EventSender()
                        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                        event4 = FmEvent(True, source_one, 193, 2032692, enums.FM_ACTIVE_SEVERITY.CLEARED,
                                         enums.FM_EVENT_TYPE.equipmentAlarm,
                                         enums.FM_PROBABLE_CAUSE.enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                         "VM status became ACTIVE", None, "VM %s has changed to status ACTIVE" % (k))
                        evnet_sender4.create_new_fm_event(event4)
            if cmp(a, b) != 0:
                mysql_root_password = get_mysql_password()
                mysql_vip = "192.168.42.28"
                db = MySQLdb.connect(mysql_vip, "root", mysql_root_password)
                cursor = db.cursor()
                use_base_sql = """use om_datafree;"""
                cursor.execute(use_base_sql)
                update_sql = """update vm_monitor set vm_status=\'%s\' where vm_uuid=\'%s\';""" % (
                    vm_curr_status, vm_uuid)
                cursor.execute(update_sql)
                db.commit()
                db.close()
        a = b


def get_mysql_password():
    with open('/etc/astute.yaml', 'r') as f:
        y = yaml.load(f)
    return y['mysql']['root_password']


if __name__ == '__main__':
    main()
    time.sleep(1)
