import xmltodict
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid

import Lane
from Intersection import Intersection
from RoadModel import RoadModel


def lane_draw(agent):
    """ draw agents on the Mesa canvas

    Args:
        agent: the agent that gets drawn on the canvas

    """

    if isinstance(agent, Lane.Lane):
        text = agent.ID
    else:
        text = ''

    if agent.shape == 'rect':

        return {"Shape": agent.shape, "w": 0.9, 'h':0.9, "Filled": "true", "Layer": 0, "Color": agent.color,
            'text': text, 'text_color': 'white'}
    else:

        return {"Shape": agent.shape,'r': 1, "Filled": "true", "Layer": 1, "Color": agent.color,
                'text': text, 'text_color': 'white'}


def xml_to_dict(filename):
    """convert the xml-file to a pyhton dict

    Args:
        filename: root of the xml-file

    Returns: python dictionary of the xml-file

    """
    with open(filename) as t:
        data = t.read()
        xmldict = xmltodict.parse(data)
    return xmldict



xmldict = xml_to_dict('79190154_BOS210_ITF_COMPLETE.xml')

dimensions = (101, 101)

# {'1': '3', '3': '1', '2':'4'}
intersection = Intersection(xmldict, dimensions, {'1':'2', '2':'3', '3':'4'})

dim = intersection.dimensions

canvas_element = CanvasGrid(lane_draw, dim[0], dim[1], (dim[0] * 10), (dim[1] * 10))

model_params = {
    "length": UserSettableParameter("number", "Road length", 10),
    "intersection": intersection
}

server = ModularServer(
    RoadModel,
    [canvas_element],
    "Den Bosch Kruispunt",
    model_params
)
