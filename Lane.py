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

        sig_dict = self.get_signalgroup_dict()

        for x in xml_dict:
            if self.ID == x['laneID']:

                try:
                    self.signal_group = TrafficLight(sig_dict[int(x['connectsTo']['connection']['signalGroup'])], self)
                except KeyError:
                    pass
                except TypeError:
                    self.signal_group = TrafficLight(sig_dict[int(x['connectsTo']['connection'][0]['signalGroup'])],self)

    def get_signalgroup_dict(self):

        sg_xml = self.intersection.xml_dict
        signalgroups = \
            sg_xml['topology']['controlData']['controller']['controlUnits']['controlUnit']['controlledIntersections'][
                'controlledIntersection']['signalGroups']['sg']
        sg_id = []
        sg_name = []
        for sg in signalgroups:
            sg_id.append(int(sg['signalGroup']))
            sg_name.append(int(sg['name']))
        if len(sg_id) != len(sg_name):
            print("Length sg_ID and sg_name aren't equal, return nothing")
            return
        return dict(zip(sg_id, sg_name))
