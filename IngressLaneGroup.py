from LaneGroup import LaneGroup

class IngressLaneGroup(LaneGroup):

    def __init__(self, ID, length, xml_dict, loc, kind,intersection, position, color = 'black'):
        LaneGroup.__init__(self, ID, length, color, xml_dict, loc, kind, intersection, position)
        self.color = color


