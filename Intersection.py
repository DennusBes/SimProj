import numpy as np
import pandas as pd

from EgressLaneGroup import EgressLaneGroup
from IngressLaneGroup import IngressLaneGroup


class Intersection:

    def __init__(self, xml_dict, activation_df, dimensions, manipulation=None):

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
        self.traffic_light_combos = [['07', '09'], ['09', '10'], ['05', '06'], ['06', '26'], ['05', '06', '11', '26', '36'], ['05', '11', '26', '36', '37'], ['11', '26', '36'], ['05', '11', '26', '37'], ['06', '07', '09'], ['24', '28', '38'], ['05', '11', '26', '36'], ['09', '10', '28'], ['05', '11'], ['24', '35'], ['24', '35', '38'], ['05', '06', '11', '26', '36', '37'], ['05', '06', '26'], ['05', '06', '11'], ['11', '26', '37'], ['05', '06', '11', '26', '37'], ['06', '07'], ['06', '11', '26', '36'], ['11', '24', '26', '28', '35', '36', '37', '38'], ['05', '26'], ['06', '09'], ['10', '24', '35'], ['10', '24'], ['11', '26'], ['06', '11', '26', '37'], ['06', '11', '26', '36', '37'], ['11', '26', '36', '37'], ['10', '24', '28', '38'], ['10', '24', '35', '38'], ['24', '28', '35', '38'], ['05', '06', '11', '26'], ['09', '28'], ['05', '11', '26', '28'], ['11', '24', '26', '28', '35', '36', '38'], ['05', '11', '26', '28', '37'], ['11', '24', '26'], ['06', '11'], ['10', '24', '28', '35', '38'], ['06', '11', '26'], ['05', '06', '11', '36'], ['24', '26', '35'], ['11', '24', '26', '36'], ['05', '11', '26', '28', '36', '37'], ['11', '24', '26', '36', '37'], ['11', '24', '36'], ['10', '24', '28'], ['05', '11', '26'], ['05', '28'], ['24', '26'], ['11', '24', '35'], ['05', '11', '36'], ['11', '24', '26', '37'], ['24', '26', '28', '38'], ['11', '24', '26', '28', '36', '38'], ['11', '24'], ['24', '28', '35'], ['24', '26', '35', '38'], ['28', '38'], ['05', '26', '37'], ['11', '24', '26', '28', '35', '37', '38'], ['11', '24', '26', '35', '36', '37'], ['24', '28'], ['10', '28', '38'], ['11', '24', '26', '28', '35', '38'], ['11', '24', '26', '35', '37'], ['11', '24', '28', '35', '38'], ['11', '24', '26', '28', '37', '38'], ['11', '24', '26', '35', '38'], ['11', '24', '26', '35'], ['05', '06', '26', '37'], ['24', '26', '28', '35', '38'], ['05', '11', '28', '38'], ['11', '36'], ['06', '26', '37'], ['11', '24', '26', '35', '36', '37', '38'], ['11', '24', '26', '35', '36'], ['05', '11', '26', '28', '36', '37', '38'], ['10', '24', '28', '35'], ['11', '24', '26', '35', '37', '38'], ['09', '10', '28', '38'], ['11', '24', '26', '28', '36', '37', '38'], ['11', '26', '28', '37'], ['05', '11', '28'], ['05', '26', '28'], ['06', '11', '36'], ['11', '24', '35', '38'], ['11', '24', '26', '28', '35', '36', '37'], ['11', '26', '28', '36', '38'], ['11', '28', '38'], ['11', '26', '28', '37', '38'], ['09', '28', '38'], ['10', '28'], ['26', '28'], ['05', '28', '38'], ['26', '37'], ['11', '24', '28', '38'], ['24', '26', '28'], ['26', '28', '38'], ['24', '26', '28', '35'], ['11', '24', '26', '28', '35', '36'], ['07', '09', '28'], ['11', '24', '26', '28', '38'], ['11', '24', '26', '28', '36', '37'], ['11', '24', '28'], ['05', '26', '28', '38'], ['24', '26', '37'], ['07', '28'], ['11', '24', '26', '28', '35'], ['11', '24', '26', '35', '36', '38'], ['11', '26', '28', '36'], ['05', '11', '26', '28', '37', '38']]
        #self.get_traffic_combos()

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

    def get_traffic_combos(self):

        df = self.activation_df
        df = df.sample(frac = 0.5)

        combos = []
        for index, row in df.iterrows():
            r = list(row[df.columns])
            if (r.count('#') > 1):
                combo = [ind for ind in row.index if row[ind] == '#']
                if combo not in combos:
                    combos.append(combo)
        print(combos)
        self.traffic_light_combos =  combos
