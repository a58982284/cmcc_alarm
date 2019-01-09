import time
import commands
import sys
import os
from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender
from oslo_config import cfg

CONF = cfg.CONF
CONF.import_opt('region_name', 'watchmen_conf', 'DEFAULT')
region = CONF.DEFAULT.region_name
CMCC_LA_DATA_DIR = "/var/cmcc-la/data"
NODE = os.uname()[0].split('.')[0]


class service_supervision(object):
    def __init__(self):
        self.service = sys.argv[1]

    def correct_parameter(self):

        if self.service :
            self.raise_alert(self.service)
        else:
            print "incorrect parameter,please provide the service name to monitor."
            sys.exit(1)

    def raise_alert(self,service):
        output_num = []
        while True:
            output_status, output = commands.getstatusoutput(
                "ps -ef | grep %s | grep -v grep > /dev/null" % (service))
            output_num.append(output)
            if len(output_num)<2:
                print "raise alert"
                evnet_sender = EventSender()
                source_one = "Region=%s,CeeFunction=1,Node=%s,Service=%s" % (region, NODE, service)
                event = FmEvent(
                    False,
                    source_one,
                    193,
                    2031710,
                    enums.FM_ACTIVE_SEVERITY.MAJOR,
                    enums.FM_EVENT_TYPE.other,
                    enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                    "Service stopped",
                    None,
                    "On node:%s service: %s has been stopped." % (NODE, service)
                )
                evnet_sender.create_new_fm_event(event)
                time.sleep(120)
            else:
                time.sleep(1)


if __name__ == '__main__':
    serviceSupervision = service_supervision()
    serviceSupervision.correct_parameter()
