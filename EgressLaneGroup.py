from LaneGroup import LaneGroup

class EgressLaneGroup(LaneGroup):

    def __init__(self, ID, length, xml_dict, loc, kind, intersection, color = '#bfc3c9'):
        LaneGroup.__init__(self, ID, length, color, xml_dict, loc, kind, intersection)
        self.color = color


