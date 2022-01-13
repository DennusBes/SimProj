import pandas as pd
import numpy as np
from LaneGroup import LaneGroup
import random
from IngressLaneGroup import IngressLaneGroup
from EgressLaneGroup import EgressLaneGroup


class Intersection:

    def __init__(self, xml_dict, dimensions):

        self.xml_dict = xml_dict
        self.center = (dimensions[0] / 2, dimensions[1] / 2)
        self.dimensions = dimensions
        self.req_ingress_groups = self.set_group_numbers('ingress')
        self.req_egress_groups = self.set_group_numbers('egress')
        self.ingress_groups = self.set_lane_groups('ingress')
        self.egress_groups = self.set_lane_groups('egress')


    def set_group_numbers(self, kind):
        df = pd.DataFrame([x for x in
                           self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['laneSet'][
                               'genericLane'] if x['laneAttributes']['sharedWith'] == '0001000000'])



        #df = df.replace({'egressApproach': {'2': '4'}})
        #df = df.replace({'ingressApproach': {'2': '4'}})


        l = list(set(list(set(eval(f'df.{kind}Approach')))))
        l.remove(np.NaN)

        return sorted([int(x) for x in l])

    def set_lane_groups(self, kind):

        mid_square = 3

        if kind == 'ingress':
            lane_group = IngressLaneGroup

            loc_dict = {1: [self.center[0] - mid_square, self.center[1] + mid_square + 1],
                        2: [self.center[0] + mid_square + 1, self.center[1] + mid_square],
                        3: [self.center[0] + mid_square, self.center[1] - mid_square - 1],
                        4: [self.center[0] - mid_square - 1, self.center[1] - mid_square]}


        elif kind == 'egress':
            lane_group = EgressLaneGroup

            loc_dict = {1: [self.center[0] + mid_square, self.center[1] + mid_square + 1],
                        2: [self.center[0] + mid_square + 1, self.center[1] - mid_square],
                        3: [self.center[0] - mid_square, self.center[1] - mid_square - 1],
                        4: [self.center[0] - mid_square - 1, self.center[1] + mid_square]}


        check_list = eval(f'self.req_{kind}_groups')
        return [lane_group(i, 20, f'#{"%06x" % random.randint(0, 0xFFFFFF)}', self.xml_dict,
                           loc_dict[i], kind) if i in check_list else None for i in list(range(1,5))]
