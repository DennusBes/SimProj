from mesa import Agent

from FillerRoad import FillerRoad


class Vehicle(Agent):

	def __init__(self, unique_id, model):
		super().__init__(unique_id, model)
		self.shape = 'bus.png'
		self.color = ''

