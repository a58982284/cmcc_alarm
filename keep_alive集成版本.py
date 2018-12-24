# coding:utf-8
import time
import commands
import json
import requests
from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender
import sys
import json
import logging as log
from kombu import BrokerConnection
from kombu import Exchange
from kombu import Queue
from kombu.mixins import ConsumerMixin
from ktoken import ktoken
from endpoints import endpoints


EXCHANGE_NAME="nova"
ROUTING_KEY="notifications.info"
QUEUE_NAME="nova_dump_queue"
BROKER_URI="amqp://nova:uoKLyhFwpKoVgn3F2P4ybAdN@192.168.42.24:5673//"

log.basicConfig(stream=sys.stdout, level=log.DEBUG)

class NotificationsDump(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection
        self.ktoken = ktoken.get_token()
        self.endpoints = endpoints
        #return

    def get_consumers(self, consumer, channel):
        exchange = Exchange(EXCHANGE_NAME, type="topic", durable=False)
        queue = Queue(QUEUE_NAME, exchange, routing_key = ROUTING_KEY, durable=False, auto_delete=True, no_ack=True)
        return [ consumer(queue, callbacks = [ self.on_message ]) ]

    def on_message(self, body, message):
        message = json.loads(body['oslo.message'])
        log.info('Body: %r' % message['event_type'])
        log.info('---------------')

    identity_url = 'https://cic.ericsson.se:5000/v2.0'
    metering_url = 'http://[fd00::c0a8:2a1c]:8774'

    def create_sample(self):
        token = ktoken.get_token()

            #self.ceilometer_auth_url = endpoints('ceilometer').get_endpoint()
            #url = self.ceilometer_auth_url+'/v2/meters/'+source
        ceilometer_auth_url = endpoints('nova').get_endpoint()
        #url = metering_url + '/v2.1/servers/%s ' % (vm_uuid)
        url = ceilometer_auth_url + '/v2.1/servers/%s ' %(vm_uuid)
            #mem_value = memory_mb if source == 'hypervisor.memory.total' else memory_mb_used
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
        fields = [{
            "os-start": 'null'
            }]
        requests.post(url, data=json.dumps(fields), headers=headers)





def keep_alive(a):
    vm_uuid = a
    region_status, region = commands.getstatusoutput(
        "grep \"region_name\" /etc/watchmen/watchmen-producer.conf | cut -d\"=\" -f2")
    count = 0
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
                "nova list --all-tenants --fields tenant_id | grep %s | awk -F\"|\" '{print $3}' | tr -d ' '"%(vm_uuid))
            evnet_sender = EventSender()
            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (region, tenant_uuid, vm_uuid)
            event = FmEvent(
                True,
                source_one,
                193,
                2032702,
                enums.FM_ACTIVE_SEVERITY.WARNING,
                enums.FM_EVENT_TYPE.other,
                enums.FM_PROBABLE_CAUSE.enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                "VM Restore Failed",
            )
            evnet_sender.create_new_fm_event(event)


if __name__ == '__main__':
    log.info("Connecting to broker {}".format(BROKER_URI))
    with BrokerConnection(BROKER_URI) as connection:
        NotificationsDump(connection).run()
    keep_alive()
