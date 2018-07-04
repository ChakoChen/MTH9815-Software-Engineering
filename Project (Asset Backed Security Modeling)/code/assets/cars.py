'''HW1 9815 - a class derived from q2_1 asset'''

# from Loans import Asset
from assets.asset import Asset

class Car(Asset):
    def __init__(self, initValue,depr=0):
        super(Car,self).__init__(initValue,depr)


class Lamborghini(Car):
    def __init__(self, initValue):
        super(Lamborghini,self).__init__(initValue,0.3)

class Prius(Car):
    def __init__(self, initValue):
        super(Prius,self).__init__(initValue,0.05)

class RangeRover(Car):
    def __init__(self,initValue):
        super(RangeRover,self).__init__(initValue,0.5)

