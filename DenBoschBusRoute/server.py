import xmltodict
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule

from DenBoschBusRoute.agent import CarQueue
from DenBoschBusRoute.agent import ConnectedIntersections
from DenBoschBusRoute.agent import Intersection
from DenBoschBusRoute.agent import Lane
from DenBoschBusRoute.agent import TrafficLight
from DenBoschBusRoute.model import RoadModel
from DenBoschBusRoute.utils import calculate_yellow_light, calculate_red_clearance_interval


def lane_draw(agent):
    """ draw agents on the Mesa canvas

    Args:
        agent: the agent that gets drawn on the canvas

    """

    if isinstance(agent, Lane):
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


dimensions = (90, 90)

# {'1': '3', '3': '1', '2':'4'}
intersection2 = Intersection(xml_to_dict('DenBoschBusRoute/resources/data/7919015E_BOS211_ITF_COMPLETE.xml'), False,
                             [[6, 7, 9], [9, 10], [5, 6, 11, 26, 36], [6, 11, 26, 37], [6, 7], [5, 11, 26, 36],
                              [5, 11, 26, 36, 37], [5, 6, 11, 26, 36, 37], [6, 9], [5, 6, 26], [11, 26, 37],
                              [10, 24, 35], [5, 6], [6, 11, 26, 36], [24, 35, 38], [7, 9], [5, 11, 26, 37],
                              [10, 24, 35, 38], [5, 26], [6, 11, 26, 36, 37], [6, 11], [5, 6, 11, 26, 37], [10, 24],
                              [5, 6, 11], [10, 24, 28, 38], [28, 38], [6, 26], [5, 6, 11, 26], [11, 24, 26, 36],
                              [5, 11],
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
                              [9, 10, 28, 38], [5, 28, 38], [24, 26, 28, 35, 38], [11, 24, 26, 28, 37, 38],
                              [26, 28, 38],
                              [5, 11, 26, 28], [11, 24, 26, 28, 36, 37, 38], [24, 28, 35], [11, 24, 26, 35, 36, 37],
                              [7, 9, 28], [5, 11, 26, 28, 36, 37, 38], [11, 26, 28, 37, 38], [11, 24, 26, 35, 38],
                              [26, 37], [9, 28, 38], [5, 11, 26, 28, 37], [11, 24, 26, 28, 36, 38], [24, 26, 28, 38],
                              [26, 28], [11, 24, 35, 38], [11, 24, 26, 28, 35, 36, 37], [7, 28],
                              [11, 24, 26, 28, 35, 36], [11, 28, 38], [5, 11, 28], [11, 26, 28, 37], [10, 28],
                              [11, 24, 26, 28, 36, 37], [5, 11, 26, 28, 36], [11, 24, 26, 28, 35],
                              [5, 11, 26, 28, 37, 38], [5, 26, 28, 38]], [[2, 3], [1, 2], [0, 1]])

