'''test various aspects of this project'''


def first_test():
    from Loans.Auto import FixedAutoLoan
    from Loans.LoanPool import LoanPool
    from Loans.Mortgage import FixedMortgage, VariableMortgage

    from Loans.loan import FixedRateLoan
    from assets.cars import Car, Lamborghini, RangeRover, Prius
    from assets.house import PrimaryHome, VacationHome

    fl = FixedRateLoan(25000, 0.05, 240)
    print fl.getRate(10)

    fm = FixedMortgage(100000, .075, 360)
    print fm.getRate()
    print fm.monthlyPayment()
    for i in range(2):
        print fm.principalDue(i)

    vm = VariableMortgage(200000, {24: 0.06, 360: 0.11}, 360)
    print vm.getRate(25)

    al = FixedAutoLoan(17000, .12, 60)
    print al.getRate()

    list_of_loans = [FixedAutoLoan(10000, .12, 60), FixedAutoLoan(20000, .11, 59), FixedAutoLoan(30000, .10, 58)]
    lp = LoanPool(list_of_loans)

    print "Total principal: %.2f" % lp.totalPrincipal()

    for i in range(2):
        print "Total balance at time %i: %.2f" % (i, lp.totalBalance(i))

    for i in range(5):
        print "P: %.2f + I: %.2f = totPmt: %.2f" % (lp.totalPrincipalDue(i), lp.totalInterestDue(i), lp.totalPaymentDue(i))

    print "WAR: %.4f, WAM: %.4f" % (lp.WAR(), lp.WAM())

    for i in range(55, 60):
        print "in period %i, WAR: %.6f, WAM: %.4f" % (i, lp.WAR(i), lp.WAM(i))

    print "========================== Creating some Cars ==================="

    c = Car(40000)
    c.depreciation = 0.10  # 1.0314159**12 - 1
    print c.currentValue()
    print c.monthlyDepreciation()
    print c.currentValue(12)

    rr = RangeRover(120000)
    l = Lamborghini(320000)
    p = Prius(23000)
    print "period\tRange Rover\tLamborghini\tPrius"
    for i in range(0, 60, 12):
        print "%i \t %.0f \t %.0f \t %.0f" % (i, rr.currentValue(i), l.currentValue(i), p.currentValue(i))

    print "======================== Creating some houses =========================="
    bk = PrimaryHome(600000)
    pu = VacationHome(600000)
    print "period\tprimary\tvacation"
    for i in range(0, 60, 12):
        print "%i \t %.0f \t %.0f" % (i, bk.currentValue(i), pu.currentValue(i))


def car_test():
    from Loans.Auto import FixedAutoLoan
    from assets.cars import Car, Lamborghini, RangeRover, Prius

    p = Prius(23000)
    print "created prius:"
    # if type(p)==type(Prius(0)):
    if isinstance(p,Car):
        print "it is a car"
    else:
        print "i have no idea what it is"

    l = FixedAutoLoan(10000,0.05,60,p)
    print l.getRate()
    if isinstance(l._asset,Car):
        print "this loan is backed by a car"
    print "per \t bal \t equity \t assval \t recover"
    for i in range (3):
        print "%i \t %.2f \t %.2f \t %.2f \t %.2f" % (i, l.loanBalance(i), l.equity(i), l._asset.currentValue(i), l.recoveryValue(i))


def mortgage_test():
    from Loans.Mortgage import FixedMortgage, VariableMortgage

    from assets.house import PrimaryHome, VacationHome

    vh = VacationHome(100000)
    m = FixedMortgage(80000,0.05,360,vh)
    print m.monthlyPayment(1)
    vh2 = VacationHome(90000)
    m2 = FixedMortgage(80000,0.05,360,vh2)
    print m2.monthlyPayment(1)
    print m2.PMI(1)


def tranche_test():
    # test standardTranche class
    print "Importing standardTranche"
    from ABS.tranche import standardTranche
    print "Creating standardTranche"
    s=standardTranche(100000,0.05,1)
    print s
    print "\nincrementing time period and "
    print "\nmaking principal and interest payments to tranche"
    for i in range(5):
        s.increaseTimePeriod()
        # s.makePrincipalPayment(200)
        s.makeInterestPayment(5)

    print "\nprinting history"
    s.getHistory(1)


