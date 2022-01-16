import pandas as pd
import numpy as np
from Lane import Lane


class LaneGroup:
    def __init__(self, ID, length, color, lane_df, loc, kind):

        self.ID = ID
        self.length = length
        self.color = color
        self.lane_df = lane_df
        self.lon = loc[0]
        self.lat = loc[1]
        self.kind = kind
        self.lanes = self.get_lanes()
        self.width = len(self.lanes)

    def get_lanes(self):
        df = self.lane_df

        lane_numbers = list(df[['laneID']][df[f'{self.kind}Approach'].astype(str) == str(int(self.ID))]['laneID'])

        return [Lane(x, self.color) for x in lane_numbers]
