'''
9815 Final Project
This class will be a composition of Tranche objects,
initialized with a total Notional amount.
It will contain a Factory Method to add tranches to itself
'''

from ABS.tranche import standardTranche

class StructuredSecurity(object):
    def __init__(self, notional):
        self._total_notional = notional # total deal notional amount
        self._subordination_flags = set([]) # a unique set of subordination flags
        self._tranche_list = [] # a list of tranches in the deal
        self._reserve_account = 0 # repository for excess waterfall cash
        self._reserve_tracker = [0] # time series of reserve account balances

    @property
    def reserveBalance(self):
        return self._reserve_account

    def __str__(self):
        output = "Structured Security"
        output += "\nTotal Notional: " + str(self._total_notional) + "\nTranches:"
        # output += str(["Tranche size: %i" % (t.notionalBalance()) for t in self._tranche_list]) + "\n"
        for sub_level in sorted(self._subordination_flags):
            output += "\nSubordination: " + str(sub_level)
            for tranche in [t for t in self._tranche_list if t.subordination == sub_level]:
                output += "\n\tSize: " + str(tranche.notionalBalance())
                output += "\tRate: " + str(tranche.rate)
        return output


    # factory method to add tranches to the deal list
    def addTranche(self,tranche_type,percentage,rate,subordination):
        # create a temporary tranche with these characteristics
        # first check that there is room (assuming all tranches contain principal)
        current_deal_principal = 0
        if len(self._tranche_list) != 0:
            # adjust deal principal for existing tranches
            current_deal_principal = sum([t.notionalBalance() for t in self._tranche_list])
        available_principal = self._total_notional - current_deal_principal
        new_tranche_principal = percentage * self._total_notional
        if new_tranche_principal > available_principal:
            raise Exception("ERROR: deal principal " + str(available_principal) + "; cannot add tranche " + str(new_tranche_principal))
        else:
            # everything's OK; create tranche and add to deal
            t = tranche_type(new_tranche_principal,rate,subordination)
            # add new subordination level to set of subordination levels (only if unique)
            self._subordination_flags = self._subordination_flags.union(set([subordination]))
            self._tranche_list += [t]

    def setSequential(self,tranche,seq_tf):
        # set the flag on a tranche to a boolean value indicating sequential
        tranche.sequential(seq_tf)

    def setProRata(self,tranche,pro_rata_tf):
        # set the flag on a tranche to a boolean value indicating pro-rata
        tranche.pro_rata(pro_rata_tf)

    def increaseTimePeriod(self):
        # increment time period for every tranche
        [t.increaseTimePeriod() for t in self._tranche_list]

    # cycle through all tranches, in order of subordination
    # interest payments first, then
    # principal payments (sequential or pro rata)
    def makePayments(self,cash_amount):
        cash_amount += self._reserve_account # include any reserve account balance in waterfall
        self._reserve_account = 0 # we have moved the reserve account balance into the waterfall; excess will be returned at the end
        self.increaseTimePeriod() # prepare tranches to receive payments by incrementing time period
        # first make interest payments to all tranches (subordinate interest is senior to senior principal)
        for subordination_level in sorted(self._subordination_flags): # descend through subordination levels
            # get total current balance at this subordination level
            sub_level_balance = sum([t.notionalBalance(t.currentPeriod-1) for t in self._tranche_list
                                     if t.subordination == subordination_level])
            sub_level_paid_out = 0
            # pay each tranche at this level
            for tranche in [t for t in self._tranche_list if t.subordination == subordination_level]:
                if sub_level_balance > 0:
                    # determine pro-rata share
                    pro_rata_ratio = tranche.notionalBalance(tranche.currentPeriod-1)/sub_level_balance
                    # split up the available cash
                    available_cash = pro_rata_ratio * cash_amount
                    # ask tranche for required payment amount
                    interest_needed = tranche.interestDue()
                    # pay minimum of available cash or required interest
                    if available_cash < interest_needed:
                        payment_amount = available_cash
                    else:
                        payment_amount = interest_needed
                    # pay tranche
                    tranche.makeInterestPayment(payment_amount)
                    # track total payment to subordination level
                    sub_level_paid_out += payment_amount
                # reduce funds available by amount paid to entire subordination level
                cash_amount -= sub_level_paid_out
        # second, make principal payments to tranches in order of subordination
        for subordination_level in sorted(self._subordination_flags): # descend through subordination levels
            # get total current balance at this subordination level
            sub_level_balance = sum([t.notionalBalance(t.currentPeriod - 1) for t in self._tranche_list
                                     if t.subordination == subordination_level])
            sub_level_paid_out = 0
            # pay each tranche at this level
            for tranche in [t for t in self._tranche_list if t.subordination == subordination_level]:
                tranche_balance = tranche.notionalBalance(tranche.currentPeriod-1)
                if sub_level_balance > 0:
                    # determine pro-rata share
                    pro_rata_ratio = tranche_balance/sub_level_balance
                    # split up the available cash
                    available_cash = pro_rata_ratio * cash_amount
                    if available_cash > tranche_balance:
                        # paying tranche off completely!
                        payment_amount = tranche_balance # only pay the remaining balance of tranche
                    else:
                        # give tranche all available funds (pro rata within subordination level)
                        payment_amount = available_cash
                    # pay tranche
                    tranche.makePrincipalPayment(payment_amount)
                    # track total payment to subordination level
                    sub_level_paid_out += payment_amount
                # reduce funds available by amount paid to subordination level
                cash_amount -= sub_level_paid_out
        # put leftover cash into reserve account
        self._reserve_account += cash_amount
        self._reserve_tracker += [self._reserve_account]

    # create a list of lists: each inner list is a tranche, and contains the following values for a given time period:
    # Interest Due, Interest Paid, Interest Shortfall, Principal Paid, Balance
    def getWaterfall(self):
        return [tranche.getHistory() for tranche in self._tranche_list] # tranche returns the appropriate values

    def showWaterfall(self):
        for tList in self.getWaterfall():
            print "\nPer\tInt Due\tInt Pd\tI Shtfl\tPrin Pd\tBal"
            for i, period in enumerate(tList):
                print "%i\t" % (i),
                for num in period:
                    print "%.2f\t" % (num),
                print ""
        print "\nReserve account:\nPeriod\tBalance"
        for i,amt in enumerate(self._reserve_tracker):
            print "%i\t%.2f" % (i,amt)

    def getReserves(self):
        # return list of reserve account balances
        return self._reserve_tracker