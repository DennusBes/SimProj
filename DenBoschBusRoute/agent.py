import numpy as np
import pandas as pd
from mesa import Agent


class ConnectedIntersections:

    def __init__(self, intersections_list, dimensions, bus_lanes):
        self.bus_lanes = bus_lanes
        self.intersections_list = intersections_list
        self.dimensions = dimensions
        self.intersections = np.empty((3, 3), dtype=object)
        self.fill_intersections_matrix()
        self.create_centerpoints()
        self.fill_all_intersections()

    def fill_intersections_matrix(self):

        il = self.intersections_list.copy()

        count_list = []
        for i in range(self.intersections.shape[0], 0, -1):
            for j in range(self.intersections.shape[1]):
                try:
                    self.intersections[i, j] = il[-1]
                    self.intersections[i, j].ID = len(count_list)
                    count_list.append('')
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

                if self.intersections[count_1, count_2] is not None:
                    self.intersections[count_1, count_2].fill_intersection()


class Intersection:

    def __init__(self, xml_dict, flip, trafic_light_combos, turn_instructions=[]):

        self.turn_instructions = turn_instructions
        self.flip = flip
        self.xml_dict = xml_dict
        self.lat = self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['refPoint']['lat']
        self.lon = self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['refPoint']['long']
        self.traffic_light_combos = trafic_light_combos
        self.step_at_change = 0
        self.current_green = trafic_light_combos[0]
        self.pity_traffic_light = None
        self.ID = None
        self.center = None
        self.lane_df = None
        self.max_group_width = None
        self.mid_square = None
        self.sep = None
        self.ingress_groups = None
        self.egress_groups = None

    def set_group_numbers(self, kind):
        """ returns a list with the numbers of the lanegroups that should be created for ingress/egress

        Args:
            kind: ingress or egress

        Returns: a list of the numbers of lanegroups

        """

        gn = list(set(list(set(eval(f'self.lane_df.{kind}Approach')))))
        gn.remove(np.NaN)

        return sorted([int(x) for x in gn])

    def set_lane_groups(self, kind):
        """ create the lanegroup objects for this intersection

        Args:
            kind: ingress or egress

        Returns: a list of lanegroup objects

        """

        mid_square = self.mid_square
        sep = self.sep

        loc_dict = None
        lane_group = None

        if kind == 'ingress':
            lane_group = IngressLaneGroup

            loc_dict = {1: [self.center[0] - mid_square, self.center[1] + mid_square + sep],
                        2: [self.center[0] + mid_square + sep, self.center[1] + mid_square],
                        3: [self.center[0] + mid_square, self.center[1] - mid_square - sep],
                        4: [self.center[0] - mid_square - sep, self.center[1] - mid_square]}


        elif kind == 'egress':
            lane_group = EgressLaneGroup

            loc_dict = {1: [self.center[0] + mid_square, self.center[1] + mid_square + sep],
                        2: [self.center[0] + mid_square + sep, self.center[1] - mid_square],
                        3: [self.center[0] - mid_square, self.center[1] - mid_square - sep],
                        4: [self.center[0] - mid_square - sep, self.center[1] + mid_square]}

        group_order = eval(f'self.req_{kind}_groups')

        group_order += [None] * (4 - len(group_order))

        self.turn_intersection(group_order)

        groups = [lane_group(group, 10, self.lane_df, loc_dict[i + 1], kind, self, i) if group is not None else None for
                  i, group in
                  enumerate(group_order)]

        return groups

    def turn_intersection(self, lst):

        def swap(i1, i2, lst):
            lst[i1], lst[i2] = lst[i2], lst[i1]

            return lst

        for i in self.turn_instructions:
            lst = swap(i[0], i[1], lst)

        return lst

    def set_lane_df(self):

        self.lane_df = pd.DataFrame([x for x in
                                     self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry'][
                                         'laneSet'][
                                         'genericLane'] if
                                     x['laneAttributes']['sharedWith'][3] == '1' and x['laneAttributes']['sharedWith'][
                                         7] == '0'])

    def fill_intersection(self):

        self.lane_df = None
        self.set_lane_df()
        self.req_ingress_groups = self.set_group_numbers('ingress')
        self.req_egress_groups = self.set_group_numbers('egress')

        # calculate the max amount of lanes next to each other for this intersection
        lanes_per_group = [
            [len(list(self.lane_df[['laneID']][self.lane_df[f'{kind}Approach'].astype(str) == str(int(i))]['laneID']))
             for i in range(1, 5)] for kind in ['ingress', 'egress']]
        self.max_group_width = max([lanes_per_group[0][i] + lanes_per_group[1][i] for i in range(4)])

        self.mid_square = self.max_group_width - 2
        self.sep = 1
        self.ingress_groups = self.set_lane_groups('ingress')
        self.egress_groups = self.set_lane_groups('egress')


