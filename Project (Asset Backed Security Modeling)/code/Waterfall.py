'''
9815 Final Project
Standalone functions employing ABS and Loans
to perform a cash flow simulation:
- the source of the cash flows is a LoanPool
- the recipient of the cash flows is a StructuredSecurity
The results of the simulation are handled appropriately
'''

# from ABS.structuredProduct import StructuredSecurity
# from Loans.LoanPool import LoanPool
from Timer.timer import Timer


def doWaterfall(loanPool, structuredSecurity):
    timer = Timer()
    lpTime = 0
    absTime = 0
    current_period = 0
    breakcounter = 5000 # arbitrarily high number; surely no loanPool would last longer than this number of months
    while loanPool.totalActiveLoans(current_period) > 0: # while any loans remain
        current_period += 1 # increment period; period 0 represents origination, so start with 1
        # print "Current period: " + str(current_period),
        # ask loan pool for its total payment for current time period
        timer.start()
        available_funds = loanPool.makePayment()
        lpTime += timer.end()
        # print ", Avail funds: " + str(available_funds),
        # pay structured security with amount provided by loan pool
        timer.start()
        structuredSecurity.makePayments(available_funds)
        absTime += timer.end()
        # print "...paid!"

    # call getWaterfall on both loan pool and structured security, and save into two variables
    # return results, as well as balance of reserve account
    print "\nLoan Pool History:"
    loanPool.showHistory()
    print "\nStructured Security Waterfall:"
    structuredSecurity.showWaterfall()

    print "Total time on Loan Pool: %.2f" % (lpTime)
    print "Total time on ABS: %.2f" % (absTime)