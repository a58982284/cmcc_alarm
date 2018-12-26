# coding:utf-8
import threading
import sys
import time
import commands
import json
import urllib2
import MySQLdb
import yaml
import requests
import logging as log
from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender
from kombu import BrokerConnection
from kombu import Exchange
from kombu import Queue
from kombu.mixins import ConsumerMixin
from ktoken import ktoken
from endpoints import endpoints

EXCHANGE_NAME = "nova"
ROUTING_KEY = "notifications.info"
QUEUE_NAME = "nova_dump_queue"
BROKER_URI = "amqp://nova:3fwEP0GdHcxOzmk69EM1O4Rq@[fd00::c0a8:3416]:5673//"
#BROKER_URI = "amqp://nova:uoKLyhFwpKoVgn3F2P4ybAdN@192.168.42.24:5673//"

log.basicConfig(stream=sys.stdout, level=log.DEBUG)


class vmMonitor(ConsumerMixin):
    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, consumer, channel):
        exchange = Exchange(EXCHANGE_NAME, type="topic", durable=False)
        queue = Queue(QUEUE_NAME, exchange, routing_key=ROUTING_KEY, durable=False, auto_delete=True, no_ack=True)
        return [consumer(queue, callbacks=[self.on_message])]

    def on_message(self, body, message):
        # SCRIPTS_DIR = "/var/cmcc-la/scripts"
        region_status, region = commands.getstatusoutput(
            "grep \"region_name\" /etc/watchmen/watchmen-producer.conf | cut -d\"=\" -f2")
        commands.getstatusoutput("source /root/openrc")
        res = curl_get_kpi()
        res = res["servers"]
        tenant_id = []
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

        last_cache = {}
        for i in res:
            vm_uuid = str(i.get('id'))
            vm_last_status = i.get('status')
            tenant_id_vm = i.get('tenant_id')
            tenant_id.append(tenant_id_vm)
            last_cache[vm_uuid] = vm_last_status
            insert_sql = """insert ignore into vm_monitor values(\'%s\',\'%s\');""" % (vm_uuid, vm_last_status)
            cursor.execute(insert_sql)
            db.commit()
        db.close()

        while True:
            message = json.loads(body['oslo.message'])  # old def on_message,insert to while
            event_type = message.get('event_type')

            res_two = curl_get_kpi()  # get all vm uuid and status
            res_two = res_two["servers"]
            curr_cache = {}
            for j in res_two:
                vm_uuid = str(j.get('id'))
                vm_curr_status = j.get('status')
                curr_cache[vm_uuid] = vm_curr_status
            dict_del = dict.fromkeys([x for x in last_cache if x not in curr_cache])
            if dict_del != {}:
                for key_uuid in dict_del:
                    print('%s:%s deleted to nova' % (time.ctime(), key_uuid))
                    del_sql = """DELETE FROM vm_monitor where vm_uuid=\'%s\';""" % (key_uuid)
                    mysql_crud(del_sql)

                    if last_cache[key_uuid] == 'ERROR':
                        evnet_sender = EventSender()
                        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], key_uuid)
                        event = FmEvent(True, source_one, 193, 2032692, enums.FM_ACTIVE_SEVERITY.CLEARED,
                                        enums.FM_EVENT_TYPE.equipmentAlarm,
                                        enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                        "VM status became error", None,
                                        "VM %s has changed to status error" % (key_uuid))
                        evnet_sender.create_new_fm_event(event)
                    if last_cache[key_uuid] == 'SHUTOFF':
                        evnet_sender = EventSender()
                        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], key_uuid)
                        event = FmEvent(True, source_one, 193, 2032693, enums.FM_ACTIVE_SEVERITY.CLEARED,
                                        enums.FM_EVENT_TYPE.equipmentAlarm,
                                        enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                        "VM status became shutoff", None,
                                        "VM %s has changed to status shutoff" % (key_uuid))
                        evnet_sender.create_new_fm_event(event)

                dict_add = dict.fromkeys([x for x in curr_cache if x not in last_cache])
                if dict_add != {}:
                    for key_uuid in dict_add:
                        print('%s:%s added to nova' % (time.ctime(), key_uuid))
                dict_abnormal = dict.fromkeys(
                    [x for x in last_cache if x in curr_cache and last_cache[x] != curr_cache[x]])
                if dict_abnormal != {}:
                    for k in dict_abnormal:
                        if last_cache[k] == "ACTIVE" and curr_cache[k] == "ERROR":
                            print('raise event -to error %s' % k)
                            evnet_sender = EventSender()
                            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                            event = FmEvent(True, source_one, 193, 2032692, enums.FM_ACTIVE_SEVERITY.CRITICAL,
                                            enums.FM_EVENT_TYPE.equipmentAlarm,
                                            enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
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
                                        print("restore vm to keep it alive")
                                        keep_alive(k)      #nova reset
                                        time.sleep(50)  # 原脚本睡50
                                        count = 0
                                        while count <= 2 and event_type != 'compute.instance.power_on.end':  # error情况下restore vm,是假数据,因为环境中没有error状态,所以等拿到error状态了再改这个函数
                                            keep_alive(k)
                                            count += 1
                                            time.sleep(5)
                                        if count > 2:
                                            evnet_sender = EventSender()
                                            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
                                                region, tenant_id[0], k)
                                            event = FmEvent(True, source_one, 193, 2032702,
                                                            enums.FM_ACTIVE_SEVERITY.WARNING, enums.FM_EVENT_TYPE.other,
                                                            enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                                            "VM Restore Failed", )
                                            evnet_sender.create_new_fm_event(event)

                        if last_cache[k] == "ACTIVE" and curr_cache[k] == "SHUTOFF":
                            print('raise event -to shutoff %s' % k)
                            evnet_sender = EventSender()
                            source = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                            event = FmEvent(True, source, 193, 2032693, enums.FM_ACTIVE_SEVERITY.CRITICAL,
                                            enums.FM_EVENT_TYPE.equipmentAlarm,
                                            enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                            "VM status became shutoff", None,
                                            "VM %s has changed to status shutoff" % (k))
                            evnet_sender.create_new_fm_event(event)
                            res = curl_get_kpi_show(k)
                            res = res["servers"]
                            for i in res:
                                metadata = i.get('metadata', '')
                                if metadata != '':
                                    retValue_status, retValue = commands.getstatusoutput(
                                        "echo %s | grep \"Keep_Alive:true\"" % (metadata))
                                    if retValue:
                                        print "start vm to keep it alive"
                                        nova_start(k)  # nova start
                                        count = 0
                                        while count <= 2 and event_type != 'compute.instance.power_on.end':
                                            nova_start(k)
                                            count += 1
                                            time.sleep(5)
                                        if count > 2:
                                            evnet_sender = EventSender()
                                            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
                                                region, tenant_id[0], k)
                                            event = FmEvent(True, source_one, 193, 2032702,
                                                            enums.FM_ACTIVE_SEVERITY.WARNING, enums.FM_EVENT_TYPE.other,
                                                            enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                                            "VM Restore Failed", )
                                            evnet_sender.create_new_fm_event(event)

                        if last_cache[k] == "ERROR" and curr_cache[k] == "ACTIVE":
                            print('clear event -error %s' % k)
                            evnet_sender = EventSender()
                            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                            event = FmEvent(True, source_one, 193, 2032692, enums.FM_ACTIVE_SEVERITY.CLEARED,
                                            enums.FM_EVENT_TYPE.equipmentAlarm,
                                            enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                            "VM status became error", None,
                                            "VM %s has changed to status error" % (k))
                            evnet_sender.create_new_fm_event(event)
                        if last_cache[k] == "SHUTOFF" and curr_cache[k] == "ACTIVE":
                            print('clear event - shutoff %s' % k)
                            evnet_sender = EventSender()
                            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_id[0], k)
                            event = FmEvent(True, source_one, 193, 2032693, enums.FM_ACTIVE_SEVERITY.CLEARED,
                                            enums.FM_EVENT_TYPE.equipmentAlarm,
                                            enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                                            "VM status became shutoff", None,
                                            "VM %s has changed to status shutoff" % (k))
                            evnet_sender.create_new_fm_event(event)
                if cmp(last_cache, curr_cache) != 0:
                    update_sql = """update vm_monitor set vm_status=\'%s\' where vm_uuid=\'%s\';""" % (
                        vm_curr_status, vm_uuid)
                    mysql_crud(update_sql)
            last_cache = curr_cache


