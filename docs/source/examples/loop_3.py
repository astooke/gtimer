import gtimer as gt
import time

time.sleep(0.1)
gt.stamp('first')
loop = gt.timed_loop('named_loop')
x = 0
while x < 3:
    next(loop)
    time.sleep(0.1)
    x += 1
    gt.stamp('loop')
loop.exit()
time.sleep(0.1)
gt.stamp('second')
print gt.report(include_itrs=False)