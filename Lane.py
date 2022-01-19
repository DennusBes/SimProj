from CarQueue import CarQueue
class Lane:

    def __init__(self, ID, color,kind, connections, intersection):
        self.ID = ID
        self.color = color
        self.intersection = intersection
        self.connections = connections
        self.kind = kind
        self.shape = 'rect'
        self.layer = 0
        self.car_lists = [CarQueue(i) for i in range(2)]




