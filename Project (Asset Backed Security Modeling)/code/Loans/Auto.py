'''9815 HW1: Auto loan class will derive from fixed rate loan classes'''

from loan import FixedRateLoan
from assets.cars import Car# note: this declaration caused an error when it was preceded by q2_2
# (I couldn't use the "isinstance" test in FixedAutoLoan)

class FixedAutoLoan(FixedRateLoan):
    def __init__(self, notional, rate, term, asset):
        super(FixedRateLoan,self).__init__(notional, rate, term, asset)
        self._fixed_payment=super(FixedRateLoan,self).monthlyPayment() # just calcalate once
        if isinstance(self._asset,Car) == False:
            raise Exception("Fixed Auto Loan must contain a car")
        # if type(self._asset) != type(Prius(0)):
        #     print type(self._asset)
        #     print type(Prius(0))
        #     raise Exception("You didn't givve this fixed auto lona a car")

    def monthlyPayment(self,period=None):
        return self._fixed_payment