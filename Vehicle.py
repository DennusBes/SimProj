from mesa import Agent

from FillerRoad import FillerRoad


class Vehicle(Agent):

	def __init__(self,  model):
		super().__init__(self, model)

		self.shape = 'clear.png'
		self.color = ''
		self.wait_time = 0

	def increase_wait_time(self):
		self.wait_time += 1