from CarQueue import CarQueue
from TrafficLight import TrafficLight


class Lane:

    def __init__(self, ID, color, kind, connections, intersection):
        self.ID = ID
        self.color = color
        self.intersection = intersection
        self.kind = kind
        self.connections = connections
        self.shape = 'rect'
        self.layer = 0
        self.car_lists = [CarQueue(i) for i in range(2)]
        self.signal_group = None
        self.get_signal_group()

    def get_signal_group(self):
        xml_dict = \
            self.intersection.xml_dict['topology']['mapData']['intersections']['intersectionGeometry']['laneSet'][
                'genericLane']

        for x in xml_dict:
            if self.ID == x['laneID']:


                try:
                    print(x['laneID'], x['connectsTo']['connection'])
                    self.signal_group = TrafficLight(int(x['connectsTo']['connection']['signalGroup']), self)
                except KeyError:
                    pass
                except TypeError:
                    self.signal_group = TrafficLight(int(x['connectsTo']['connection'][0]['signalGroup']),self)
