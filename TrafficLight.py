class TrafficLight:

    def __init__(self, id, lane):
        self.ID = id
        self.state = 'red'
        self.shape = 'circle'
        self.lane = lane

    def change_state(self, state):
        self.state = state
