from Vehicle import Vehicle

class Car(Vehicle):

    def __init__(self):
        Vehicle.__init__(self)

        self.shape = 'circle'


