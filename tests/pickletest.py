import cPickle as pickle
import os
import mmap


filename = 'wellio2.pkl'

x = {'yeah': 1, 'whack': 7, 'jack': 8}
print "x: ", x
print "id(x): ", id(x)

# Regular pickle to file.
#
# with open('data.pkl', 'wb') as f:
#     pickled_x = pickle.dumps(x)
#     print "len pickled x: ", len(pickled_x)
#     f.write(pickled_x)

# x['womp'] = 4  # transmogrify x
# print "after pickle, x: ", x

# with open('data.pkl', 'rb') as f:
#     size = os.path.getsize('data.pkl')
#     print "os.path.size: ", size
#     y = pickle.load(f)




# Pickle to mmap.
#
# filename = 'data1.pkl'
file_not_empty = os.path.isfile(filename) and os.path.getsize(filename) > 0
pickled_x = pickle.dumps(x)
data_len = len(pickled_x)
with open(filename, 'w') as f:
    f.write(data_len*b'\0')
# with open(filename, 'r+') as f:
#     mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
#     mm.flush()
#     mm.close()
with open(filename, 'r+') as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY)
    mm.seek(0)
    pickled_x = pickle.dumps(x)
    print "len pickled x: ", len(pickled_x)
    print "mm.size(): ", mm.size()
    mm.write(pickled_x)
    mm.seek(0)
    print mm.read(data_len)
    # mm.flush()
    mm.close()

x['womp'] = 4
print "after pickle, x: ", x


# # Try to unpickle without mmap code.
# with open(filename, 'rb') as f:
#     # z = f.read()
#     # print "z: ", z
#     y = pickle.load(f)  # Doesn't work when written with ACCESS_COPY
#     # But it DOES work with ACCESS_WRITE...meaning this goes to the actual
#     # file, and mmap.read() is needed to avoid that.

# print "y: ", y


with open(filename, 'rb') as f:
    size = os.path.getsize(filename)
    print "os.path.getsize: ", size
    mm = mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ)
    pickled_y = mm.read(size)
    print "len(pickled_y): ", len(pickled_y)
    print "pickled_y: ", pickled_y
    y = pickle.loads(pickled_y)
    mm.close()


print "y: ", y


# # Now make the same mmap file a larger size
# with open('data.pkl', 'r+') as f:
#     pickled_x = pickle.dumps(x)
#     size = len(pickled_x)
#     mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
#     mm_size = mm.size()
#     if mm_size < size:
#         mm.resize(size)
#     mm.seek(0)
#     print "len pickled x: ", len(pickled_x)
#     mm.write(pickled_x)
#     mm.close()

# print "x: ", x

# with open('data.pkl', 'rb') as f:
#     size = os.path.getsize('data.pkl')
#     print "os.path.getsize: ", size
#     mm = mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ)
#     pickled_y = mm.read(size)
#     print "len(pickled_y): ", len(pickled_y)
#     y = pickle.loads(pickled_y)
#     mm.close()

# print "pickled_y: ", pickled_y
# print "y: ", y


# # Now make the same mmap file a smaller size
# del x['yeah']
# with open('data.pkl', 'r+') as f:
#     pickled_x = pickle.dumps(x)
#     size = len(pickled_x)
#     mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
#     mm_size = mm.size()
#     if mm_size < size:
#         mm.resize(size)
#     mm.seek(0)
#     print "len pickled x: ", len(pickled_x)
#     mm.write(pickled_x)
#     mm.close()

# print "x: ", x

# with open('data.pkl', 'rb') as f:
#     size = os.path.getsize('data.pkl')
#     print "os.path.getsize: ", size
#     mm = mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ)
#     pickled_y = mm.read(size)
#     print "len(pickled_y): ", len(pickled_y)
#     y = pickle.loads(pickled_y)
#     mm.close()

# print "pickled_y: ", pickled_y
# print "y: ", y