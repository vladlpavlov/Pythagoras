from Pythagoras import *

my_cache = PickleCache()

my_cache.update_parent_logger()

@my_cache
def f(x):
    return x**2

f(7)








