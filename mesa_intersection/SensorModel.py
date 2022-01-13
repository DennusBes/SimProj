from mesa import Model
from mesa.space import SingleGrid
import numpy as np

class SensorModel(Model):
	"""
	Model class for the Nagel-Schreckenberg Car model.
	"""


	def __init__(self, length, ingress, intersection):
		"""
		"""

		super().__init__()
		self.length = length
		self.intersection = intersection

		self.ingress = ingress 

		self.grid = SingleGrid(self.intersection.dimensions[0], self.intersection.dimensions[1], torus=False)
		self.create_agents()

	def create_agents(self):
		"""
		Creates n number of agents.
		"""

		for lk in ['ingress', 'egress']:

			data = eval(f'self.intersection.{lk}_groups')

			dir_keys = {0:(0,+1), 1:(+1,0), 2:(0,-1), 3:(-1,0)}
			for counter, lg in enumerate(data):
					x_pos = lg.lon
					y_pos = lg.lat
					length = lg.length

					for j in range(length):
						agent = lg
						self.grid.place_agent(agent, (int(x_pos) + dir_keys[counter][0]*j, int(y_pos) + dir_keys[counter][1]*j))