'''9815 hw -- An Asset Class'''

class Asset(object):
    def __init__(self, initValue, depr):
        self._initValue = initValue # initial value of asset
        self._depreciationRate = depr # annual depreciation rate

    def annualDepreciation(self):
        raise NotImplementedError() # makes this an abstract class?

    @property
    def depreciation(self):
        return self._depreciationRate

    @depreciation.setter
    def depreciation(self, dr):
        self._depreciationRate=dr

    def monthlyDepreciation(self):
        return 1-(1-self._depreciationRate)**(1.0/12)

    def currentValue(self,period=0):
        return self._initValue * (1-self.monthlyDepreciation())**period
