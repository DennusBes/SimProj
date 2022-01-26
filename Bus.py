from Vehicle import Vehicle

from mesa import Agent

class Bus(Agent):

    def __init__(self, unique_id,weight, model):
        super().__init__(unique_id, model)
        self.weight = weight
        self.shape = 'bus.png'
        self.color = ''
        self.speed = 0
        self.layer = 2
        self.delete_agent = False
        self.crossed_intersection = False
