'''9815 HW1 Mortgage (and mixin) classes '''

from Loans.loan import FixedRateLoan, VariableRateLoan
# from assets import HouseBase
from assets.house import HouseBase

# an object to add functionality to mortgages
# particularly PMI
class MortgageMixin(object):
    # despite not inheriting, must initialize with base class?
    def __init__(self, notional, rate, term, home):
        super(MortgageMixin,self).__init__(notional, rate, term, home)
        if isinstance(self._asset,HouseBase) == False:
            raise Exception("Mortgage must contain a House")

    # mortgage-related functions
    def PMI(self, period):
        # 0.75% of loan amount, applied monthly
        # need to add test for >80% LTV, once loan has an home
        if self.loanBalance(0) / self._asset.currentValue(0) > 0.8: # based on original loan balance and house value
            return 0.0075/12 * self.loanBalance(period)
        else:
            return 0
        # return 0.0075/12 * self.loanBalance(period) # assume for now LTV is 100%

    def monthlyPayment(self,period=0):
        standardPmt = super(MortgageMixin,self).monthlyPayment(period)
        return standardPmt + self.PMI(period)

    def principalDue(self,period=0):
        #print "Calculating principal due:"
        #print "mo pmt: %.2f - pmi: %.2f - interest: %.2f = " %(super(MortgageMixin,self).monthlyPayment(period) , self.PMI(period) , super(MortgageMixin,self).interestDue(period))
        return super(MortgageMixin,self).monthlyPayment(period) - super(MortgageMixin,self).interestDue(period)


class FixedMortgage(MortgageMixin, FixedRateLoan):
    def __init__(self, notional, rate, term,home):
        super(FixedRateLoan,self).__init__(notional, rate, term, home)
        super(MortgageMixin,self).__init__(notional, rate, term, home)

class VariableMortgage(MortgageMixin, VariableRateLoan):
    def __init__(self, notional, rate, term,home):
        super(VariableRateLoan,self).__init__(notional, rate, term, home)
        super(MortgageMixin,self).__init__(notional,rate,term, home)

