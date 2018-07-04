'''9815 HW Loan base class'''

# from Loans import Asset
from assets.asset import Asset

class Loan(object):
    def __init__(self, notional, rate, term, asset):
        self._notional = notional
        self._rate = rate # annual
        self._term = term # months
        self._asset = asset # the underlying asset class
        self._good_loan = 1 # turns to 0 when defaulted
        self._recovery_multiplier = 0.6
        if isinstance(self._asset,Asset) == False:
            raise Exception("Loan must contain an Asset")

    def checkDefault(self, random_number):
        if random_number == 0: # loan defaults
            self._good_loan = 0 # set to defaulted value
            # print "Loan of original size %.2f defaults!" % (self._notional)
        return random_number == 0

    def __str__(self):
        output = "Loan: "
        output += str(self._notional)
        output += ", " + str(self._rate*100)
        output += ", " + str(self._term)
        return output


    def monthlyPayment(self,period=None):
        # assuming self-amortizing loan
        r=self._rate/12 # monthly interest rate
        P = self._notional # principal balance
        N = self._term # term of loan, in months
        return (r*P)/(1-(1+r)**(-N)) * self._good_loan

    def totalPayments(self):
        # assuming self-amortizing loan
        return self.monthlyPayment() * self._term

    def totalInterest(self):
        r = self._rate / 12  # monthly interest rate
        P = self._notional  # principal balance
        N = self._term  # term of loan, in months
        total_int = 0
        pmt = (r*P)/(1-(1+r)**(-N))
        for n in range(0,self._term): # for each month in term of loan
            bal=P*(1+r)**n - pmt * ((1+r)**n-1)/r # calculate current balance
            total_int=total_int + r*bal # add monthly interest payment to total
        return total_int

    def recoveryValue(self,period):
        if period > self._term:
            # loan expired; no recovery
            loan_recovery_value = 0
        else:
            asset_recovery_value = self._asset.currentValue(period)*self._recovery_multiplier
            loan_recovery_value = asset_recovery_value
            # return minimum of recovery value, outstanding loan balance
            # calculate loan balance for period... class method won't work because loan is defaulted
            r = self._rate / 12  # monthly interest rate
            P = self._notional  # principal balance
            N = self._term  # term of loan, in months
            pmt = (r * P) / (1 - (1 + r) ** (-N))
            n = period
            bal = P * (1 + r) ** n - pmt * ((1 + r) ** n - 1) / r  # calculate balance at period per slide formula
            # print "asset recovery: %.2f; balance: %.2f" % (asset_recovery_value, bal)
            if bal < loan_recovery_value:
                loan_recovery_value = bal
        return loan_recovery_value

    def equity(self,period):
        # returns the available equity = asset value less loan balance
        return self._asset.currentValue(period) - self.loanBalance(period)

    @property  # getters & setters
    def notional(self):
        return self._notional * self._good_loan

    @notional.setter
    def notional(self, _notional):
        self._notional = _notional

    @property
    def isGood(self):
        return self._good_loan == 1

    @property
    def Good(self):
        return self._good_loan # 1 if good, 0 if defaulted

    @property  # getters & setters
    def rate(self):
        return self._rate * self._good_loan

    @rate.setter
    def rate(self, _rate):
        self._rate = _rate

    @property  # getters & setters
    def term(self):
        return self._term * self._good_loan

    @term.setter
    def term(self, _term):
        self._term = _term

    # when we'll override a function by the child classes
    # we're going to raise a "not implemented error" because
    # there's no point in the child class????

    # this function will do different things depending on whether
    # you have a fixed or variable rate loan
    def getRate(self, period):
        raise NotImplementedError()

    def interestDue(self,period=0):
        if self.loanBalance(period) == 0:
            return 0
        else:
            # use a formula to calculate the interest due at a given period
            r = self._rate / 12  # monthly interest rate
            P = self._notional  # principal balance
            N = self._term  # term of loan, in months
            pmt = (r*P)/(1-(1+r)**(-N))
            n = period
            bal = P * (1 + r) ** n - pmt * ((1 + r) ** n - 1) / r  # calculate balance at period per slide formula
            return r * bal * self._good_loan  # monthly interest due in submitted period

    def principalDue(self,period=0):
        prin_due = (self.monthlyPayment(period) - self.interestDue(period)) * self._good_loan
        if prin_due > self.loanBalance(period):
            prin_due = self.loanBalance(period)
        return prin_due

    def loanBalance(self,period=0):
        if period > self._term:
            return 0
        else:
            r = self._rate / 12  # monthly interest rate
            P = self._notional  # principal balance
            N = self._term  # term of loan, in months
            pmt = (r*P)/(1-(1+r)**(-N))
            n = period
            bal = P * (1 + r) ** n - pmt * ((1 + r) ** n - 1) / r  # calculate balance at period per slide formula
            return bal * self._good_loan
