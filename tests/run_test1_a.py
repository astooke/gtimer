import gtimer as gt
import test1_b
import time


time.sleep(0.1)
gt.stamp('first')
time.sleep(0.2)
gt.stamp('second')
loop = gt.timed_loop('loop')
for i in [1, 2, 3]:
    next(loop)
    test1_b.func()
    test1_b.func()
    time.sleep(0.1)
    gt.stamp('loop1')
loop.exit()
time.sleep(0.1)
gt.stamp('third')

x = gt.save_pkl()


print(gt.report())
