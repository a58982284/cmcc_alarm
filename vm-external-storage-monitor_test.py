# coding:utf-8
from ktoken import ktoken
from endpoints import endpoints
import json
import urllib2
from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender
from oslo_config import cfg
import time
import threading
from watchmen.common.fmevent import FmEvent

CONF = cfg.CONF
CONF.import_opt('region_name', 'watchmen_conf', 'DEFAULT')
region = CONF.DEFAULT.region_name


class generate_compute_instance_with_volume(object):

    def __init__(self):
        self.token = ktoken()
        self.nova_auth_url = endpoints('nova').get_endpoint()
        self.cinder_endpoint = endpoints('cinder').get_endpoint()
        # print self.cinder_endpoint      #http://192.168.42.28:8776/v1/%(tenant_id)s
        self.nova_last_cache = []
        self.last_cache = []
        #self.interval= 60.0

    def nova_list(self):
        token = self.token.get_token()
        url = self.nova_auth_url + '/servers/detail?all_tenants=1'
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        # print '--------------novaliststart--------------'
        nova_list_json = json.loads(response.read())
        # print nova_list_json
        # print '--------------novalistend--------------'
        return nova_list_json

    def get_nova_list(self):        #timmer
        res = self.nova_list()
        res = res["servers"]
        for item_nova in res:
            vm_uuid = str(item_nova.get('id'))
            tenant_id = item_nova.get('tenant_id')
            compute_domain = item_nova.get("OS-EXT-SRV-ATTR:host")
            compute = compute_domain.split('.')[0]
            cache = {'vm_uuid': vm_uuid, 'compute': compute, 'tenant_id': tenant_id}
            self.nova_last_cache.append(cache)
        print 'get_nova_list函数得到的是'
        print self.nova_last_cache
        return self.nova_last_cache

    '''
        [
    {
        'compute': u'compute-1209-2',
        'tenant_id': u'689c319ac7a14aca86312c3e1036b275',
        'vm_uuid': 'f092ff4d-feb6-4741-8a56-f882981abb5d'
    },
    {
        'compute': u'compute-1209-2',
        'tenant_id': u'689c319ac7a14aca86312c3e1036b275',
        'vm_uuid': '1693537f-98f4-4e5b-b425-a5075189fd37'
    },
    {
        'compute': u'compute-1209-2',
        'tenant_id': u'689c319ac7a14aca86312c3e1036b275',
        'vm_uuid': '0764feba-09b5-43c4-8279-f9d3fec35ef1'
    }
]
        '''

    def request_cinder(self):
        token = self.token.get_token()  # 和nova list一样
        # tenant_id = self.get_tenant_id()
        tenant_id = self.nova_last_cache[0].get('tenant_id')
        # url = self.cinder_endpoint + '/volumes/detail'%(tenant_id)  #http://192.168.42.28:8776/v1/%(tenant_id)s/volumes/detail    http://192.168.42.28:8776/v2/689c319ac7a14aca86312c3e1036b275/volumes/detail
        url = self.cinder_endpoint.split('%')[
                  0] + tenant_id + '/volumes/detail'  # http://192.168.42.28:8776/v1/689c319ac7a14aca86312c3e1036b275/volumes/detail
        # print url
        headers = {'Content-Type': 'application/json', 'X-Auth-Token': token}
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        response_json=json.loads(response.read())
        print 'request_cinder函数得到的是'
        print response_json
        print '设置的假数据并给cinder_res返回假数据'
        false_data = {
"volumes":[
{
"migration_status":'null',
"attachments":[
{
"server_id":"1693537f-98f4-4e5b-b425-a5075189fd37", #cd15e1c0-e03e-41cf-94cf-934722b1233b  1693537ff-98f4-4e5b-b425-a5075189fd37
"attachment_id":"a8849d64-a981-474e-aa1b-054d1908322a",
"attached_at":"2018-09-06T09:58:23.000000",
"host_name":'null',
"volume_id":"75cf5bad-48b6-471f-a40f-fbcb1eb436c8",
"device":"/dev/vda",
"id":"75cf5bad-48b6-471f-a40f-fbcb1eb436c8"
}
],
"links":[
{
"href":"http://[2100::4848:73]:8776/v2/d6701fb237e946719667c06cf61c7b21/volumes/75cf5bad-48b6-471f-a40f-fbcb1eb436c8",
"rel":"self"
},
{
"href":"http://[2100::4848:73]:8776/d6701fb237e946719667c06cf61c7b21/volumes/75cf5bad-48b6-471f-a40f-fbcb1eb436c8",
"rel":"bookmark"
}
],
"availability_zone":"nova",
"os-vol-host-attr:host":"cinder@ceph_volumes_az_2#CEPH_AZ_2",
"encrypted":'false',
"updated_at":"2018-09-06T09:58:23.000000",
"replication_status":"disabled",
"snapshot_id":'null',
"id":"75cf5bad-48b6-471f-a40f-fbcb1eb436c8",
"size":80,
"user_id":"288b67a8179d4d39b980fe7566e1fb57",
"os-vol-tenant-attr:tenant_id":"d6701fb237e946719667c06cf61c7b21",
"os-vol-mig-status-attr:migstat":'null',
"metadata":{
"readonly":"False",
"attached_mode":"rw"
},
"status":"in-use",
"volume_image_metadata":{
"checksum":"9391c15bc8dc42f6d5931e124da725d6",
"min_ram":"0",
"disk_format":"qcow2",
"image_name":"centos_with_i40evf",
"image_id":"12778beb-d82c-4f52-9984-b72285d7c9bb",
"container_format":"bare",
"min_disk":"0",
"size":"938016768"
},
"description":"",
"multiattach":'false',
"source_volid":'null',
"consistencygroup_id":'null',
"os-vol-mig-status-attr:name_id":'null',
"name":"",
"bootable":"true",
"created_at":"2018-09-06T09:57:51.000000",
"volume_type":'null'
},
]
}
        return false_data       #假数据,记得注销掉
        #return response_json
        #return json.loads(response.read())  # {u'volumes': []}

    def cinder_res(self):           #这个需要在main里运行,加timer
        cinder_res = self.request_cinder()
        print'cinder_res得到的request_cinder返回值(现在是假数据)'
        print cinder_res
        res = cinder_res.get('volumes')
        print 'res是'
        print res
        for items in res:
            item = items.get('attachments')
            print 'attachments是(server_id在里面)'
            print item
            status = items.get('status')  # in-use
            print 'status是'
            print status
            if status == "in-use":
                print 'status确实等于in-use'
                for redis_item in item:
                    result = redis_item.get('server_id')  # 20b75a57-37ec-43d3-8efc-2aabce235877
                    print 'server_id是'
                    print result
                    for nova_cache in self.nova_last_cache:
                        print 'nova_cache的uuid是'
                        print nova_cache.get('vm_uuid')
                        if nova_cache.get('vm_uuid') == result:
                            print 'nova_cache的uuid和server_id相等'
                            self.last_cache.append(nova_cache)
        print 'cinder_res的返回值是'
        print self.last_cache
        return self.last_cache  # $compute $uuid $tenant_id >> $temp_output

    def get_active_alarm_list(self):
        token = ktoken().get_token()
        ceilometer_auth_url = endpoints('watchmen').get_endpoint()
        url = ceilometer_auth_url + '/active_alarm_list/sort_by/sequence_no/sort_order/asc/page_number/0/page_size/1000'
        req = urllib2.Request(url)
        req.add_header('X-Auth-Token', token)
        req.add_header('X-Tenant-Name', 'admin')
        response = urllib2.urlopen(req)
        #print 'get_active_alarm_list的返回值是'
        #print response
        # print json.loads(response.read())['active_alarm_list']
        return json.loads(response.read()).get('active_alarm_list')

    def alarm_item(self):
        cache_uuid = []
        res = self.get_active_alarm_list()
        #print '---告警列表返回值---'
        #print res
        for item_cache in self.last_cache:
            cache_vm_uuid = item_cache.get('vm_uuid')
            cache_uuid.append(cache_vm_uuid)  # 把缓存里的uuid形成了一个list
        for item in res:
            if item.get('specific_problem') == "VM External Storage Fault":
                alarm_uuid = item.get('source')
                vm_alarm_uuid = alarm_uuid.split("VM=")[-1]  # 1693537ff-98f4-4e5b-b425-a5075189fd37    #这个是告警列表里的id
                print '----告警列表uuid---'
                print vm_alarm_uuid
                tenant_id_original = alarm_uuid.split("Tenant=")
                tenant_id = tenant_id_original[1].split(',')[0]  #689c319ac7a14aca86312c3e1036b275
                print '---需要清除告警的tenant_id---'
                print tenant_id

                compute_original = item.get('additional_text')
                compute = compute_original.split('on ')[1]  #compute-1209-2
                print '---需要清除告警的compute'
                print compute
                if vm_alarm_uuid not in cache_uuid:  # 如果告警id不在缓存id中,证明现在这个机器正常了(缓存id状态比较新),那么清理告警
                    self.clear_alarm(tenant_id,vm_alarm_uuid,compute)
                    print '已经清除了告警'
                else:
                    return 0
        print'准备触发告警'
        self.raise_alarm()  # 告警

    def raise_alarm(self):
        print'raise_alarm函数得到的缓存是'
        print self.last_cache
        for item_cache in self.last_cache:
            vm_uuid = item_cache.get('vm_uuid')
            tenant_id = item_cache.get('tenant_id')
            compute = item_cache.get('compute')

            evnet_sender = EventSender()
            source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
                region, tenant_id, vm_uuid)
            event = FmEvent(True, str(source_one), 193, 2032707, enums.FM_ACTIVE_SEVERITY.MAJOR,
                            enums.FM_EVENT_TYPE.equipmentAlarm,
                            enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                            "VM External Storage Fault",
                            None,
                            str("Pyhsical Storage Network Fault on %s"%(compute))
                            )
            evnet_sender.create_new_fm_event(event)
        print '可能的告警已经结束'

    def clear_alarm(self,tenant_id,vm_uuid,compute):
        print 'clear_alarm函数得到的tenant_id'
        print tenant_id
        print 'clear_alarm函数得到的vm_uuid'
        print vm_uuid
        print 'clear_alarm函数得到的compute'
        print compute
        evnet_sender = EventSender()
        print 'clear_alarm函数得到的region'
        print region
        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
            region, tenant_id, vm_uuid)
        event = FmEvent(True, str(source_one), 193, 2032707, enums.FM_ACTIVE_SEVERITY.CLEARED,
                        enums.FM_EVENT_TYPE.equipmentAlarm,
                        enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                        "VM External Storage Fault",
                        None,
                        str("Pyhsical Storage Network Fault on %s" % (compute))
                        )
        evnet_sender.create_new_fm_event(event)

    def launch(self):
        while True:
            self.get_nova_list()
            print 'get_nova_list执行完毕'
            time.sleep(60)
            self.cinder_res()
            print 'cinder_res执行完毕'
            time.sleep(60)
            self.alarm_item()
            time.sleep(1)
            print 'alarm_item执行完毕'

if __name__ == '__main__':
    compute_instance_with_volume = generate_compute_instance_with_volume()
    compute_instance_with_volume.launch()



