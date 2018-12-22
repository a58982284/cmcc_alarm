#!/usr/bin/env python

import os
import re
import json
import urllib2
import subprocess
import ConfigParser
import threading

identity_url='https://cic.ericsson.se:5000/v2.0'
metering_url='http://[fd00::c0a8:2a1c]:8774'


def curl_keystone():
    url = identity_url+'/tokens'
    values = {"auth":{"passwordCredentials": {"username": "admin", "password": "admin"}, "tenantName": "admin"}}
    params = json.dumps(values)
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    req = urllib2.Request(url, params, headers)
    response = urllib2.urlopen(req)
    data = response.read()
    ddata=json.loads(data)
    token = ddata['access']['token']['id']
    return token


def curl_get_kpi():
    xtoken = curl_keystone()
    url = metering_url + '/v2.1/servers/detail?all_tenants=1'
    req = urllib2.Request(url)
    req.add_header('X-Auth-Token', xtoken)
    response = urllib2.urlopen(req)
    data = response.read()
    ddata=json.loads(data)
    return ddata


if __name__ == '__main__':print curl_get_kpi()
