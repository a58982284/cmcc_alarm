#coding:utf-8
from ktoken import ktoken
from endpoints import endpoints
import json
import urllib2

def get_active_alarm_list():
    token = ktoken().get_token()
    ceilometer_auth_url = endpoints('watchmen').get_endpoint()
    url = ceilometer_auth_url + '/active_alarm_list/sort_by/sequence_no/sort_order/asc/page_number/0/page_size/1000'
    req = urllib2.Request(url)
    req.add_header('X-Auth-Token', token)
    req.add_header('X-Tenant-Name', 'admin')
    response = urllib2.urlopen(req)
    print json.loads(response.read())['active_alarm_list']
    #return json.loads(response.read())['active_alarm_list']

'''
[{u'major_type': 193, u'last_event_time': u'2018-12-27 05:36:28+00:00', u'event_type': 4, u'additional_text': u'On node cic-2 Cinder Service has been stopped.', u'sequence_no': 1, u'active_severity': 4, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=cic-2,Service=Cinder Service', u'specific_problem': u'Service Permanently Stopped', u'is_stateful': True, u'minor_type': 2031715, u'probable_cause': 100545, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2018-12-27 05:36:31+00:00', u'event_type': 1, u'additional_text': u'NTP error', u'sequence_no': 2, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-3,UpstreamNTPServerConnection=1', u'specific_problem': u'NTP Stratum Level Failure', u'is_stateful': True, u'minor_type': 2031708, u'probable_cause': 70, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2018-12-27 05:36:31+00:00', u'event_type': 1, u'additional_text': u'NTP error', u'sequence_no': 4, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-4,UpstreamNTPServerConnection=1', u'specific_problem': u'NTP Stratum Level Failure', u'is_stateful': True, u'minor_type': 2031708, u'probable_cause': 70, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2018-12-27 05:36:31+00:00', u'event_type': 1, u'additional_text': u'NTP error', u'sequence_no': 6, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-2,UpstreamNTPServerConnection=1', u'specific_problem': u'NTP Stratum Level Failure', u'is_stateful': True, u'minor_type': 2031708, u'probable_cause': 70, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2018-12-27 05:36:31+00:00', u'event_type': 4, u'additional_text': u'On node cic-3 Cinder Service has been stopped.', u'sequence_no': 8, u'active_severity': 4, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=cic-3,Service=Cinder Service', u'specific_problem': u'Service Permanently Stopped', u'is_stateful': True, u'minor_type': 2031715, u'probable_cause': 100545, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2018-12-27 05:37:32+00:00', u'event_type': 4, u'additional_text': u'On node cic-1 Cinder Service has been stopped.', u'sequence_no': 14, u'active_severity': 4, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=cic-1,Service=Cinder Service', u'specific_problem': u'Service Permanently Stopped', u'is_stateful': True, u'minor_type': 2031715, u'probable_cause': 100545, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2019-01-07 09:00:02+00:00', u'event_type': 1, u'additional_text': u'Core dump file /var/log/crash/cores/core.compute-1209-4.domain.tld.1546159983.rs:send_to_aggr.747.gz generated.', u'sequence_no': 4267, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-4,CoreDump=1546159983.rs:send_to_aggr.747', u'specific_problem': u'Core Dump Generated', u'is_stateful': True, u'minor_type': 2031713, u'probable_cause': 0, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2019-01-07 09:00:02+00:00', u'event_type': 1, u'additional_text': u'Core dump file /var/log/crash/cores/core.compute-1209-4.domain.tld.1546165469.rs:send_to_aggr.750.gz generated.', u'sequence_no': 4268, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-4,CoreDump=1546165469.rs:send_to_aggr.750', u'specific_problem': u'Core Dump Generated', u'is_stateful': True, u'minor_type': 2031713, u'probable_cause': 0, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2019-01-08 15:15:37+00:00', u'event_type': 1, u'additional_text': u'None', u'sequence_no': 4425, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Tenant=87772029bed54fb0b36bdb966b6cbd1e,VM=instance-0000000d', u'specific_problem': u'VM Unavailable', u'is_stateful': True, u'minor_type': 2031702, u'probable_cause': 165, u'additional_info': u'test watchmen api'}, {u'major_type': 193, u'last_event_time': u'2019-01-09 02:25:30+00:00', u'event_type': 1, u'additional_text': u'NTP error', u'sequence_no': 4498, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-4,UpstreamNTPServerConnection=1', u'specific_problem': u'NTP Upstream Server Failure', u'is_stateful': True, u'minor_type': 2031709, u'probable_cause': 70, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2019-01-09 02:40:30+00:00', u'event_type': 1, u'additional_text': u'NTP error', u'sequence_no': 4506, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-2,UpstreamNTPServerConnection=1', u'specific_problem': u'NTP Upstream Server Failure', u'is_stateful': True, u'minor_type': 2031709, u'probable_cause': 70, u'additional_info': u'None'}, {u'major_type': 193, u'last_event_time': u'2019-01-09 02:42:10+00:00', u'event_type': 1, u'additional_text': u'NTP error', u'sequence_no': 4507, u'active_severity': 5, u'source': u'Region=ITTE-CEE-E2E-R7C,CeeFunction=1,Node=compute-1209-3,UpstreamNTPServerConnection=1', u'specific_problem': u'NTP Upstream Server Failure', u'is_stateful': True, u'minor_type': 2031709, u'probable_cause': 70, u'additional_info': u'None'}]


'''



if __name__ == '__main__':
    get_active_alarm_list()