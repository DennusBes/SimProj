import pandas as pd
import numpy as np
import random
from IngressLaneGroup import IngressLaneGroup
from EgressLaneGroup import EgressLaneGroup


class Intersection:

    def __init__(self, xml_dict, dimensions, manipulation=None):

        self.xml_dict = xml_dict
        self.center = (dimensions[0] / 2, dimensions[1] / 2)
        self.dimensions = dimensions
        self.lane_df = None
        self.manipulate_intersection(manipulation)
        self.req_ingress_groups = self.set_group_numbers('ingress')
        self.req_egress_groups = self.set_group_numbers('egress')

        # calculate the max amount of lanes next to each other for this intersection
        lanes_per_group = [
            [len(list(self.lane_df[['laneID']][self.lane_df[f'{kind}Approach'].astype(str) == str(int(i))]['laneID']))
             for i in range(1, 5)] for kind in ['ingress', 'egress']]
        self.max_group_width = max([lanes_per_group[0][i] + lanes_per_group[1][i] for i in range(4)])
        self.ingress_groups = self.set_lane_groups('ingress')
        self.egress_groups = self.set_lane_groups('egress')

    def manipulate_intersection(self, change):

        self.lane_df = pd.DataFrame([x for x in
                                     self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry'][
                                         'laneSet'][
                                         'genericLane'] if x['laneAttributes']['sharedWith'] == '0001000000'])

        self.lane_df = self.lane_df.replace(
            {'ingressApproach': change, 'egressApproach': change})

    def set_group_numbers(self, kind):

        gn = list(set(list(set(eval(f'self.lane_df.{kind}Approach')))))
        gn.remove(np.NaN)

        return sorted([int(x) for x in gn])

    def set_lane_groups(self, kind):

        mid_square = self.max_group_width - 2
        sep = 2

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

        check_list = eval(f'self.req_{kind}_groups')
        return [lane_group(i, 46, self.lane_df,
                           loc_dict[i], kind, self) if i in check_list else None for i in list(range(1, 5))]
