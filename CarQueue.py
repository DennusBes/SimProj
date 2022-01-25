class CarQueue:

    def __init__(self, id):
        self.cars = []
        self.color = 'black'
        self.shape = 'clear.png'
        self.ID = id


    def add_car(self,car):

        self.cars.append(car)

    def remove_car(self):

        self.cars.pop(0)
        
    def clear_cars(self):
        
        self.cars.clear()