class LaneGroup:
    def __init__(self, ID, length, color, lane_df, loc, kind, intersection, position):

        self.ID = ID
        self.position = position
        self.length = length
        self.color = color
        self.lane_df = lane_df
        self.lon = loc[0]
        self.lat = loc[1]
        self.kind = kind
        self.intersection = intersection
        self.lanes = None
        self.get_lanes()
        self.width = len(self.lanes)
        self.order_lanes()

    def order_lanes(self):
        """ changes the order of the lanes based on 'maneuvers' in the XML file

        Args:
            flip: reverses the egress lane list

        """

        flip = self.intersection.flip

        if self.kind == 'ingress':

            rev = False
        elif self.kind == 'egress':

            rev = flip

        if self.position == 0 or self.position == 2:

            self.lanes.sort(key=lambda x: x.lon, reverse=rev)
        elif self.position == 1 or self.position == 3:
            self.lanes.sort(key=lambda x: x.lat, reverse=rev)

    def get_lane_connections(self, lane_id):
        """ gets a dictionary of lane connections for a specific lane

        Args:
            lane_id: the id of the lane

        Returns: a dictionary of lane connections

        """

        xml = self.intersection.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['laneSet'][
            'genericLane']

        ingress_dict = {}
        for x in xml:

            if x['laneAttributes']['sharedWith'][3] == '1':

                try:
                    ingress_dict[int(x['laneID'])] = [
                        {'connecting_lane': x['connectsTo']['connection']['connectingLane']['lane'],
                         'maneuver': x['connectsTo']['connection']['connectingLane']['maneuver']}]
                except TypeError:

                    temp_list = []
                    for i in x['connectsTo']['connection']:
                        temp_list.append({'connecting_lane': i['connectingLane']['lane'],
                                          'maneuver': i['connectingLane']['maneuver']})
                    ingress_dict[int(x['laneID'])] = temp_list
                except KeyError:
                    pass

        egress_dict = {}
        for k, v in ingress_dict.items():

            for i in v:

                payload = {'connecting_lane': k, 'maneuver': i['maneuver']}

                if payload['maneuver'] == '010000000000':
                    payload['maneuver'] = '001000000000'
                elif payload['maneuver'] == '001000000000':
                    payload['maneuver'] = '010000000000'

                try:
                    egress_dict[int(i['connecting_lane'])].append(payload)
                except KeyError:
                    egress_dict[int(i['connecting_lane'])] = [payload]
        try:
            return eval(f"{self.kind}_dict[lane_id]")
        except KeyError:
            return None

    def get_lanes(self):
        """ create lanes based on the xml-file

        """
        df = self.lane_df

        lane_numbers = list(df[['laneID']][df[f'{self.kind}Approach'].astype(str) == str(int(self.ID))]['laneID'])

        lanes = [Lane(x, self.color, self.kind, self.get_lane_connections(int(x)), self.intersection,
                      list(self.lane_df[self.lane_df['laneID'] == f'{x}']['nodes'])[0]['nodeXY'][0]['node-LatLon'][
                          'lat'],
                      list(self.lane_df[self.lane_df['laneID'] == f'{x}']['nodes'])[0]['nodeXY'][0]['node-LatLon'][
                          'lon'],
                      list(df[['laneID', 'laneAttributes']][df['laneID'] == str(x)]['laneAttributes'])[0]['sharedWith'])
                 for x in
                 lane_numbers]

        self.lanes = lanes


