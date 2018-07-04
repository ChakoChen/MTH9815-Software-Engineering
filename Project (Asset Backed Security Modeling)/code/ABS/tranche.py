'''9815 Final Project
Tranche classes
for Asset-Backed Security Tranches'''

# Abstract Base Class for all ABS Tranches
class Tranche(object):
    def __init__(self, notional, rate, subordination):
        self._notional = notional
        self._rate = rate
        self._subordination = subordination
        self._principal_payments = [0] # a list of principal payments, indexed by period
        self._interest_payments = [0] # a list of interest payments, indexed by period
        self._interest_shortfalls = [0] # a list of interest shortfalls, indexed by period
        # self._principal_balance = [self._notional] # the current tranche notional, net of principal received
        self._sequential = True # boolean flag: True = sequential; False = pro rata
        self._frequency = 12 # monthly periods

    def __str__(self):
        output = "Tranche:\n"
        output += "Notional: " + str(self._notional)
        output += "\nRate: " + str(self._rate)
        output += "\nSubordination Level: " + str(self._subordination)
        return output

    @property
    def subordination(self):
        return self._subordination

    @property
    def rate(self):
        return self._rate

    @subordination.setter
    def subordination(self,sub):
        self._subordination = sub

    @property
    def sequential(self):
        return self._sequential

    @sequential.setter
    def sequential(self,seq_tf):
        self._sequential = seq_tf

    @property
    def pro_rata(self):
        return not self._sequential

    @pro_rata.setter
    def pro_rata(self, pro_rata_tf):
        self._sequential = not pro_rata_tf


# the most basic ABS tranche
class standardTranche(Tranche):
    def __init__(self, notional, rate, subordination):
        super(standardTranche,self).__init__(notional, rate, subordination)
        self._time_period = 0 # current time period, for tracking purposes

    def __str__(self):
        return  "Standard " + Tranche.__str__(self)


    @property
    def currentPeriod(self):
        return self._time_period

    # standard tranche needs to be able to track current time period
    # must call this before making payments to tranche
    def increaseTimePeriod(self):
        self._time_period += 1
        # append "ready" indicator to tranche lists
        # self._principal_payments += ["Ready"]
        # self._interest_payments += ["Ready"]
        # self._interest_shortfalls += ["Ready"]
        self._principal_payments += [0]
        self._interest_payments += [0]
        self._interest_shortfalls += [0]

    # reset tranche to original state
    def reset(self):
        self._principal_payments = [0] # a list of principal payments, indexed by period
        self._interest_payments = [0] # a list of interest payments, indexed by period
        self._interest_shortfalls = [0] # a list of interest shortfalls, indexed by period
        self._time_period = 0 # current time period, for tracking purposes
        # self._principal_balance = [self._notional] # the current tranche notional, net of principal received


    # record a principal payment for current time period (must be made current first)
    # can only happen once per time period
    # principal pays down current balance
    # if we try to pay more principal than notional balance, return excess amount
    def makePrincipalPayment(self, amount):
        excess_principal=0
        # print str(self.currentPeriod)+": " + str(self._principal_payments[self.currentPeriod])
        # check to see if already paid in current time period
        if self._principal_payments[self.currentPeriod] == 0:
            # ready to pay this period; check that tranche is not paid down
            if self.notionalBalance(self.currentPeriod-1) == 0:
                raise Exception("ERROR: Tranche already paid down in period "+str(self.currentPeriod-1))
            else:
                # is there excess principal?
                if amount > self.notionalBalance(self.currentPeriod-1):
                    excess_principal = amount - self.notionalBalance(self.currentPeriod-1)
                    amount = self.notionalBalance(self.currentPeriod-1)
                self._principal_payments[self.currentPeriod] = amount # update principal payments list
                # self._current_principal_balance -= amount # deduct payment from notional
        else:
            raise Exception("ERROR: Non-zero principal payment already exists in period " + str(self.currentPeriod))
        return excess_principal

    # record interest payment for current time period
    # can only happen once per time period
    # interest shortfalls accrue to current balance
    def makeInterestPayment(self,amount):
        # check to see if interest is due
        current_interest_due = self.interestDue()
        shortfall = current_interest_due - amount
        # print "%i: Int pmt due of %.2f" % (self.currentPeriod, current_interest_due)
        # print "%i: shtfall: %.2f - %.2f = %.2f" % (self.currentPeriod, current_interest_due, amount, shortfall)
        if shortfall < 0:
            shortfall = 0
        if current_interest_due == 0:
            raise Exception("ERROR: No interest due in period " + str(self.currentPeriod))
        # check to see if already paid in current time period
        else:
            if self._interest_payments[self.currentPeriod] == 0:
                self._interest_payments[self.currentPeriod] = amount # append current interest payment to list
                # self._current_principal_balance += shortfall # adjust notional for shortfall
                self._interest_shortfalls[self.currentPeriod] = shortfall # append any shortfall to list
            else:
                raise Exception("ERROR: Non-zero interest payment exists for period " + str(self.currentPeriod))

    # return amount of notional still owed to the tranche for the current time period
    # (after payments)
    def notionalBalance(self,period=0):
        if period > len(self._principal_payments):
            raise Exception("ERROR: asking for future information")
        else:
            # sum previous interest shortfalls
            shortfalls = sum([amt for i,amt in enumerate(self._interest_shortfalls) if i <= period])
            # print "shortfalls: " + str(shortfalls)
            # sum previous principal payments
            prin_pmts = sum([amt for i,amt in enumerate(self._principal_payments) if i<= period])
            # print "prin_pmts: " + str(prin_pmts)
            # return original notional less previous interest shortfalls and principal payments
            return self._notional + shortfalls - prin_pmts

    # return interest due for current time period
    def interestDue(self):
        # return self._current_principal_balance(period-1)*self._rate
        return self.notionalBalance(self.currentPeriod-1)*self._rate/self._frequency

    def getHistory(self, print_me=0):
        # a list containing for each period: (Interest Due, Interest Paid, Interest Shortfall, Principal Paid, Balance)
        output=[(0, 0, 0, 0, self.notionalBalance())]
        period=1
        while period < len(self._principal_payments):
            int_due = self.notionalBalance(period-1) * self.rate / self._frequency
            int_pd = self._interest_payments[period]
            int_sht = self._interest_shortfalls[period]
            p_pd = self._principal_payments[period]
            bal = self.notionalBalance(period-1) - p_pd + int_sht
            output += [(int_due, int_pd, int_sht, p_pd, bal)]
            period += 1
        # return output # list of tuples, 1 for each period
        if print_me == 1:
            # output to screen
            print "Per\tInt Due\tInt Pd\tI Shtfl\tPrin Pd\tBal"
            for i,period in enumerate(output):
                print "%i\t" % (i),
                for num in period:
                    print "%.2f\t" % (num),
                print ""
        return output # list of tranche information by period