def structured_product_test():
    # test structured product class
    from ABS.structuredProduct import StructuredSecurity
    from ABS.tranche import standardTranche
    print "creating structured security"
    sp = StructuredSecurity(100000)

    print "\nPrinting structured security:"
    print sp

    print "\nadding tranche, 20% of deal, sub level 1"
    sp.addTranche(standardTranche,.2,.05,1)
    print "\nPrinting structured security:"
    print sp

    print "\nadding tranche, 40% of deal, sub level 1"
    sp.addTranche(standardTranche, .4, .05, 1)
    print "\nPrinting structured security:"
    print sp

    print "\nadding tranche, 25% of deal, sub level 2"
    sp.addTranche(standardTranche, .25, .07, 2)
    print "\nPrinting structured security:"
    print sp

    print "\nmaking payments"
    sp.makePayments(50)

    print "\nmaking payments again"
    sp.makePayments(500)

    print "\nPrinting Waterfall"
    sp.showWaterfall()

def auto_loan_test():
    from Loans.Auto import FixedAutoLoan
    from assets.cars import Prius
    from Loans.LoanPool import LoanPool

    print "Creating loan"
    p = Prius(100000)
    loan = FixedAutoLoan(100000, 0.08, 10, p)
    lp = LoanPool([loan])
    print loan
    print "running cash flows"
    while lp.totalActiveLoans() > 0:
        print lp.makePayment()
    print "Cash flow history:"
    lp.showHistory()

    print "\ncreating second loan"
    loan = FixedAutoLoan(75000, 0.06, 8, p)
    lp = LoanPool([loan])
    print "running cash flows"
    while lp.totalActiveLoans() > 0:
        print lp.makePayment()
    print "Cash flow history:"
    lp.showHistory()


def waterfall_test():
    from ABS.structuredProduct import StructuredSecurity
    from ABS.tranche import standardTranche
    from Loans.LoanPool import LoanPool
    from Loans.Auto import FixedAutoLoan
    from assets.cars import Prius
    from Waterfall import doWaterfall

    print "\nCreating simple pool of loans:"
    p=Prius(100000)
    loan1 = FixedAutoLoan(100000,0.08,10,p)
    loan2 = FixedAutoLoan(75000,0.06,8,p)
    lp = LoanPool([loan1,loan2])
    print lp

    print "\nCreating structured security:"
    abs = StructuredSecurity(175000)
    abs.addTranche(standardTranche,0.8,0.05,1)
    abs.addTranche(standardTranche,0.2,0.08,2)
    print abs

    # print "\nRunning cash flows on loan pool"
    # break_int = 1000
    # while lp.totalActiveLoans() > 0 and break_int > 0:
    #     print lp.makePayment()
    #     break_int -= 1

    doWaterfall(lp,abs)


def test_CSV():
    from File_IO.CSV_Files import CSV_to_loanPool
    print "creating loanpool from csv file"
    loanPool = CSV_to_loanPool('Loans.csv')
    print "\nCreated loanpool: "
    print loanPool
    # print "\nLoans:"
    # for loan in loanPool.loanList:
    #     print loan


def large_loanpool_waterfall_test():
    from ABS.structuredProduct import StructuredSecurity
    from ABS.tranche import standardTranche
    # from Loans.LoanPool import LoanPool
    # from Loans.Auto import FixedAutoLoan
    # from assets.cars import Prius
    from Waterfall import doWaterfall
    from File_IO.CSV_Files import CSV_to_loanPool, loanPool_to_CSV, abs_to_CSV

    print "Creating loan pool from 1,500 loans"
    loanPool = CSV_to_loanPool('Loans.csv')
    print loanPool

    print "\nCreating structured security:"
    abs = StructuredSecurity(28354374.31)
    abs.addTranche(standardTranche, 0.7053585376753, 0.05, 1)
    abs.addTranche(standardTranche, 0.294641462, 0.08, 2)
    print abs

    doWaterfall(loanPool,abs)

    print "\nWriting loanPool history to csv file"
    loanPool_to_CSV(loanPool.getHistory(),'spam.csv')

    print "\nWriting ABS history to csv file"
    abs_to_CSV(abs,'eggs.csv')

    print "\nLoanPool time breakdown:"
    loanPool.showTimes()