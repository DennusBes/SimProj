import random

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler

from FillerRoad import FillerRoad
from Vehicle import Vehicle


class RoadModel(Model):

    def __init__(self, intersection, green_length, orange_length, traffic_light_priority, ci):

        super().__init__()
        self.traffic_light_priority = traffic_light_priority
        self.ci = ci
        self.green_length = green_length
        self.orange_length = orange_length
        self.intersection = intersection
        self.schedule = BaseScheduler(self)
        self.grid = MultiGrid(self.ci.dimensions[0], self.ci.dimensions[1], torus=False)
        self.create_roads()
        # self.create_filler_roads()
        self.create_vehicle()

    def create_roads(self):
        """ Places the lane agents on the canvas

        """

        for intersection in self.ci.intersections.reshape(1, 9)[0]:
            if intersection is not None:

                for lk in ['ingress', 'egress']:

                    # print(self.intersection.ingress_groups)

                    data = eval(f'intersection.{lk}_groups')

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

                                    # placing the carqueue objects
                                    if (j == 1 or j == 3) and lk == 'ingress':

                                        if j == 1:
                                            ind = 0
                                        if j == 3:
                                            ind = 1

                                        self.grid.place_agent(lane.car_lists[ind], (
                                            x_pos + eval(f"{lk}_dir_keys")[counter + 1][0] * i,
                                            y_pos + eval(f"{lk}_dir_keys")[counter + 1][1] * i))

                                    if j == 0 and lk == 'ingress':
                                        self.grid.place_agent(lane.signal_group, (
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
        for i in range(1):
            vehicle = Vehicle(i, self)
            self.grid.place_agent(vehicle, (12, 23 - i))
            self.schedule.add(vehicle)

    def step(self):

        self.schedule.step()
        current_step = self.schedule.steps

        for intersection in self.ci.intersections.reshape(1, 9)[0]:
            if intersection is not None:

                groups = intersection.ingress_groups

                for group in groups:
                    if group is not None:
                        lanes = group.lanes
                        for lane in lanes:

                            self.traffic_light_control(lane, current_step, groups, intersection)

                            self.spawn_vehicle(lane,0.4)
                            if lane.signal_group.state == 'green':
                                self.despawn_vehicle(lane)

    def get_traffic_prio(self, groups, intersection):

        prio_dict = {}
        for group in groups:
            if group is not None:
                lanes = group.lanes
                for lane in lanes:
                    try:
                        prio_dict[lane.signal_group.ID] += len(lane.car_lists[0].cars)
                    except KeyError:
                        prio_dict[lane.signal_group.ID] = len(lane.car_lists[0].cars)

        combos = intersection.traffic_light_combos

        return combos[np.argmax([sum([prio_dict[x] if x in list(prio_dict.keys()) else 0 for x in i]) for i in combos])]

    def traffic_light_control(self, lane, current_step, groups, intersection):

        if lane.signal_group.ID not in intersection.current_green:
            lane.signal_group.change_state('red')
        if (
                lane.signal_group.state == 'red' or lane.signal_group.state == 'orange') and lane.signal_group.ID in intersection.current_green and intersection.step_at_change + self.green_length > current_step:
            lane.signal_group.change_state('green')
            intersection.step_at_change = current_step
        if intersection.step_at_change + self.green_length == current_step and lane.signal_group.state == 'green':
            lane.signal_group.change_state('orange')
        if intersection.step_at_change + self.green_length + self.orange_length == current_step and lane.signal_group.state == 'orange':
            lane.signal_group.change_state('red')
            if self.traffic_light_priority:
                intersection.current_green = self.get_traffic_prio(groups, intersection)
            else:
                try:
                    intersection.current_green = intersection.traffic_light_combos[
                        intersection.traffic_light_combos.index(intersection.current_green) + 1]
                except IndexError:
                    intersection.traffic_light_combos[0]

            intersection.step_at_change = current_step + 1


    def spawn_vehicle(self, lane, chance):
        if random.random() < chance:
            lane.car_lists[0].add_car(Vehicle(1, self))

    def despawn_vehicle(self, lane):

        if len(lane.car_lists[0].cars) > 0:
            lane.car_lists[0].remove_car()
