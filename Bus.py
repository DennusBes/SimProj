from Vehicle import Vehicle
class Bus:

    def __init__(self):

        Vehicle.__init__(self)
        self.weight = 1
        self.shape = 'bus.png'
        self.color = ''
        self.speed = 0
        self.layer = 2
        self.delete_agent = False
        self.crossed_intersection = False


