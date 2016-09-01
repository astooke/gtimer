from context import gtimer as gt
import time
import test2_b
# import data_glob as g


# @gt.wrap
def funky():
    print "inside funky"
    time.sleep(0.1)
    gt.stamp('wrapped_1')


time.sleep(0.1)
gt.stamp('first')
# for i in [1, 2, 3]:

dumdum = test2_b.Dummy()

dumdum.print_it()
gt.stamp('after dumdum')
loop = gt.timed_for([1, 2, 3], 'loop1')


# for i in gt.timed_for([1, 2, 3], 'loop1'):
for i in loop:
    print "i: ", i
    # print "g.lf: ", g.lf
    # print "g.lf.stamps: ", g.lf.stamps
    time.sleep(0.1)
    funky()
    gt.stamp('l1_first')
    for j in gt.timed_for([1, 2], 'loop2'):
        # for j in [1, 2, 3]:
        print "j: ", j
        # print "g.lf: ", g.lf
        # print "g.lf.stamps: ", g.lf.stamps
        time.sleep(0.1)
        gt.stamp('l2_first1234654654654654654645ghghgh54654')
        funky()

    #     funky()
    #     gt.stamp('after_funky')
    #     # for k in gt.timed_for([1, 2], 'loop3'):
    #     #     print "k: ", k
    #     #     time.sleep(0.03)
    #     #     gt.stamp('l3_first')
    #     #     funky()
    #     #     gt.stamp('l3_after_funky')
    #     # for m in gt.timed_for([1, 2], 'loop4'):
    #     #     print "m: ", m
    #     #     time.sleep(0.01)
    #     #     gt.stamp('l_fourth')
    #     time.sleep(0.1)
    #     gt.stamp('l2_second')
time.sleep(0.1)
gt.stamp('second')
# gt.open_next_timer('yeah')
time.sleep(0.1)
gt.stamp('yeah_1')
test2_b.monkey()
time.sleep(0.1)
gt.stamp('yeah_2')
time.sleep(0.1)
gt.stamp('yeah_1', unique=False)
# gt.close_last_timer()
funky()
gt.stop()
# print g.rf.children
print gt.report()
# print g.tif.times.stamps
# print g.tif.times.stamps_itrs


