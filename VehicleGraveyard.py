class VehicleGraveyard:

    def __init__(self, i):
        self.cars = []
        self.ID = i
        self.busses = []

    def add_car(self,car):

        self.cars.append(car)

    def add_bus(self,car):

        self.busses.append(car)		