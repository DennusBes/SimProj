from Lane import Lane


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
