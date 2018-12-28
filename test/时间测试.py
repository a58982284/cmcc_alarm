import time

timeStamp = 0

if (time.time()-timeStamp >30):
    print timeStamp
    timeStamp = time.time()
    print timeStamp