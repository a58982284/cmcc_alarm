import threading
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
        self.logger = logging.getLogger("libvirt_log")
        self.timeStamp_event4 = 0
        self.timeStamp_event5 = 0

    def callback(self, conn, dom, event, detail, opaque):
        myInstance = dom.name()
        global nodeName
        nodeName = libvirt_utils.get_nova_name(myInstance)
        global uuid
        uuid = libvirt_utils.get_uuid_by_name(myInstance)
        global tenant_id
        tenant_id = libvirt_utils.get_tenant_id(myInstance)

        if "instance" in dom.name():
            if (time.time() - self.timeStamp_event4 > 30) and event == 4:
                minor_id = 2032696
                self.watchmenAlarm(True, self.region, tenant_id, uuid, nodeName, minor_id,
                                   enums.FM_ACTIVE_SEVERITY.CRITICAL,
                                   "Virtual Machine OS Fault")
                self.logger.error(
                    "watchmen-client create-event -sf -src Region=\"%s\",CeeFunction=\"1\",Tenant=\"%s\",VM=%s -ma 193 -mi 2032696 -s CRITICAL -e communicationsAlarm  -p m3100Indeterminate -sp \"Virtual Machine OS Fault\" -t \"VM %s(%s)\"" % (
                        self.region, tenant_id, uuid, nodeName, uuid))
                self.logger.error('%s VM %s(%s): Detected Virtual Machine OS Fault,possible reason: kernel panic' % (
                    str(time.ctime()), nodeName, uuid))
                global timer
                timer = threading.Timer(10.0, self.watchmenCleared, [tenant_id, uuid, nodeName])
                timer.start()
                self.timeStamp_event4 = time.time()
            elif (time.time() - self.timeStamp_event5 > 30) and event == 5:
                minor_id = 2032697
                self.watchmenAlarm(False, self.region, tenant_id, uuid, nodeName, minor_id,
                                   enums.FM_ACTIVE_SEVERITY.WARNING,
                                   "Virtual Machine Running Fault")
                self.logger.warning(
                    "watchmen-client create-event -sl -src Region=%s,CeeFunction=\"1\",Tenant=\"%s\",VM=$uuid -ma 193 -mi 2032697 -s WARNING -e communicationsAlarm  -p m3100Indeterminate -sp \"Virtual Machine Running Fault\" -t \"VM %s(%s):%s\"" % (
                        self.region, tenant_id, uuid, nodeName, uuid))
                self.logger.warning(
                    '%s VM %s(%s): Detected Virtual Machine Running Fault,possible reason: qemu process had been killed or vm been powered off or shutdown abnormal.' % (
                        str(time.ctime()), nodeName, uuid))
                self.timeStamp_event5 = time.time()
        else:
            self.timeStamp = time.time()
        time.sleep(1)

    def watchmenCleared(self, tenant_id, uuid, nodeName):
        self.watchmenAlarm(True, self.region, tenant_id, uuid, nodeName, 2032696, enums.FM_ACTIVE_SEVERITY.CLEARED,
                           "Virtual Machine OS Fault")
        self.logger.info(
            "watchmen-client create-event -sf -src Region=\"%s\",CeeFunction=\"1\",Tenant=\"%s\",VM=%s -ma 193 -mi 2032696 -s CLEARED -e communicationsAlarm  -p m3100Indeterminate -sp \"Virtual Machine OS Fault\" -t \"VM %s(%s)\"" % (
                self.region, tenant_id, uuid, nodeName, uuid))
        self.logger.info(
            '%s VM %s(%s): Detected Virtual Machine OS Fault,possible reason: kernel panic.Cleared watchmen alarm.' % (
                str(time.ctime()), nodeName, uuid))

    def watchmenAlarm(self, boole, region, tenant_id, uuid, nodeName, minor_id, fm_active_severity, sp):
        evnet_sender = EventSender()
        source_one = "Region=%s,CeeFunction=1,Tenant=%s,VM=%s" % (
            region, tenant_id, uuid)
        event = FmEvent(boole, source_one, 193, minor_id, fm_active_severity, enums.FM_EVENT_TYPE.communicationsAlarm,
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
        logging.config.fileConfig('/var/cmcc-la/conf/libvirtevent_log.conf')
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
