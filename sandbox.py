from Pythagoras import *

class A(LoggableObject):
    def __init__(self):
        super().__init__(reveal_calling_method=True)
        self.info("kuku")


a = A()
print()