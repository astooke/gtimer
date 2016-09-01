

x = 7
print "x: ", x


def add_1():
    print "in add_1"
    global x
    x += 1
    print "in add_1, after +=1: ", x


def do_the_thing_to_x():
    add_1()


do_the_thing_to_x()

print "after do the thing: ", x