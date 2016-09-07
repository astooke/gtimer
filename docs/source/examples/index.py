import gtimer as gt
import time


@gt.wrap
def some_function():
    time.sleep(1)
    gt.stamp('some_method')
    time.sleep(2)
    gt.stamp('another_function')

gt.reset_root()
some_function()
gt.stamp('some_function')
time.sleep(1)
gt.stamp('another_method')
gt.stop()
print gt.report()
