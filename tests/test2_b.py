import gtimer as gt


# from context import gtimer as gt
import time


@gt.wrap
def monkey():
    print "in monkey"
    time.sleep(0.1)
    gt.stamp('oh-whoa')


class Dummy(object):

    @gt.wrap
    def print_it(self):
        time.sleep(0.1)
        print "time.sleep(0.1)"
        gt.stamp('in_the_method')