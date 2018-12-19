#coding:utf-8
import commands


def TrafficLinkMonitor():
    region_status, region = commands.getstatusoutput("grep region_name /etc/watchmen/watchmen-producer.conf | cut -d\"=\" -f2")
    pass


def main():
    TrafficLinkMonitor()


if __name__ == '__main__':
    main()