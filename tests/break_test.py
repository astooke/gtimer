import gtimer as gt
import time


time.sleep(0.1)
gt.stamp('first')

# gt.break_for()
# x = gt.timed_for([1, 2, 3], 'loop')
# print "made x"
# time.sleep(2)
# print "calling the for loop"
# for i in x:  # gt.timed_for([1, 2, 3, 4], 'loop'):
#     print i
#     if i == 3:
#         break
#     time.sleep(0.1)
#     gt.stamp('l_1')


# for i in gt.timed_for([1, 2, 3, 4], 'loopA'):
#     if i == 3:
#         gt.break_loop()
#         break
#     time.sleep(0.1)
#     gt.stamp('lA')

# loop = gt.timed_for([1, 2, 3, 4], 'loopB')

# for i in loop:
#     if i == 3:
#         gt.break_for()
#         break
#     time.sleep(0.1)
#     gt.stamp('lB')

loop = gt.timed_for([1, 2, 3], 'forfor')
for i in loop:
    print i
    time.sleep(0.1)
    gt.stamp('loop1')
    for j in [4, 5, 6]:
        print j
        time.sleep(0.1)
        gt.stamp('loop2', unique=False)




# with loop:
# for i in loop:
#     # loop.next()
#     print i
#     # if i == 3:
#     #     # gt.break_for()
#     #     loop.exit()
#     #     break
#     time.sleep(0.1)
#     i += 1
#     gt.stamp('welp')
# # loop.exit()

# for j in loop:
#     print j
#     time.sleep(0.1)
#     gt.stamp('womp')

# loop2 = gt.timed_while('loopC')
# for i in loop2:
#     time.sleep(0.1)
#     gt.stamp('lC')



# for i in gt.TimedFor([1, 2, 3], 'loop1'):
#     if i == 2:
#         pass
#     time.sleep(0.1)
#     gt.stamp('inloop1')

# with gt.TimedFor([1, 2, 3], 'loop2') as loop:
#     for i in loop:
#         time.sleep(0.1)
#         gt.stamp('inloop2')

# for i in gt.timed_for([1, 2, 3], 'loop3'):
#     time.sleep(0.1)
#     gt.stamp('inloop3')

# YES PREFERRED.
# x = 0
# with gt.timed_while('loop4') as loop:
#     while x < 7:
#         next(loop)
#         x += 1
#         print x
#         if x == 3:
#             continue
#         if x == 6:
#             break
#         time.sleep(0.1)
#         gt.stamp('inloop4')



# Since these are not prefered, get rid of the 
# __iter__() method on the while loop, only keep
# next().


# x = 0
# NOT PREFERRED ... strange to have a while using 
# a for statement, nothing special about timing code
# requires this construct, this is generally possible
# and mangled style.
# for _ in gt.TimedWhile2('loop5'):
#     print x
#     x += 1
#     if x == 3:
#         # gt.break_loop()
#         break
#     time.sleep(0.1)
#     gt.stamp('inloop5')
#     if x > 4:
#         gt.set_while_false()

# x = 0
# NOT PREFERRED: calls for.
# with gt.TimedWhile2('loop6') as loop:
#     for _ in loop:
#         print x
#         x += 1
#         if x == 3:
#             gt.break_loop()
#             break
#         time.sleep(0.1)
#         gt.stamp('inloop6')
#         if x > 4:
#             gt.set_while_false()

# for i in gt.TimedFor([1, 2, 3, 4], 'loop'):
#     # if i == 3:
#     #     break
#     time.sleep(0.1)
#     gt.stamp('l_1')

time.sleep(0.1)
gt.stamp('last')
gt.stop()
print gt.report()
