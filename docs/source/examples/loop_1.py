import gtimer as gt
import time

time.sleep(0.1)
gt.stamp('first')
for i in [1, 2, 3]:
    time.sleep(0.1)
    gt.stamp('loop', unique=False)
time.sleep(0.1)
gt.stamp('second')
print gt.report()
