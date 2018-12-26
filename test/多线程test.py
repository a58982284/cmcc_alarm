# encoding: UTF-8
import threading
import time
# 方法1：将要执行的方法作为参数传给Thread的构造方法
def func():
    print 'func() passed to Thread'
while True:
    t1 = threading.Thread(target=func)
    t2 = threading.Thread(target=func)
    time.sleep(2)
    t1.start()
    t2.start()