import threading
import time
class generate_compute_instance_with_volume(object):
    def __init__(self):
        self.interval = 5.0

    def get_nova_list(self):
        print 'get_nova_list'

    def cinder_res(self):
        print 'cinder_res'

    def alarm_item(self):
        print 'alarm_item'

    def launch(self):
        while True:
            time1 = threading.Timer(2, self.get_nova_list,)
            time2 = threading.Timer(3, self.cinder_res,)
            time3 = threading.Timer(4,self.alarm_item,)
            time1.start()
            time2.start()
            time3.start()
            time.sleep(5)

if __name__ == '__main__':
    compute_instance_with_volume = generate_compute_instance_with_volume()
    compute_instance_with_volume.launch()