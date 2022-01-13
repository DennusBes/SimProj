import pandas as pd
import numpy as np
from Lane import Lane


class LaneGroup:
    def __init__(self, ID, length, color, xml_dict, loc, kind):
        self.ID = ID
        self.length = length
        self.color = color
        self.xml_dict = xml_dict
        self.lon = loc[0]
        self.lat = loc[1]
        self.kind = kind
        self.lanes = self.get_lanes()

    def get_lanes(self):
        df = pd.DataFrame([x for x in
                           self.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['laneSet'][
                               'genericLane'] if x['laneAttributes']['sharedWith'] == '0001000000'])

        # df = df.replace({'egressApproach': {'2': '4'}})
        # df = df.replace({'ingressApproach': {'2': '4'}})

        lane_numbers = list(df[['laneID']][df[f'{self.kind}Approach'].astype(str) == str(int(self.ID))]['laneID'])

        return [Lane(x) for x in lane_numbers]
