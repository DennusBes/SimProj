from Lane import Lane


class LaneGroup:
    def __init__(self, ID, length, color, lane_df, loc, kind, intersection):

        self.ID = ID
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

        #22
        #for i in (self.lanes):
        #    print(i.connections)
        #print()



        self.order_lanes()


    def order_lanes(self):
        """ changes the order of the lanes based on 'maneuvers' in the XML file

        Args:
            flip: reverses the ingress lane list

        """

        flip = self.intersection.flip

        left = []
        right = []
        straight = []
        left_straight = []
        right_straight = []

        for lane in self.lanes:

            if lane.connections is not None:

                maneuvers = list(set([p['maneuver'] for p in lane.connections]))

                if '010000000000' in maneuvers:
                    if '100000000000' in maneuvers:
                        right_straight.append(lane)
                        continue
                    right.append(lane)

                elif '001000000000' in maneuvers:
                    if '100000000000' in maneuvers:
                        left_straight.append(lane)
                        continue
                    left.append(lane)

                elif '100000000000' in maneuvers:
                    straight.append(lane)

        if self.kind == 'ingress':

            self.lanes = right + right_straight + straight + left_straight + left
            if flip:
                self.lanes = self.lanes[::-1]
        else:
            self.lanes = right[::-1] + right_straight[::-1] + straight[::-1] + left_straight[::-1] + left[::-1]

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
                    #print(x['laneID'],x)

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
        lanes = [Lane(x, self.color, self.kind, self.get_lane_connections(int(x)), self.intersection) for x in
                 lane_numbers]

        self.lanes = lanes
