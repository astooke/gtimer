# print test.
import gtimer as gt
import time
import gtimer.data_glob as g
import os


filenames = ['test3a.pkl', 'test3b.pkl']

time.sleep(0.1)
# gt.stamp('beforehand')
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
    # print gt.report()
    # print 'past report'


gt.stop()
gt.rename_root_timer('par1')
# print gt.report(include_itrs=False)

# times1 = gt.get_times()
gt.save_pkl(filenames[0])
# print "before reset: ", g.sf.cum
gt.reset_current_timer()
# print "after reset: ", g.sf.cum
# print gt.report()


time.sleep(0.1)
gt.stamp('extra')

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
    # print gt.report()
    # print 'past report'

gt.stop()
gt.rename_root_timer('par2')
gt.save_pkl(filenames[1])
# times2 = gt.get_times()

gt.reset_current_timer()
gt.rename_root_timer('serial')


time.sleep(0.1)
gt.stamp('first serial')
gt.attach_par_subdivision('my_first_par', gt.load_pkl(filenames))
# print "after attaching, out in script: ", g.tf.par_subdvsn_awaiting
time.sleep(0.2)
gt.stamp('second_serial')
# print "after stamp: ", g.rf.par_subdvsn
gt.stop()

# filename = 'test_file.pkl'
# gt.save(filename)
# print os.path.getsize(filename)


# print g.rf.par_subdvsn
print gt.report()
print gt.compare()
# with open('test_delim.out', 'w') as f:
#     f.write(gt.compare(delim_mode=True))
# print gt.report()
# print gt.compare([times1, times2], 'yabba-dabba')

