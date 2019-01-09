from watchmen.common import enums
from watchmen.common.fmevent import FmEvent
from watchmen.producer.eventsender import EventSender
from oslo_config import cfg

CONF = cfg.CONF
CONF.import_opt('region_name', 'watchmen_conf', 'DEFAULT')
region = CONF.DEFAULT.region_name


def watchmenAlarm():
    evnet_sender = EventSender()
    source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
        region, '689c319ac7a14aca86312c3e1036b275', '1693537ff-98f4-4e5b-b425-a5075189fd37')
    event = FmEvent(True, source_one, 193, 2032707, enums.FM_ACTIVE_SEVERITY.CLEARED, enums.FM_EVENT_TYPE.equipmentAlarm,
                    enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                    "VM External Storage Fault",
                    None,
                    "Pyhsical Storage Network Fault on compute-1209-2")
    evnet_sender.create_new_fm_event(event)
    print 'watchmenalarmend'
if __name__ == '__main__':
    watchmenAlarm()


#报错的信息Region=ITTE-CEE-E2E-R8C,CeeFunction=1,Tenant=689c319ac7a14aca86312c3e1036b275,VM=1693537ff-98f4-4e5b-b425-a5075189fd37