import gtimer as gt
import time

time.sleep(0.1)
gt.stamp('first')
time.sleep(0.3)
gt.stamp('second')
print gt.report()