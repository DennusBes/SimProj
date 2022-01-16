from mesa import Model
from mesa.space import SingleGrid


class RoadModel(Model):

    def __init__(self, length, intersection):

        super().__init__()
        self.length = length
        self.intersection = intersection
        self.grid = SingleGrid(self.intersection.dimensions[0], self.intersection.dimensions[1], torus=False)
        self.create_road()

    def create_road(self):

        for lk in ['ingress', 'egress']:

            data = eval(f'self.intersection.{lk}_groups')

            dir_keys = {1: (0, +1), 2: (+1, 0), 3: (0, -1), 4: (-1, 0)}

            # These are the direcion keys that fill in the roads
            ingress_dir_keys = {1: (+1, 0), 2: (0, -1), 3: (-1, 0), 4: (0, +1)}
            egress_dir_keys = {1: (-1, 0), 2: (0, +1), 3: (+1, 0), 4: (0, -1)}

            for counter, lg in enumerate(data):
                if lg is not None:
                    length = lg.length
                    lanes = lg.lanes

                    for j in range(length):
                        x_pos = lg.lon
                        y_pos = lg.lat

                        x_pos = (int(x_pos) + dir_keys[counter + 1][0] * j)
                        y_pos = (int(y_pos) + dir_keys[counter + 1][1] * j)

                        for i, lane in enumerate(lanes):
                            if lk == 'ingress':
                                self.grid.place_agent(lane, (
                                    x_pos + ingress_dir_keys[counter + 1][0] * i,
                                    y_pos + ingress_dir_keys[counter + 1][1] * i))

                            elif lk == 'egress':
                                self.grid.place_agent(lane, (
                                    x_pos + egress_dir_keys[counter + 1][0] * i,
                                    y_pos + egress_dir_keys[counter + 1][1] * i))
