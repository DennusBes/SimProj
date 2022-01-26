from mesa import Agent

from FillerRoad import FillerRoad


class Vehicle(Agent):

	def __init__(self,  model):
		super().__init__(self, model)

		self.shape = 'bus.png'
		self.color = ''