def nova_start(uuid):
    token = ktoken().get_token()
    ceilometer_auth_url = endpoints('nova').get_endpoint()
    url = ceilometer_auth_url + '/v2.1/servers/%s ' % (uuid)
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    fields = [{
        "os-start": 'null'
    }]
    requests.post(url, data=json.dumps(fields), headers=headers)


def keep_alive(uuid):
    token = ktoken().get_token()
    ceilometer_auth_url = endpoints('nova').get_endpoint()
    url = ceilometer_auth_url + '/v2.1/servers/%s ' % (uuid)
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
    fields = [{
        "os-resetState": {"state": "active"}
    }]
    requests.post(url, data=json.dumps(fields), headers=headers)


def curl_get_kpi():
    token = ktoken().get_token()
    ceilometer_auth_url = endpoints('nova').get_endpoint()
    url = ceilometer_auth_url + '/v2.1/servers/detail?all_tenants=1 '
    req = urllib2.Request(url)
    req.add_header('X-Auth-Token', token)
    response = urllib2.urlopen(req)
    data = response.read()
    data = json.loads(data)
    return data


def curl_get_kpi_show(uuid):
    token = ktoken().get_token()
    ceilometer_auth_url = endpoints('nova').get_endpoint()
    url = ceilometer_auth_url + '/v2.1/servers/%s ' % (uuid)
    req = urllib2.Request(url)
    req.add_header('X-Auth-Token', token)
    response = urllib2.urlopen(req)
    data = response.read()
    data = json.loads(data)
    return data


def get_mysql_password():
    with open('/etc/astute.yaml', 'r') as f:
        y = yaml.load(f)
    return y['mysql']['root_password']


def mysql_crud(statement):
    mysql_root_password = get_mysql_password()
    mysql_vip = "192.168.42.28"
    db = MySQLdb.connect(mysql_vip, "root", mysql_root_password)
    cursor = db.cursor()
    use_base_sql = """use om_datafree;"""
    cursor.execute(use_base_sql)
    insert_sql = """%s""" % (statement)
    cursor.execute(insert_sql)
    db.commit()
    db.close()



if __name__ == '__main__':
    log.info("Connecting to broker {}".format(BROKER_URI))
    with BrokerConnection(BROKER_URI) as connection:
        vmMonitor(connection).run()
