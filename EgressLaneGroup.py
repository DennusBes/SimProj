from LaneGroup import LaneGroup

class EgressLaneGroup(LaneGroup):

    def __init__(self, ID, length, color, xml_dict, loc, kind):
        LaneGroup.__init__(self, ID, length, color, xml_dict, loc, kind)
        self.color = 'red'


