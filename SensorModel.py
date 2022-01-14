from mesa import Model
from mesa.space import SingleGrid
import numpy as np


class SensorModel(Model):

    def __init__(self, length, intersection):

        super().__init__()
        self.length = length
        self.intersection = intersection
        self.grid = SingleGrid(self.intersection.dimensions[0], self.intersection.dimensions[1], torus=False)
        self.create_agents()

    def create_agents(self):

        for lk in ['ingress', 'egress']:

            data = eval(f'self.intersection.{lk}_groups')

            dir_keys = {1: (0, +1), 2: (+1, 0), 3: (0, -1), 4: (-1, 0)}

            for counter, lg in enumerate(data):
                if lg is not None:
                    x_pos = lg.lon
                    y_pos = lg.lat
                    length = lg.length

                    for j in range(length):
                        agent = lg
                        self.grid.place_agent(agent, (
                            int(x_pos) + dir_keys[counter+1][0] * j, int(y_pos) + dir_keys[counter+1][1] * j))


