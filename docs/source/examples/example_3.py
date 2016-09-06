import gtimer as gt
import time

time.sleep(0.1)
gt.start()
time.sleep(0.1)
gt.stamp('first')
gt.pause()
time.sleep(0.1)
gt.resume()
gt.stamp('second')
time.sleep(0.1)
gt.b_stamp('third')
time.sleep(0.1)
gt.stop('fourth')
time.sleep(0.1)
print gt.report()
