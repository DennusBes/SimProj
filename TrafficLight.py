class TrafficLight:

    def __init__(self, id, lane):
        self.ID = id
        self.state = 'red'
        self.shape = 'circle'
        self.ticks_since_state_change = 0
        self.lane = lane

    def change_state(self, state):
        self.state = state
