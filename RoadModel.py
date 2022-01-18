from mesa import Model
from mesa.space import MultiGrid

from Car import Car
from FillerRoad import FillerRoad


class RoadModel(Model):

    def __init__(self, length, intersection):

        super().__init__()
        self.length = length
        self.intersection = intersection
        self.grid = MultiGrid(self.intersection.dimensions[0], self.intersection.dimensions[1], torus=False)
        self.create_roads()
        self.create_filler_roads()
        self.create_vehicle()

    def create_roads(self):
        """ Places the lane agents on the canvas

        """

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

                        x_pos = (int(lg.lon) + dir_keys[counter + 1][0] * j)
                        y_pos = (int(lg.lat) + dir_keys[counter + 1][1] * j)

                        for i, lane in enumerate(lanes):
                            self.grid.place_agent(lane, (
                                x_pos + eval(f"{lk}_dir_keys")[counter + 1][0] * i,
                                y_pos + eval(f"{lk}_dir_keys")[counter + 1][1] * i))

    def create_filler_roads(self):

        """ place FillerRoad agents between the lanes

        """

        x, y = self.intersection.center
        x, y = int(x), int(y)
        mid_square = self.intersection.mid_square
        sep = self.intersection.sep

        sep = sep - 1
        lst = list(range(x - mid_square - sep, x + 1 + mid_square + sep))

        for i in lst:
            for j in lst:
                self.grid.place_agent(FillerRoad(i + j), (i, j))



    def create_vehicle(self):

        self.grid.place_agent(Car(),(51,51))
        print(self.grid.get_cell_list_contents((51,51)))



