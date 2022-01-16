from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from Intersection import Intersection
from SensorModel import SensorModel
from RoadModel import RoadModel

import xmltodict


def sensor_draw(agent):
    return {"Shape": "rect", "w": 0.9, 'h':0.9, "Filled": "true", "Layer": 0, "Color": agent.color,
            'text': agent.ID, 'text_color': 'white'}


def xml_to_dict(filename):
    with open(filename) as t:
        data = t.read()
        xmldict = xmltodict.parse(data)
    return xmldict


xmldict = xml_to_dict('79190154_BOS210_ITF_COMPLETE.xml')

dimensions = (100, 100)
# {'1': '3', '3': '1', '2':'4'}
intersection = Intersection(xmldict, dimensions, {'1': '3', '3': '1', '2':'4'})

dim = intersection.dimensions

canvas_element = CanvasGrid(sensor_draw, dim[0], dim[1], (dim[0] * 10), (dim[1] * 10))

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
