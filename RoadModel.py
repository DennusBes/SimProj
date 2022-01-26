import random

import numpy as np
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler

from Bus import Bus
from FillerRoad import FillerRoad
from Vehicle import Vehicle


class RoadModel(Model):

    def __init__(self, green_length, orange_length, bus_weight, traffic_light_priority, ci,
                 pity_timer_limit, car_spawn_rate):

        super().__init__()
        self.car_spawn_rate = car_spawn_rate
        self.pity_timer_limit = pity_timer_limit
        self.bus_weight = bus_weight
        self.traffic_light_priority = traffic_light_priority
        self.ci = ci
        self.bus_lanes = self.ci.bus_lanes
        self.green_length = green_length
        self.orange_length = orange_length
        self.schedule = BaseScheduler(self)
        self.grid = MultiGrid(self.ci.dimensions[0], self.ci.dimensions[1], torus=False)
        self.bus_spawns = [None for _ in self.ci.intersections_list]

        self.create_roads()
        # self.create_filler_roads()

    def create_roads(self):
        """ Places the lane agents on the canvas

        """

        for intersection in self.ci.intersections.reshape(1, 9)[0]:
            # blijkbaar staat 6 voor de eerste intersection en 7 voor de tweede

            if intersection is not None:
                intersection_id = intersection.ID

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
                                    bus_lane = int(self.bus_lanes[intersection_id])
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
                                        self.bus_spawns[intersection_id] = (x_cor, y_cor)
                                    if j == 3 and lk == 'ingress' and int(lane.ID) == bus_lane:
                                        print("intersectionID:", intersection_id, " bus_lane:",
                                              int(self.bus_lanes[intersection_id]))
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

            if intersection is not None:
                intersection_id = intersection.ID

                intersection.pity_traffic_light = self.check_for_pity_timer(intersection)

                groups = intersection.ingress_groups

                for group in groups:
                    if group is not None:
                        lanes = group.lanes
                        for lane in lanes:

                            bus_lane = int(self.bus_lanes[intersection_id])
                            self.traffic_light_control(lane, current_step, groups, intersection)

                            self.spawn_vehicle(lane, self.car_spawn_rate, intersection_id)
                            if lane.signal_group.state == 'green':
                                self.despawn_vehicle(lane)

                            if int(lane.ID) == bus_lane:
                                if lane.bus is None:
                                    self.spawn_bus(0.1, intersection_id, lane)
                                if lane.signal_group.state == 'green' and lane.bus is not None:
                                    self.despawn_bus(lane, intersection_id)

    def get_traffic_prio(self, groups, intersection, pity_light):

        prio_dict = {}
        for group in groups:
            if group is not None:
                lanes = group.lanes
                for lane in lanes:
                    if lane.bus is None:
                        bus_weight = 0
                    else:
                        bus_weight = int(lane.bus.weight)

                    try:
                        prio_dict[lane.signal_group.ID] += (
                                len(lane.car_lists[0].cars) + len(lane.car_lists[1].cars) + bus_weight)
                    except KeyError:
                        prio_dict[lane.signal_group.ID] = (
                                len(lane.car_lists[0].cars) + len(lane.car_lists[1].cars) + bus_weight)

        combos = intersection.traffic_light_combos
        if pity_light is not None:
            combos = ([i for i in combos if pity_light in i])
            if len(combos) == 0:
                combos = intersection.traffic_light_combos
        return combos[np.argmax([sum([prio_dict[x] if x in list(prio_dict.keys()) else 0 for x in i]) for i in combos])]

    def traffic_light_control(self, lane, current_step, groups, intersection):

        if lane.signal_group.ID not in intersection.current_green:
            lane.signal_group.change_state('red')
            lane.signal_group.ticks_since_state_change += 1
        if (
                lane.signal_group.state == 'red' or lane.signal_group.state == 'orange') and lane.signal_group.ID in intersection.current_green and intersection.step_at_change + self.green_length > current_step:
            lane.signal_group.change_state('green')
            intersection.step_at_change = current_step
            lane.signal_group.ticks_since_state_change = 0
        if intersection.step_at_change + self.green_length == current_step and lane.signal_group.state == 'green':
            lane.signal_group.change_state('orange')
        if intersection.step_at_change + self.green_length + self.orange_length == current_step and lane.signal_group.state == 'orange':
            lane.signal_group.change_state('red')
            if self.traffic_light_priority:
                pity = intersection.pity_traffic_light
                intersection.current_green = self.get_traffic_prio(groups, intersection, pity)
            else:
                try:
                    intersection.current_green = intersection.traffic_light_combos[
                        intersection.traffic_light_combos.index(intersection.current_green) + 1]
                except IndexError:
                    intersection.traffic_light_combos[0]

            intersection.step_at_change = current_step + 1

    def spawn_vehicle(self, lane, chance, intersection_id):

        if random.random() < chance:
            bus_lane = int(self.bus_lanes[intersection_id])

            if lane.bus is not None and int(lane.ID) == bus_lane:
                lane.car_lists[1].add_car(Vehicle(self))
            else:
                lane.car_lists[0].add_car(Vehicle(self))
            # print(len(lane.car_lists[0].cars))

            if int(lane.ID) == int(self.bus_lanes[intersection_id]):
                print("vehicles: ", len(lane.car_lists[0].cars), "laneID: ", lane.ID)
            # print("car spawned.")
            # print("amount of cars", len(lane.car_lists[0].cars))

    def despawn_vehicle(self, lane):
        if len(lane.car_lists[0].cars) > 0:
            lane.car_lists[0].remove_car()
            # print("car despawned.")
            # print("amount of cars", len(lane.car_lists[0].cars))	            

    def spawn_bus(self, chance, intersection_id, lane):
        if random.random() < chance:
            bus = Bus(intersection_id, self.bus_weight, self)
            lane.bus = bus
            print("Bus created id: ", intersection_id)

            self.schedule.add(lane.bus)
            self.grid.place_agent(lane.bus, self.bus_spawns[intersection_id])

            # print("bus spawned.")

    def despawn_bus(self, lane, intersection_id):
        if len(lane.car_lists[0].cars) < 1:
            print("lane_id: ", lane.ID, " cars: ", len(lane.car_lists[0].cars))
            print("despawned")

            try:
                self.grid.remove_agent(lane.bus)
                self.schedule.remove(lane.bus)
            except ValueError:
                pass
            lane.bus = None
            print("Bus removed id: ", intersection_id)
            if len(lane.car_lists[1].cars) > 0:
                print("list 1: ", len(lane.car_lists[1].cars))
                print("list 0: ", len(lane.car_lists[0].cars))
                for i in lane.car_lists[1].cars:
                    lane.car_lists[0].add_car(i)
                lane.car_lists[1].clear_cars()

            # print("bus despawned.")

    def check_for_pity_timer(self, intersection):

        if intersection is not None:

            groups = intersection.ingress_groups

            for group in groups:
                if group is not None:
                    lanes = group.lanes
                    for lane in lanes:

                        if self.pity_timer_limit < lane.signal_group.ticks_since_state_change:
                            return lane.signal_group.ID
                            continue

            return None
