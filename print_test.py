# print test.
import gtimer.gtimer as gt
import time


time.sleep(0.1)

loop = gt.timed_loop('loop1')


for i in [1, 2, 3, 4]:
    next(loop)
    time.sleep(0.1)
    gt.stamp('l1')
loop.exit()

# current_times = gt.get_times()
# print gt.report()


loop2 = gt.timed_for([1, 2, 3], 'loop2')
for i in loop2:
    print "i: ", i
    time.sleep(0.1)
    gt.stamp('l2')
    loop3 = gt.timed_for([1, 2, 3], 'loop3')
    for j in loop3:
        print "j: ", j
        time.sleep(0.1)
        gt.stamp('l3')
    print gt.report()
    print 'past report'


gt.stop()

print gt.report()