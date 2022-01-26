import random

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler

from FillerRoad import FillerRoad
from Vehicle import Vehicle
from Bus import Bus


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
        self.bus_agent = [None, None]
        self.x_y = [None, None]

        self.create_roads()
        # self.create_filler_roads()

    def create_roads(self):
        """ Places the lane agents on the canvas

        """

        for intersection_id, intersection in enumerate(self.ci.intersections.reshape(1, 9)[0]):
            # blijkbaar staat 6 voor de eerste intersection en 7 voor de tweede
            if intersection_id == 6:
                intersection_id = 0
            elif intersection_id == 7:
                intersection_id = 1
            if intersection is not None:
                # print(intersection_id)
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
                                    # print("Intersection: ", intersection_id, ": lane: ",lane.ID, (int(lane.bus.buslane[0]), int(lane.bus.buslane[1])))
                                    # if int(lane.ID) == int(lane.bus.buslane[intersection_id]):
                                    #     print("lane_id : ",lane.ID)
                                    # print(intersection_id, int(lane.bus.buslane[intersection_id]))

                                    # print(self.x_y)
                                    bus_lane = int(lane.bus.buslane[intersection_id])
                                    self.grid.place_agent(lane, (
                                        x_pos + eval(f"{lk}_dir_keys")[counter + 1][0] * i,
                                        y_pos + eval(f"{lk}_dir_keys")[counter + 1][1] * i))

                                    # placing the carqueue objects
                                    if (j == 1) and lk == 'ingress':

                                        if j == 1: 
                                            ind = 0
                                        # if j == 3 and int(lane.ID) == int(lane.bus.buslane):
                                        #     ind = 1

                                        self.grid.place_agent(lane.car_lists[ind], (
                                            x_pos + eval(f"{lk}_dir_keys")[counter + 1][0] * i,
                                            y_pos + eval(f"{lk}_dir_keys")[counter + 1][1] * i))

                                    if j == 0 and lk == 'ingress':
                                        self.grid.place_agent(lane.signal_group, (
                                            x_pos + eval(f"{lk}_dir_keys")[counter + 1][0] * i,
                                            y_pos + eval(f"{lk}_dir_keys")[counter + 1][1] * i))
                                    
                                    if j == 2 and lk == 'ingress' and int(lane.ID) == bus_lane:
                                            x_cor = x_pos + eval(f"{lk}_dir_keys")[counter + 1][0] * i
                                            y_cor = y_pos + eval(f"{lk}_dir_keys")[counter + 1][1] * i
                                            # stores coordinates where bus icons will be
                                            self.x_y[intersection_id] = (x_cor, y_cor)
                                    if j == 3 and lk == 'ingress' and int(lane.ID) == bus_lane:
                                        print("intersectionID:",intersection_id, " bus_lane:",int(lane.bus.buslane[intersection_id]))
                                        self.grid.place_agent(lane.car_lists[1], (
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

    def step(self):

        self.schedule.step()
        current_step = self.schedule.steps

        for intersection_id, intersection in enumerate(self.ci.intersections.reshape(1, 9)[0]):
            if intersection_id == 6:
                intersection_id = 0
            elif intersection_id == 7:
                intersection_id = 1
            if intersection is not None:

                groups = intersection.ingress_groups

                for group in groups:
                    if group is not None:
                        lanes = group.lanes
                        for lane in lanes:

                            bus_lane = int(lane.bus.buslane[intersection_id])                                
                            self.traffic_light_control(lane, current_step, groups, intersection)

                            self.spawn_vehicle(lane,0.4, intersection_id)
                            if lane.signal_group.state == 'green':
                                self.despawn_vehicle(lane)
                            
                            if int(lane.ID) == bus_lane:
                                if self.bus_agent[intersection_id] == None:
                                    self.spawn_bus(0.1, intersection_id)
                                if lane.signal_group.state == 'green' and self.bus_agent[intersection_id] != None:
                                    self.despawn_bus(lane, intersection_id)							

    def get_traffic_prio(self, groups, intersection):

        prio_dict = {}
        for group in groups:
            if group is not None:
                lanes = group.lanes
                for lane in lanes:
                    try:
                        prio_dict[lane.signal_group.ID] += (len(lane.car_lists[0].cars) + len(lane.car_lists[1].cars))
                    except KeyError:
                        prio_dict[lane.signal_group.ID] = (len(lane.car_lists[0].cars) + len(lane.car_lists[1].cars))

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


    def spawn_vehicle(self, lane, chance, intersection_id):
        if random.random() < chance:
            bus_lane = int(lane.bus.buslane[intersection_id])

            if self.bus_agent[intersection_id] != None and int(lane.ID) == bus_lane:
                lane.car_lists[1].add_car(Vehicle(self))
            else:
                lane.car_lists[0].add_car(Vehicle(self))
            # print(len(lane.car_lists[0].cars))

            if int(lane.ID) == int(lane.bus.buslane[intersection_id]):
                print("vehicles: ", len(lane.car_lists[0].cars), "laneID: ", lane.ID)
            # print("car spawned.")
            # print("amount of cars", len(lane.car_lists[0].cars))

    def despawn_vehicle(self, lane):
        if len(lane.car_lists[0].cars) > 0:
            lane.car_lists[0].remove_car()
            # print("car despawned.")
            # print("amount of cars", len(lane.car_lists[0].cars))	            

    def spawn_bus(self, chance, intersection_id):
        if random.random() < chance:
            self.bus_agent[intersection_id] = Bus(intersection_id, self)
            print("Bus created id: ", intersection_id)

            self.schedule.add(self.bus_agent[intersection_id])
            self.grid.place_agent(self.bus_agent[intersection_id], self.x_y[intersection_id])
            
            # print("bus spawned.")

    def despawn_bus(self, lane, intersection_id):
        if len(lane.car_lists[0].cars) < 1:
            print("lane_id: ", lane.ID, " cars: ", len(lane.car_lists[0].cars))
            print("despawned")

            self.grid.remove_agent(self.bus_agent[intersection_id])
            self.schedule.remove(self.bus_agent[intersection_id])
            self.bus_agent[intersection_id] = None
            print("Bus removed id: ", intersection_id)
            if len(lane.car_lists[1].cars) > 0:
                print("list 1: ",len(lane.car_lists[1].cars))
                print("list 0: ",len(lane.car_lists[0].cars))
                for i in lane.car_lists[1].cars:
                    lane.car_lists[0].add_car(i)
                lane.car_lists[1].clear_cars()

            # print("bus despawned.")
