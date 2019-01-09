import libvirt
import time
import threading
import logging
import logging.config
from libvirt_utils import libvirt_utils
from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender
from oslo_config import cfg

CONF = cfg.CONF
CONF.import_opt('region_name', 'watchmen_conf', 'DEFAULT')
region = CONF.DEFAULT.region_name
logger = logging.getLogger("libvirt_log")

def watchmenAlarm():
    evnet_sender = EventSender()
    source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
        region, '689c319ac7a14aca86312c3e1036b275', '1693537ff-98f4-4e5b-b425-a5075189fd37')
    event = FmEvent(True, source_one, 193, 2032696, enums.FM_ACTIVE_SEVERITY.CRITICAL, enums.FM_EVENT_TYPE.communicationsAlarm,
                    enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                    "Virtual Machine OS Fault",
                    None,
                    "VM %s(%s)" % ('test_vm_02', '1693537f-98f4-4e5b-b425-a5075189fd37'))
    evnet_sender.create_new_fm_event(event)

if __name__ == '__main__':
    watchmenAlarm()


