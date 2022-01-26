import numpy as np
import pandas as pd

from EgressLaneGroup import EgressLaneGroup
from IngressLaneGroup import IngressLaneGroup


class Intersection:

    def __init__(self, xml_dict, flip, trafic_light_combos, turn_instructions = []):

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
