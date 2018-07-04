'''9815 HW1 class contains and operates on a pool of loans (composition)'''

import numpy
from Timer.timer import Timer

class LoanPool(object):
    def __init__(self,loanList):
        self._loanList = loanList # some sort of list of loans
        self._time_period = 0
        self._history = [(0,self.totalBalance(),0,0,0,self.WAR()*100,self.WAM())]
        # loan info lists for quick payment calculations:
        # Balance, Mo_Pmt, Rate, AssetVal, AssetDeprRate,isGood,badThisPer
        self._loanBalances = [loan.loanBalance() for loan in self._loanList]
        self._loanMoPmts = [loan.monthlyPayment() for loan in self._loanList]
        self._loanRates = [loan.getRate() for loan in self._loanList]
        self._loanIsGood = [1 for loan in self._loanList]
        self._loanAssetVal = [loan._asset.currentValue() for loan in self._loanList]
        self._loanAssetDeprRate = [loan._asset.depreciation for loan in self._loanList]

        # for debugging
        # self._time_spent={"CheckDefaults":0,"PrinCalc":0,"IntCalc":0,"BalCalc":0,"WAMWARCalc":0}
        self._time_spent = {"CheckDefaults": 0, "Build_Table": 0, "Calc_Items": 0, "Rand_Calc":0,"Loan_Defaults":0}
        self._timer = Timer()
        self._timer2 = Timer()

    def __str__(self):
        output = "Loan Pool\n"
        output += str(self.totalActiveLoans()) + " loans"
        output += "\nBalance: " + str(self.totalBalance())
        output += "\nWAR: " + str(self.WAR()*100)
        output += "\nWAM: " + str(self.WAM())
        return output

    def startTime(self):
        self._timer.start()

    def stopTime(self):
        return self._timer.end()

    def startTime2(self):
        self._timer2.start()

    def stopTime2(self):
        return self._timer2.end()

    @property
    def currentPeriod(self):
        return self._time_period

    @property
    def loanList(self):
        # for debugging purposes
        return self._loanList

    def increaseTimePeriod(self):
        self._time_period += 1

    # get the total loan principal
    def totalPrincipal(self):
        totalP = 0 # initialize result
        for loan in self._loanList:
            totalP += loan.notional
        return totalP

    # get the total loan balance for a given period
    def totalBalance(self, period=0):
        # if period==0:
        #     period = self.currentPeriod
        totalB = 0 # initialize result
        for loan in self._loanList:
            totalB += loan.loanBalance(period)
        return totalB

    # get the aggregate principal due in a period
    def totalPrincipalDue(self,period=0):
        # if period==0:
        #     period = self.currentPeriod
        totalP = 0 # initialize result
        for loan in self._loanList:
            totalP += loan.principalDue(period)
        return totalP

    # get the aggregate interest due in a period
    def totalInterestDue(self,period=0):
        # if period==0:
        #     period = self.currentPeriod
        totalI = 0 # initialize result
        for loan in self._loanList:
            totalI += loan.interestDue(period)
            # print period,
            # print ", ",
            # print loan,
            # print ", Bal: ",
            # print loan.loanBalance(period),
            # print ", Int due: ",
            # print loan.interestDue(period)
        return totalI

    # get the total payment due in a given period
    def totalPaymentDue(self,period=0):
        # if period==0:
        #     period = self.currentPeriod
        totalP = 0 # initialize result
        for loan in self._loanList:
            totalP += loan.monthlyPayment(period)
        return totalP

    # return the number of active loans (balance > 0)
    def totalActiveLoans(self,period=0):
        if period==0:
            period = self.currentPeriod
        totalL = 0 # initialize result
        for loan in self._loanList:
            if loan.loanBalance(period) > 0:
                totalL += 1
        return totalL

    # calculate the weighted average maturity (WAM)
    def WAM(self,period=0):
        # if period==0:
        #     period = self.currentPeriod
        totalWAM = 0
        totalBal = self.totalBalance(period)
        if totalBal > 0:
            for loan in self._loanList:
                if (loan.term - period) < 0:
                    marginalWAM = 0
                else:
                    marginalWAM = loan.term - period
                totalWAM += marginalWAM * loan.loanBalance(period) / totalBal
        return totalWAM

    # calculate the weighted averate rate (WAR)
    def WAR(self,period=0):
        # if period==0:
        #     period = self.currentPeriod
        totalWAR = 0
        totalBal = self.totalBalance(period)
        if totalBal > 0:
            for loan in self._loanList:
                totalWAR += loan.getRate(period) * loan.loanBalance(period) / totalBal
        return totalWAR

    def getDefaultRate(self):
        # default map provided in increasing order by time period
        default_map = {10: 0.0005, 59: 0.001, 119: 0.002, 179: 0.004, 209: 0.002, 360: 0.001}
        # default_map = {0:0, 10: 1, 59: 0.001, 119: 0.002, 179: 0.004, 209: 0.002, 360: 0.001}
        # find default probability based on current period
        default_key = 0
        # iterate through keys until one is larger
        # than the current period
        iter_keys = iter(sorted(default_map.keys()))
        key_check = iter_keys.next()
        while key_check < self.currentPeriod:
            key_check = iter_keys.next()
        default_key = key_check
        default_probability = default_map[default_key]
        return default_probability

    # flag a loan as defaulted if the passed in number is 0; return total recovery value
    def checkDefaults(self):
        default_probability = self.getDefaultRate()
        odds_denominator = 1/default_probability
        total_recovery = 0
        self.startTime2()
        for loan in self._loanList:
            if loan.isGood: # don't repeat-default loans, however improbable
                if loan.checkDefault(numpy.random.randint(0,odds_denominator)): # 0 appears with the default probability, causing default
                    # aggregate recovery value, add to waterfall
                    # print "default in per %i, recovery: %.2f" % (self.currentPeriod, loan.recoveryValue(self.currentPeriod))
                    total_recovery += loan.recoveryValue(self.currentPeriod)
        self._time_spent['Loan_Defaults'] += self.stopTime2()
        return total_recovery

    # make a payment; analagous to same routine in structured security
    # this will allow the loan pool to both return a cash amount paid
    # and track its internal history for reporting purposes
    def makePayment(self):
        # self._time_spent={"CheckDefaults":0,"PrinCalc":0,"IntCalc":0,"BalCalc":0,"WAMWARCalc":0}
        # increment time period
        self.increaseTimePeriod()

        # propagate defaults
        self.startTime()
        default_probability = self.getDefaultRate()
        odds_denominator = 1/default_probability
        defaulting_this_period = [(1 if numpy.random.randint(0,odds_denominator) == 0 else 0) * isGood
                                  for isGood in self._loanIsGood]
        # print "%i: defaulting bal: %.2f" % (self.currentPeriod,reduce(lambda total,(bal,gone): total+bal*gone,
        #                                                               zip(self._loanBalances,defaulting_this_period),0))
        self._time_spent['Rand_Calc'] += self.stopTime()
        self.startTime()
        # update asset values for current period depreciation
        self._loanAssetVal = [val*(1-depr) for (val,depr) in
                              zip(self._loanAssetVal,self._loanAssetDeprRate)]
        # extract recovery cash flow
        recovery_cash_flow = reduce(lambda total,(val,gone_bad): total+(val*0.6*gone_bad),
                                    zip(self._loanAssetVal,defaulting_this_period),0)
        # update defaulted list
        self._loanIsGood = [was_good - defaulted_this_time for (was_good,defaulted_this_time) in
                            zip(self._loanIsGood, defaulting_this_period)]
        # update interest, principal payments on previous period balance; then update balances
        all_interest_pmts = [balance*rate/12 for (balance,rate) in
                             zip(self._loanBalances,self._loanRates)]
        all_prin_pmts = [min(bal,mo_pmt - int_pmt) * (1 if bal > 0 else 0) for (mo_pmt,int_pmt,bal) in
                         zip(self._loanMoPmts,all_interest_pmts,self._loanBalances)]
        self._loanBalances = [max(0,bal - prin_pmt) for (bal,prin_pmt) in
                              zip(self._loanBalances,all_prin_pmts)]
        self._time_spent['Calc_Items'] += self.stopTime()
        self.startTime()
        # report figures net of defaults
        interest_due = reduce(lambda total,(int_pmt,good): total + int_pmt*good,
                              zip(all_interest_pmts,self._loanIsGood),0)
        principal_due = reduce(lambda total,(prin_pmt,good): total+prin_pmt*good,
                               zip(all_prin_pmts,self._loanIsGood),0)
        period_balance = reduce(lambda total,(bal,good): total+bal*good,
                                zip(self._loanBalances,self._loanIsGood),0)
        period_war = 0 # no longer interested in this; just want speed!
        period_wam = 0 # no longer interested in this; just want speed!
        self._time_spent['Build_Table'] += self.stopTime()

        # # the slightly less old way
        # # run default method, calculate and collect total recovery
        # self.startTime()
        # recovery_cash_flow = self.checkDefaults() # Cannot figure out how to avoid this step; need to get recovery value for this period's defaulted loans
        # self._time_spent['CheckDefaults'] += self.stopTime()
        # # the following numbers should now all be net of defaults in the loan pool
        # # create table of loan balances, rates, goodness in current period
        # # ...then I can just zip down some results!
        # self.startTime()
        # loan_table = [(loan.loanBalance(self.currentPeriod-1),loan.monthlyPayment(),
        #                loan.getRate()) #, loan.Good)
        #                for loan in self._loanList if loan.isGood]
        # self._time_spent['Build_Table'] += self.stopTime()
        # self.startTime()
        # # current balance is previous balance less monthly payment, add back interest
        # period_balance = reduce(lambda total,(balance,mo_pmt,rate): total+(balance-mo_pmt+balance*rate/12),loan_table,0)
        # interest_due = reduce(lambda total,(balance,spam,rate): total+balance*rate/12,loan_table,0)
        # # monthly_pmt = reduce(lambda total,(spam,mo_pmt,eggs,good): total+mo_pmt*good,loan_table,0)
        # principal_due = reduce(lambda total,(balance,mo_pmt,rate): total+min(balance,mo_pmt-balance*rate/12),loan_table,0)
        # period_war = 0 # no longer interested in this; just want speed!
        # period_wam = 0 # no longer interested in this; just want speed!
        # # self._time_spent['Calc_Items'] += self.stopTime()

        # # the old way
        # self.startTime()
        # principal_due = self.totalPrincipalDue(self.currentPeriod-1) # payments made in arrears
        # self._time_spent['PrinCalc'] += self.stopTime()
        # self.startTime()
        # interest_due = self.totalInterestDue(self.currentPeriod-1)
        # self._time_spent['IntCalc'] += self.stopTime()
        # self.startTime()
        # period_balance = self.totalBalance(self.currentPeriod) # balance for arrears payments made next period
        # self._time_spent['BalCalc'] += self.stopTime()
        # self.startTime()
        # period_war = self.WAR(self.currentPeriod)*100 # typically outputting 2-digit numbers
        # period_wam = self.WAM(self.currentPeriod)
        # self._time_spent['WAMWARCalc'] += self.stopTime()
        # print "Debug: appending history, e.g. WAR = " + str(period_war)

        self._history += [(self.currentPeriod, period_balance, interest_due, principal_due, recovery_cash_flow, period_war, period_wam)]
        # return total cash flow: interest, principal, recovery
        return interest_due + principal_due + recovery_cash_flow

    def getHistory(self):
        # returns a list of tuples:
        # [(Period, Balance, Interest_Due, Principal_Due, Recoveries, WAR, WAM)]
        return self._history

    def showHistory(self):
        print "Per\tBal\tInt_Due\tPrin_Due\tRecov.\tWAR\tWAM"
        for i,period_list in enumerate(self.getHistory()):
            # print "%i\t" % (i),
            for num in period_list:
                print "%.2f\t" % (num),
            print "" # new line

    def showTimes(self):
        for key in self._time_spent.iterkeys():
            print key,
            print ": ",
            print self._time_spent[key]

