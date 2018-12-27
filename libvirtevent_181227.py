# coding:utf-8
import commands
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



class libvirtEvent(object):

    def __init__(self):
        self.SHELL_CHECK_REGION = "grep region_name /etc/watchmen/watchmen-producer.conf | cut -d'=' -f2"
        self.region = CONF.DEFAULT.region_name

    def callback(self, conn, dom, event, detail, opaque):
        print "EVENT: Domain %s(%s) %s %s" % (dom.name(), dom.ID(), event, detail)
        myInstance = dom.name()
        nodeName = libvirt_utils.get_nova_name(myInstance)
        uuid = dom.StringUUID()
        tenant_id = libvirt_utils.get_tenant_id(myInstance)
        logging.config.fileConfig('/var/cmcc-la/conf/libvirtevent_log.conf')
        logger = logging.getLogger("libvirt_log")
        timeStamp = 0
        deltatime = time.time() - timeStamp
        tstime = time.ctime()
        if deltatime > 30 and "instance" in dom.name():
            if event == 4:
                minor_id = 2032696
                timestatus, times = commands.getstatusoutput(
                    "cat /var/cmcc-la/data/libvirt-event-time.conf | grep $uuid | grep $minor_id | awk '{print $3}")
                if times > 0:
                    wa_timestampstatus, wa_timestamp = commands.getstatusoutput(
                        "date -d \"{} second ago\" +%Y-%m-%d\" \"%H:%M:%S.%6N -u".format(times))
                    logger.info("Adjust %s second ahead for %s,%s==>%s" % (times, uuid, tstime, wa_timestamp))
                self.watchmenAlarm(self.region, tenant_id, uuid, nodeName, minor_id, enums.FM_ACTIVE_SEVERITY.CRITICAL,
                                   "Virtual Machine OS Fault")
                logger.error(
                    "watchmen-client create-event -sf -src Region=\"%s\",CeeFunction=\"1\",Tenant=\"%s\",VM=%s -ma 193 -mi 2032696 -s CRITICAL -e communicationsAlarm  -p m3100Indeterminate -sp \"Virtual Machine OS Fault\" -t \"VM %s(%s)\"" % (
                        self.region, tenant_id, uuid, nodeName, uuid))
                logger.error('%s VM %s(%s): Detected Virtual Machine OS Fault,possible reason: kernel panic' % (
                    str(time.ctime()), nodeName, uuid))
                time.sleep(10)
                self.watchmenAlarm(self.region, tenant_id, uuid, nodeName, minor_id, enums.FM_ACTIVE_SEVERITY.CLEARED,
                                   "Virtual Machine OS Fault")
                logger.info(
                    "watchmen-client create-event -sf -src Region=\"%s\",CeeFunction=\"1\",Tenant=\"%s\",VM=%s -ma 193 -mi 2032696 -s CLEARED -e communicationsAlarm  -p m3100Indeterminate -sp \"Virtual Machine OS Fault\" -t \"VM %s(%s)\"" % (
                        self.region, tenant_id, uuid, nodeName, uuid))
                logger.info(
                    '%s VM %s(%s): Detected Virtual Machine OS Fault,possible reason: kernel panic.Cleared watchmen alarm.' % (
                        str(time.ctime()), nodeName, uuid))
            elif event == 5:
                minor_id = 2032697
                self.watchmenAlarm(self.region, tenant_id, uuid, nodeName, minor_id, enums.FM_ACTIVE_SEVERITY.WARNING,
                                   "Virtual Machine Running Fault")
                logger.warning(
                    "watchmen-client create-event -sl -src Region=%s,CeeFunction=\"1\",Tenant=\"%s\",VM=$uuid -ma 193 -mi 2032697 -s WARNING -e communicationsAlarm  -p m3100Indeterminate -sp \"Virtual Machine Running Fault\" -t \"VM %s(%s):%s\"" % (
                        self.region, tenant_id, uuid, nodeName, uuid))
                logger.warning(
                    '%s VM %s(%s): Detected Virtual Machine Running Fault,possible reason: qemu process had been killed or vm been powered off or shutdown abnormal.' % (
                        str(time.ctime()), nodeName, uuid))
        else:
            timeStamp = time.time()
        time.sleep(1)

    def watchmenAlarm(self, region, tenant_id, uuid, nodeName, minor_id, fm_active_severity, sp):
        evnet_sender = EventSender()
        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
            region, tenant_id, uuid)
        event = FmEvent(True, source_one, 193, minor_id, fm_active_severity, enums.FM_EVENT_TYPE.communicationsAlarm,
                        enums.FM_PROBABLE_CAUSE.m3100Indeterminate,
                        sp,
                        None,
                        "VM %s(%s):$myReason" % (nodeName, uuid))
        evnet_sender.create_new_fm_event(event)

    def virEventLoopNativeRun(self):
        while True:
            libvirt.virEventRunDefaultImpl()

    def virEventLoopNativeStart(self):
        libvirt.virEventRegisterDefaultImpl()
        eventLoopThread = threading.Thread(target=self.virEventLoopNativeRun, name="libvirtEventLoop")
        eventLoopThread.setDaemon(True)
        eventLoopThread.start()

    def main(self):

        self.virEventLoopNativeStart()
        conn = libvirt.openReadOnly('qemu:///system')
        conn.domainEventRegister(self.callback, None)
        conn.setKeepAlive(5, 3)

        while conn.isAlive() == 1:
            time.sleep(1)


if __name__ == '__main__':
    CONF = cfg.CONF
    CONF.import_opt('region_name', 'watchmen_conf', 'DEFAULT')
    libvirt_utils = libvirt_utils()
    libvirt_event = libvirtEvent()
    libvirt_event.main()
