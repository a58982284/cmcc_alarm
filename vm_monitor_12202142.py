# coding:utf-8
import sys
import time
import commands
import os
import re
import json
import urllib2
import subprocess
import ConfigParser
import threading

from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSende

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


def main():
    SCRIPTS_DIR = "/var/cmcc-la/scripts"
    region_status, region = commands.getstatusoutput(
        "grep \"region_name\" /etc/watchmen/watchmen-producer.conf | cut -d\"=\" -f2")
    commands.getstatusoutput("source /root/openrc")
    # create the vm status file
    res = curl_get_kpi()
    res = res["servers"]
    cache_file = []  # 缓存文件
    cache_status_file = []
    vm_uuid_cache = []
    for i in res:
        vm_uuid = i.get('id', '')
        vm_name = i.get('name', '')
        vm_last_status = i.get('status', '')
        vm_status_file = str(vm_uuid) + ',' + str(vm_name) + ',' + str(vm_last_status)
        cache_file.append(vm_status_file)
        cache_status_file.append(vm_last_status)
        vm_uuid_cache.append(vm_uuid)
    print cache_file
    # 然后需要先判断一下sql中有没有这张表,如果没有的话就创建一张表

    while True:
        res_two = curl_get_kpi()
        res_two = res_two["servers"]
        cache_file_two = []
        cache_status_file_two = []
        vm_uuid_cache_two = []
        vm_last_status_two = []
        for j in res_two:
            vm_uuid = j.get('id','')
            vm_name = j.get('name','')
            vm_curr_status = j.get('status','')
            #vm_last_status = cache_status_file#从缓存里查vm状态 ,是个list

            tenant_id = ""
            vm_status_file_two = str(vm_uuid) + ',' + str(vm_name) + ',' + str(vm_curr_status)
            cache_file_two.append(vm_status_file_two)
            cache_status_file_two.append(vm_curr_status)
            diffent_uuid_list=list(set(vm_uuid_cache_two).difference(set(vm_uuid_cache)))
            if diffent_uuid_list !=[]:    # 如果从缓存中发现差异   #vm_last_status=`cat ${vm_last_status_file} | grep $vm_uuid | awk -F, '{print $3}'
                # new added vm
                print "`date`:%s added to nova"%(vm_name)   #比较差异之后把two中新增的uuid对应的vm_name取出来打印(用mysql)
                vm_uuid_cache = vm_uuid_cache_two   ##校准缓存
                cache_file = cache_file_two #校准缓存
                #然后拿cache_file_two的元素作为基准重新覆盖数据库中的相应表
            elif diffent_uuid_list == []:
                continue
            #diffent_status_list = list(set(vm_uuid_cache_two).difference(set(cache_status_file)))

        #if cache_file != cache_file_two:
            #cache_file = cache_file_two







        #commands.getstatusoutput("cp -p ${%s} ${%s}.bak" % (vm_last_status_file, vm_last_status_file))
        #nova_list_status, nova_list = commands.getstatusoutput("nova list --all 2>/dev/null | grep ^\"|\" | grep -v ID")
        #if nova_list_status != 0:
            #continue

            #nova_list_per = nova_list.split("\n")
            # for i in nova_list_per:
            #     b = i.split("|")
            #     vm_uuid = b[1]
            #     vm_uuid_split = vm_uuid.split(" ")
            #     vm_uuid_rel = vm_uuid_split[1]
            #     vm_name = b[2]
            #     vm_name_split = vm_name.split(" ")
            #     vm_name_rel = vm_name_split[1]
            #     vm_curr_status = b[4]
            #     vm_curr_status_split = vm_curr_status.split(" ")
            #     vm_curr_status_rel = vm_curr_status_split[1]
            #     #vm_last_status_file = vm_name_rel + ',' + vm_uuid_rel + ',' + vm_last_status_rel
            #     tenant_id =b[3]
            #     tenant_id_split = tenant_id.split(" ")
            #     tenant_id_rel = tenant_id_split[1]
            #     vm_last_status = commands.getstatusoutput("cat ${%s} | grep %s | awk -F, '{print $3}'"%(vm_last_status_file,vm_uuid_rel))
            #     status_changed = ""


if __name__ == '__main__':
    main()
