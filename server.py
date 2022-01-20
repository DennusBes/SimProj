import pandas as pd
import xmltodict
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid

import Lane
from CarQueue import CarQueue
from Intersection import Intersection
from RoadModel import RoadModel
from TrafficLight import TrafficLight


def lane_draw(agent):
    """ draw agents on the Mesa canvas

    Args:
        agent: the agent that gets drawn on the canvas

    """

    if isinstance(agent, Lane.Lane):
        text = ''
    elif isinstance(agent, CarQueue):
        text = len(agent.cars)

    elif isinstance(agent, TrafficLight):

        return {"Shape": agent.shape, 'r': 1, "Filled": "true", "Layer": 2, "Color": agent.state,
                'text': agent.ID, 'text_color': 'white'}
    else:
        text = ''

    if agent.shape == 'rect':

        return {"Shape": agent.shape, "w": 0.9, 'h': 0.9, "Filled": "true", "Layer": 0, "Color": agent.color,
                'text': text, 'text_color': 'white'}
    else:

        return {"Shape": agent.shape, 'r': 1, "Filled": "true", "Layer": 1, "Color": agent.color,
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


dimensions = (101, 101)

# {'1': '3', '3': '1', '2':'4'}
intersection = Intersection(xml_to_dict('7919015E_BOS211_ITF_COMPLETE.xml'),
                            pd.read_csv('BOS211.csv', sep=';', low_memory=False), dimensions, False,
                            [[6, 7, 9], [9, 10], [5, 6, 11, 26, 36], [6, 11, 26, 37], [6, 7], [5, 11, 26, 36],
                             [5, 11, 26, 36, 37], [5, 6, 11, 26, 36, 37], [6, 9], [5, 6, 26], [11, 26, 37],
                             [10, 24, 35], [5, 6], [6, 11, 26, 36], [24, 35, 38], [7, 9], [5, 11, 26, 37],
                             [10, 24, 35, 38], [5, 26], [6, 11, 26, 36, 37], [6, 11], [5, 6, 11, 26, 37], [10, 24],
                             [5, 6, 11], [10, 24, 28, 38], [28, 38], [6, 26], [5, 6, 11, 26], [11, 24, 26, 36], [5, 11],
                             [24, 28, 38], [11, 26], [24, 26, 35], [11, 24, 26, 28, 35, 36, 37, 38], [6, 11, 26],
                             [24, 26, 28, 35], [5, 11, 26], [11, 24, 26, 36, 37], [11, 26, 36], [10, 24, 28, 35, 38],
                             [11, 26, 36, 37], [11, 24, 26, 37], [24, 28, 35, 38], [5, 11, 36], [24, 35], [10, 24, 28],
                             [5, 6, 11, 36], [11, 24, 26, 28, 35, 38], [24, 26], [5, 6, 26, 37], [11, 24, 28, 35, 38],
                             [9, 10, 28], [11, 24, 26, 28, 35, 36, 38], [11, 24, 26], [11, 24, 35], [10, 24, 28, 35],
                             [24, 28], [11, 24, 26, 35, 37], [9, 28], [11, 24], [24, 26, 35, 38], [11, 36],
                             [11, 24, 26, 35, 36, 37, 38], [11, 24, 26, 35, 36], [6, 26, 37], [6, 11, 36], [5, 28],
                             [11, 24, 28, 38], [5, 11, 26, 28, 36, 37], [5, 26, 28], [11, 24, 26, 28, 35, 37, 38],
                             [11, 24, 26, 35, 37, 38], [11, 24, 26, 35], [11, 26, 28, 36], [11, 24, 36],
                             [5, 11, 28, 38], [11, 26, 28, 36, 38], [5, 26, 37], [10, 28, 38], [11, 24, 26, 28, 38],
                             [9, 10, 28, 38], [5, 28, 38], [24, 26, 28, 35, 38], [11, 24, 26, 28, 37, 38], [26, 28, 38],
                             [5, 11, 26, 28], [11, 24, 26, 28, 36, 37, 38], [24, 28, 35], [11, 24, 26, 35, 36, 37],
                             [7, 9, 28], [5, 11, 26, 28, 36, 37, 38], [11, 26, 28, 37, 38], [11, 24, 26, 35, 38],
                             [26, 37], [9, 28, 38], [5, 11, 26, 28, 37], [11, 24, 26, 28, 36, 38], [24, 26, 28, 38],
                             [26, 28], [11, 24, 35, 38], [11, 24, 26, 28, 35, 36, 37], [7, 28],
                             [11, 24, 26, 28, 35, 36], [11, 28, 38], [5, 11, 28], [11, 26, 28, 37], [10, 28],
                             [11, 24, 26, 28, 36, 37], [5, 11, 26, 28, 36], [11, 24, 26, 28, 35],
                             [5, 11, 26, 28, 37, 38], [5, 26, 28, 38]],
                            {'1': '2', '2': '3', '3': '4'})

intersection2 = Intersection(xml_to_dict('79190154_BOS210_ITF_COMPLETE.xml'),
                             pd.read_csv('BOS210.csv', sep=';', low_memory=False), dimensions, True,
                             [[12, 22, 24, 32, 37], [3, 24], [4, 5, 12], [4, 5], [1, 3], [5, 11], [4, 12, 31], [3, 4],
                              [3, 4, 5], [1, 3, 24], [11, 38], [12, 24], [3, 5], [12, 22], [4, 5, 12, 31], [4, 5, 38],
                              [4, 12], [3, 38], [5, 11, 38], [12, 31], [12, 22, 31, 32], [5, 12], [1, 3, 22], [24, 37],
                              [12, 22, 24], [5, 38], [1, 22], [3, 4, 5, 38], [1, 3, 22, 24, 32, 37], [4, 5, 12, 28, 31],
                              [5, 12, 28, 31], [1, 38], [12, 24, 31], [1, 24], [1, 3, 22, 24], [3, 5, 38],
                              [3, 4, 5, 28], [22, 24], [3, 22, 24], [12, 28], [1, 3, 22, 24, 32], [12, 22, 31],
                              [22, 24, 32, 37], [1, 22, 24], [5, 12, 31], [12, 22, 28], [5, 28], [3, 22], [5, 11, 28],
                              [1, 22, 24, 32], [12, 24, 28], [12, 28, 31], [4, 5, 12, 28], [1, 3, 38], [12, 22, 32],
                              [4, 12, 28, 31], [12, 22, 24, 31], [22, 32], [12, 22, 24, 32], [3, 22, 24, 32],
                              [1, 24, 37], [5, 12, 28], [4, 28], [12, 22, 28, 31], [4, 38], [1, 22, 24, 32, 37],
                              [12, 24, 28, 31], [1, 3, 24, 37], [3, 4, 38], [12, 22, 24, 31, 37], [1, 3, 22, 24, 37],
                              [3, 22, 28], [12, 24, 37], [22, 24, 32], [4, 5, 28], [4, 12, 28], [12, 22, 24, 28, 31],
                              [11, 28], [1, 3, 22, 32], [3, 22, 32], [22, 24, 37], [12, 22, 24, 37], [3, 22, 24, 37],
                              [3, 5, 28], [12, 22, 24, 28], [3, 4, 28], [1, 22, 32], [3, 28], [3, 22, 24, 32, 37],
                              [12, 22, 24, 31, 32], [3, 24, 37], [22, 28], [1, 22, 24, 37],
                              [12, 22, 24, 28, 31, 32, 37], [12, 22, 24, 28, 31, 32]]
                             ,
                             {'1': '2', '2': '3', '3': '4'})

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
