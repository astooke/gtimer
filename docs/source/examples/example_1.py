import gtimer as gt
import time

time.sleep(0.1)
gt.stamp('first')
time.sleep(0.2)
gt.stamp('second')
time.sleep(0.1)
gt.stamp('third')
print gt.report()
