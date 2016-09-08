import gtimer as gt
import time

# Could be in another file with gtimer import.
@gt.wrap
def func_1():
    time.sleep(0.1)
    gt.stamp('f_first')

def func_2():
    time.sleep(0.1)
    gt.stamp('f_inline')

time.sleep(0.1)
func_1()
gt.stamp('first')
func_2()
gt.stamp('second')
time.sleep(0.1)
gt.stamp('third', quick_print=True)
gt.subdivide('sub')
time.sleep(0.1)
func_1()
gt.stamp('sub_1')
time.sleep(0.1)
gt.stamp('sub_2')
gt.end_subdivision()
gt.stamp('fourth')
print gt.report()