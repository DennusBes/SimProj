import numpy as np


class ConnectedIntersections:

    def __init__(self, intersections_list, dimensions):
        self.intersections_list = intersections_list
        self.dimensions = dimensions

        self.intersections = np.empty((3, 3), dtype=object)
        self.fill_intersections_matrix()
        self.create_centerpoints()
        self.fill_all_intersections()

    def fill_intersections_matrix(self):

        il = self.intersections_list.copy()

        for i in range(self.intersections.shape[0], 0, -1):
            for j in range(self.intersections.shape[1]):
                try:
                    self.intersections[i, j] = il[-1]
                    del il[-1]
                except IndexError:
                    continue

    def create_centerpoints(self):
        x_base = self.dimensions[1] / 3
        y_base = self.dimensions[0]
        for count_1, i in enumerate(self.intersections):
            for count_2, j in enumerate(i):
                x_upper_lim = x_base + x_base * count_2
                y_upper_lim = y_base - count_1 * y_base / 3

                x_lower_lim = x_upper_lim - x_base
                y_lower_lim = y_upper_lim - y_base / 3

                if j is not None:
                    j.center = ((int(np.mean((x_upper_lim, x_lower_lim))), int(np.mean((y_upper_lim, y_lower_lim)))))

    def fill_all_intersections(self):

        for count_1, i in enumerate(self.intersections):
            for count_2, j in enumerate(i):

                if self.intersections[count_1,count_2] is not None:
                    self.intersections[count_1,count_2].fill_intersection()