class Lane:

    def __init__(self, ID, color, kind, connections, intersection, lat, lon, shared_with):
        self.lat = lat
        self.lon = lon
        self.ID = ID
        self.color = color
        self.shared_with = shared_with
        self.bus = None
        self.intersection = intersection
        self.kind = kind
        self.connections = connections
        self.shape = 'rect'
        self.layer = 0
        self.car_lists = [CarQueue(i) for i in range(2)]
        self.signal_group = None
        self.get_signal_group()

    def get_signal_group(self):
        xml_dict = \
            self.intersection.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['laneSet'][
                'genericLane']

        sig_dict = self.get_signalgroup_dict()

        for x in xml_dict:
            if self.ID == x['laneID']:

                try:
                    self.signal_group = TrafficLight(sig_dict[int(x['connectsTo']['connection']['signalGroup'])], self)
                except KeyError:
                    pass
                except TypeError:
                    self.signal_group = TrafficLight(sig_dict[int(x['connectsTo']['connection'][0]['signalGroup'])],
                                                     self)

    def get_signalgroup_dict(self):

        sg_xml = self.intersection.xml_dict
        signalgroups = \
            sg_xml['topology']['controlData']['controller']['controlUnits']['controlUnit']['controlledIntersections'][
                'controlledIntersection']['signalGroups']['sg']
        sg_id = []
        sg_name = []
        for sg in signalgroups:
            sg_id.append(int(sg['signalGroup']))
            sg_name.append(int(sg['name']))
        if len(sg_id) != len(sg_name):
            print("Length sg_ID and sg_name aren't equal, return nothing")
            return
        return dict(zip(sg_id, sg_name))


class TrafficLight:

    def __init__(self, id, lane):
        self.ID = id
        self.state = 'red'
        self.shape = 'circle'
        self.ticks_since_state_change = 0
        self.lane = lane

    def change_state(self, state):
        self.state = state


class Vehicle(Agent):

    def __init__(self, model):
        super().__init__(self, model)

        self.shape = 'DenBoschBusRoute/resources/images/clear.png'
        self.color = ''
        self.wait_time = 0

    def increase_wait_time(self):
        self.wait_time += 1


class Bus(Agent):

    def __init__(self, unique_id, weight, model):
        super().__init__(unique_id, model)
        self.weight = weight
        self.shape = 'DenBoschBusRoute/resources/images/bus.png'
        self.color = ''
        self.speed = 0
        self.layer = 2
        self.delete_agent = False
        self.crossed_intersection = False
        self.wait_time = 0

    def increase_wait_time(self):
        self.wait_time += 1


class CarQueue:

    def __init__(self, id):
        self.cars = []
        self.color = 'black'
        self.shape = 'DenBoschBusRoute/resources/images/clear.png'
        self.ID = id

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self):
        self.cars.pop(0)

    def clear_cars(self):
        self.cars.clear()


class EgressLaneGroup(LaneGroup):

    def __init__(self, ID, length, xml_dict, loc, kind, intersection, position, color='#bfc3c9'):
        LaneGroup.__init__(self, ID, length, color, xml_dict, loc, kind, intersection, position)
        self.color = color


class IngressLaneGroup(LaneGroup):

    def __init__(self, ID, length, xml_dict, loc, kind, intersection, position, color='black'):
        LaneGroup.__init__(self, ID, length, color, xml_dict, loc, kind, intersection, position)
        self.color = color


class FillerRoad:
    def __init__(self, id):
        self.color = 'grey'
        self.ID = id
        self.shape = 'rect'
        self.layer = 0


class VehicleGraveyard:

    def __init__(self, i):
        self.cars = []
        self.ID = i
        self.busses = []

    def add_car(self, car):
        self.cars.append(car)

    def add_bus(self, car):
        self.busses.append(car)
