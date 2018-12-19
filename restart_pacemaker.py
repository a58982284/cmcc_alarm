#coding:utf-8
import commands

def RestartPacemaker():
    status, output = commands.getstatusoutput("fuel node | grep cic | awk '{print $5}'")
    for cic_node in output:
        pass

def main():
    RestartPacemaker()



if __name__ == '__main__':
    main()