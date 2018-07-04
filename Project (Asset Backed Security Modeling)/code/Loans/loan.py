'''9815 HW: Loan objects will inherit from loan base class'''

'''Derived loan class'''

# from Loans import Loan
# from assets.asset import Asset
from Loans.loan_base import Loan

class FixedRateLoan(Loan):
    def __init__(self,notional,rate,term,asset):
        super(FixedRateLoan,self).__init__(notional,rate,term,asset)
        # having trouble initializing a fixed car loan with a car asset
    # not an object; just a loan, with no special functionality
    # which makes this very simple! We don't even have to initialize....

    def getRate(self,period=None):
        # overrides base class function
        return self._rate # this should work, even though we didn't initialize


class VariableRateLoan(Loan):
    def __init__(self, notional, rateDict, term, asset):
        self._rateDict = rateDict
        super(VariableRateLoan,self).__init__(notional,None,term, asset)
        # do want this to initialize from base class loan
        # but taking in a special type of rate, so initializing to None....

    def getRate(self, period=0):
        # find the current period
        i=0 # the index
        rate=9999 # make a not=found error obvious
        for i in sorted(self._rateDict.keys()):
            if period <= i:
                rate = self._rateDict[i]
            if i > period:
                break
        return rate


    # rateDict: {0:.03, 2:.04, 10:.5} periods and new rates
    # all you have to do is put in your time period,
    # and it will pass back the rate
