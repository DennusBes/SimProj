from mesa import Agent

from FillerRoad import FillerRoad


class Vehicle(Agent):

	def __init__(self, unique_id, model):
		super().__init__(unique_id, model)
		self.speed = 0
		self.length = 0
		self.shape = 'car_black.png'
		self.color = 'red'
		self.layer = 1
		self.delete_agent = False
		self.crossed_intersection = False

	def step(self):
		"""
		A single step
		- evaluate all parameters to adjust speed and whether to move or not
		"""
		self.delete_agent = False

		self.speed += 1
		new_x_pos = self.get_new_x_pos()

		self.set_speed(new_x_pos)
		self.move()
	
	def check_cell(self, x_pos, y_pos):
		"""
		Checks if cell has no other vehicles and if cell is a filler road
		:return: True if empty otherwise False
		"""
		try:
			this_cell = self.model.grid.get_cell_list_contents([(x_pos, y_pos)])

			for obj in this_cell:
				if isinstance(obj, Vehicle):
					print("Next cell already contains a vehicle")
					return False
				elif isinstance(obj, FillerRoad) and self.crossed_intersection == False:
					print("Next cell is filler road")
					self.crossed_intersection = True
					return False
			return True
		except IndexError:
			print("Next cell is out of grid")
			self.delete_agent = True
			return False

	def get_new_x_pos(self):
		"""
		Checks the best x coordinate the car can go to. (Car x position + car speed).
		:param lane: Lane to check.
		:returns: Best car x position. If car is in front of him it will return current x position.
		"""
		print("Current position: ", self.pos[0])
		print("Current speed: ", self.speed)
		print("Next position: ",self.pos[0] + self.speed)
		for i in range((self.pos[0] + 1), (self.pos[0] + self.speed + 1)):
			if not self.check_cell(i,self.pos[1]):
				return i - 1

		return self.pos[0] + self.speed

	def set_speed(self, x_cor):
		"""
		Sets new car speed
		"""
		self.speed = x_cor - self.pos[0]

	def move(self):
		"Moves the car to the next position with the given x and y coordinates"
		this_cell = self.model.grid.get_cell_list_contents([self.pos])
		currentVehicle = [obj for obj in this_cell if isinstance(obj, Vehicle)][0]		
		if self.delete_agent == True:
			self.model.grid._remove_agent(self.pos, currentVehicle)
			self.model.schedule.remove(currentVehicle)
		else:
			self.model.grid.move_agent(self, (self.pos[0] + self.speed, self.pos[1]))





