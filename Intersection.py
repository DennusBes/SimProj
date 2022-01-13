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
        self.req_ingress_groups = self.set_number_of_groups('ingress')
        self.req_egress_groups = self.set_number_of_groups('egress')
        self.ingress_groups = self.set_lane_groups('ingress')
        self.egress_groups = self.set_lane_groups('egress')

    def set_number_of_groups(self, kind):
        df = pd.DataFrame([x for x in
                           self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['laneSet'][
                               'genericLane'] if x['laneAttributes']['sharedWith'] == '0001000000'])

        l = list(set(list(set(eval(f'df.{kind}Approach')))))
        l.remove(np.NaN)

        return len(l)

    def set_lane_groups(self, kind):

        mid_square = 3

        if kind == 'ingress':
            lane_group = IngressLaneGroup

            loc_dict = {0: [self.center[0] - mid_square, self.center[1] + mid_square + 1],
                        1: [self.center[0] + mid_square + 1, self.center[1] + mid_square],
                        2: [self.center[0] + mid_square, self.center[1] - mid_square - 1],
                        3: [self.center[0] - mid_square - 1, self.center[1] - mid_square]}


        elif kind == 'egress':
            lane_group = EgressLaneGroup

            loc_dict = {0: [self.center[0] + mid_square, self.center[1] + mid_square + 1],
                        1: [self.center[0] + mid_square + 1, self.center[1] - mid_square],
                        2: [self.center[0] - mid_square, self.center[1] - mid_square - 1],
                        3: [self.center[0] - mid_square - 1, self.center[1] + mid_square]}

        return [lane_group(i + 1, 41, f'#{"%06x" % random.randint(0, 0xFFFFFF)}', self.xml_dict,
                           loc_dict[i], kind) for i in
                range(eval(f'self.req_{kind}_groups'))]