intersection1 = Intersection(xml_to_dict('DenBoschBusRoute/resources/data/79190154_BOS210_ITF_COMPLETE.xml'), True,
                             [[5, 11], [3, 22], [1, 3, 22, 24, 41], [3, 4, 5], [4, 5, 41], [3, 5, 38], [3, 4],
                              [5, 12, 28, 31], [3, 5], [4, 5], [1, 3, 24], [5, 41], [1, 3, 41], [5, 11, 41], [3, 41],
                              [1, 3], [11, 38, 41], [4, 12], [4, 5, 12, 41], [11, 41], [1, 3, 24, 41], [4, 5, 12],
                              [4, 12, 31], [5, 12, 31], [3, 4, 5, 28, 41], [4, 12, 41], [3, 4, 41], [1, 24],
                              [4, 5, 12, 28, 31], [3, 5, 41], [5, 12, 28], [5, 11, 38], [3, 24], [1, 3, 22],
                              [3, 4, 5, 41], [11, 38], [12, 41], [5, 11, 38, 41], [4, 12, 31, 41], [12, 31], [12, 24],
                              [5, 38, 41], [3, 38, 41], [4, 41], [5, 12], [3, 24, 37], [4, 5, 12, 28, 31, 41],
                              [3, 4, 5, 38], [1, 22], [1, 41], [22, 24, 32, 37], [24, 41], [3, 22, 41], [3, 22, 24, 41],
                              [3, 4, 5, 38, 41], [3, 24, 41], [1, 22, 41], [1, 3, 22, 24], [5, 12, 41], [12, 22, 24],
                              [12, 28, 31], [1, 3, 22, 41], [22, 24], [1, 22, 24], [4, 12, 28, 31], [12, 24, 41],
                              [22, 24, 32], [1, 3, 22, 24, 32, 37, 41], [4, 5, 12, 31, 41], [3, 5, 38, 41], [38, 41],
                              [4, 38, 41], [12, 22, 24, 41], [4, 5, 12, 28], [5, 12, 31, 41], [1, 24, 41], [3, 4, 38],
                              [4, 5, 12, 28, 41], [1, 3, 22, 24, 32, 37], [3, 38], [1, 38, 41], [24, 37],
                              [1, 3, 22, 24, 37], [12, 22, 24, 28, 31, 32, 37], [4, 5, 12, 31], [5, 38], [3, 28],
                              [1, 3, 38, 41], [12, 31, 41], [1, 3, 38], [4, 5, 38], [3, 22, 24], [12, 22, 41],
                              [22, 24, 41], [12, 22, 24, 32, 41], [4, 5, 38, 41], [5, 11, 28], [22, 32],
                              [3, 22, 24, 32, 41], [22, 41], [1, 22, 24, 41], [12, 24, 28, 31], [22, 32, 41],
                              [1, 22, 24, 32, 37], [11, 28, 41], [12, 28], [12, 28, 41], [12, 24, 31, 41], [28, 41],
                              [12, 24, 28, 31, 41], [22, 24, 37, 41], [5, 11, 28, 41], [12, 22, 24, 31, 41], [4, 38],
                              [4, 28], [4, 5, 28, 41], [12, 22, 24, 31, 37, 41], [5, 12, 28, 31, 41], [3, 22, 32],
                              [12, 28, 31, 41], [5, 28], [22, 28], [4, 12, 28], [12, 24, 28], [1, 38], [5, 28, 41],
                              [1, 3, 24, 37, 41], [3, 22, 32, 41], [12, 22, 24, 28, 31], [1, 3, 22, 24, 32, 41],
                              [12, 22, 24, 31], [1, 3, 22, 24, 37, 41], [12, 22, 24, 32], [12, 22, 24, 32, 37],
                              [11, 28], [22, 28, 41], [1, 3, 22, 24, 32], [5, 12, 28, 41], [3, 4, 28],
                              [1, 22, 24, 32, 41], [12, 24, 31], [12, 22, 28, 31], [12, 22, 31, 41], [3, 4, 5, 28],
                              [12, 22], [3, 28, 41], [3, 22, 24, 32, 37, 41], [4, 12, 28, 31, 41], [1, 24, 37],
                              [12, 22, 31], [3, 22, 24, 32, 37], [3, 5, 28], [1, 3, 22, 32, 41], [22, 24, 37],
                              [1, 24, 37, 41], [12, 22, 24, 37], [1, 22, 24, 37, 41], [3, 22, 24, 37, 41],
                              [3, 5, 28, 41], [12, 22, 24, 28, 31, 32], [12, 22, 24, 31, 32], [1, 3, 24, 37],
                              [3, 4, 38, 41], [1, 22, 24, 32, 37, 41], [1, 22, 24, 32], [3, 22, 28], [12, 22, 32, 41],
                              [12, 22, 28], [4, 28, 41], [4, 5, 28], [12, 22, 32], [22, 24, 32, 41], [3, 22, 24, 32],
                              [22, 24, 32, 37, 41], [12, 22, 28, 41], [12, 24, 37], [12, 22, 24, 28, 31, 41],
                              [12, 22, 24, 28, 41], [12, 22, 31, 32], [3, 22, 28, 41], [3, 22, 24, 37], [3, 4, 28, 41],
                              [3, 24, 37, 41], [1, 22, 24, 37], [24, 37, 41], [1, 22, 32, 41], [12, 22, 24, 32, 37, 41],
                              [1, 22, 32], [1, 3, 22, 32], [12, 22, 31, 32, 41], [12, 24, 37, 41]], [[0,1],[1,3], [2,1]])

ci = ConnectedIntersections([intersection1, intersection2], dimensions, bus_lanes=[1, 12])

dim = dimensions

canvas_element = CanvasGrid(lane_draw, dim[0], dim[1], (dim[0] * 10), (dim[1] * 10))

chart = ChartModule(
    [
        {"Label": "cars_1", "Color": "Green"},
        {"Label": "cars_2", "Color": "Blue"},
        {"Label": "busses_1", "Color": "Red"},
        {"Label": "busses_2", "Color": "Orange"}
    ]
)

max_speed = int(intersection1.xml_dict['topology']['mapData']['intersections']['intersectionGeometry'][
                    'speedLimits']['regulatorySpeedLimit']['speed'])

yellow_light_duration = round(calculate_yellow_light(max_speed))
red_clearence_time = round(calculate_red_clearance_interval(max_speed, 52))

model_params = {
    'green_length': UserSettableParameter("number", "Green Light Duration", 36),
    'orange_length': UserSettableParameter("number", "Orange Light Duration", yellow_light_duration),
    'red_clearance_time': UserSettableParameter("number", "Red Clearance Duration", red_clearence_time),
    'bus_weight': UserSettableParameter("number", "Bus Weight", 5, ),
    'traffic_light_priority': UserSettableParameter('checkbox', 'traffic_light_priority', value=True),
    'ci': ci,
    'pity_timer_limit': UserSettableParameter("number", "Pity Timer Limit", 120),
    'car_spawn_rate': UserSettableParameter("number", "Car Spawn Rate (chance per tick)",
                                            round(0.04748553240740742, 4)),
    'car_despawn_rate': UserSettableParameter("number", "Car Despawn rate (every x ticks)", 3),

}

server = ModularServer(
    RoadModel,
    [canvas_element, chart],
    "Den Bosch Kruispunt",
    model_params
)
