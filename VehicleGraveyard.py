class VehicleGraveyard:

    def __init__(self, i):
        self.cars = []
        self.ID = i

    def add_car(self,car):

        self.cars.append(car)