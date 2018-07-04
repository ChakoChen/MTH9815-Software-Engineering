'''HW1 9815 house base class, derived from asset'''

# from Loans import Asset
from assets.asset import Asset

class HouseBase(Asset):
    def __init__(self, initVal, depr):
        super(HouseBase,self).__init__(initVal,depr)

class PrimaryHome(HouseBase):
    def __init__(self, initVal, depr=0.07):
        super(PrimaryHome,self).__init__(initVal, 0.07)

class VacationHome(HouseBase):
    def __init__(self, initVal, depr=0.15):
        super(VacationHome,self).__init__(initVal,0.15)


