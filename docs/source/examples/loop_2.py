import gtimer as gt
import time

time.sleep(0.1)
gt.stamp('first')
for i in gt.timed_for([1, 2, 3]):
    time.sleep(0.1)
    gt.stamp('loop_1')
    if i > 1:
        time.sleep(0.1)
        gt.stamp('loop_2')
time.sleep(0.1)
gt.stamp('second')
print gt.report()
