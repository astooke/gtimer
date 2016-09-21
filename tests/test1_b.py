import gtimer as gt
import time

@gt.wrap()
def func():
    time.sleep(0.3)
    gt.stamp('in_test1_b')
