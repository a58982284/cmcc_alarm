#coding:utf-8
import sys
import commands
import time
import os



def occupy_single_cpu(nums):
    cpu = nums
    os.popen("nohup python \-u cpu_occupy.py >/dev/null 2>&1 &")
    print ("cpu {} occupied by cpu_occupy.py,please pay attention.".format(cpu))


def main():
    if len(sys.argv) == 1:
        print "Usage: $0 <cpu 1> <cpu2> ... <cpu #>"
        print "         you can specify cpu by either range or specific cpu"
        print "         for example:"
        print "         1-23,25,30-45"
        exit(1)

    while len(sys.argv) > 1:
        cpu = sys.argv[1]
        print cpu
        if "-" in cpu:
            from_cpu = cpu.split("-")[0]
            to_cpu = cpu.split("-")[1]
            from_cpu_int = int(from_cpu)
            to_cpu_int = int(to_cpu)
            time.sleep(10)  #be careful please.
            if to_cpu and (from_cpu_int<to_cpu_int):
                for i in range(to_cpu_int, to_cpu_int + 1):
                    occupy_single_cpu(str(i))
        else:
            occupy_single_cpu(cpu)
            time.sleep(10)  #be careful please.


if __name__ == '__main__':
    main()
