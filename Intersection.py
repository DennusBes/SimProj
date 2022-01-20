import numpy as np
import pandas as pd

from EgressLaneGroup import EgressLaneGroup
from IngressLaneGroup import IngressLaneGroup


class Intersection:

    def __init__(self, xml_dict, activation_df, dimensions, flip, trafic_light_combos, manipulation=None):

        self.flip = flip
        self.xml_dict = xml_dict
        self.activation_df = activation_df
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

        self.mid_square = self.max_group_width - 2
        self.sep = 1
        self.ingress_groups = self.set_lane_groups('ingress')
        self.egress_groups = self.set_lane_groups('egress')
        self.traffic_light_combos = trafic_light_combos

    def manipulate_intersection(self, change):
        """ change the position on lanegroups on the intersection

        Args:
            change: a dictionary of what lanegroups should be swapped

        """

        self.lane_df = pd.DataFrame([x for x in
                                     self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry'][
                                         'laneSet'][
                                         'genericLane'] if x['laneAttributes']['sharedWith'][3] == '1'])

        self.lane_df = self.lane_df.replace(
            {'ingressApproach': change, 'egressApproach': change})

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

        check_list = eval(f'self.req_{kind}_groups')
        return [lane_group(i, 46, self.lane_df,
                           loc_dict[i], kind, self) if i in check_list else None for i in list(range(1, 5))]
