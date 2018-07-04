'''
9815 Final Project
These methods are to facilitate input from and output to
CSV files; in particular, to read the 1,500-loan CSV
file provided to collateralize our structured security
'''

import csv
from assets.cars import Prius
from Loans.Auto import FixedAutoLoan
from Loans.LoanPool import LoanPool

# need method to read CSV file and return a LoanPool object
# the CSV file is formatted as follows:
# Loan #,Loan Type,Balance,Rate,Term,Asset,Asset Value
# we are to assume that the assets are of type Lexus (depr. rate __%)
def CSV_to_loanPool(csv_filename):
    loan_list = [] # the list of loans to return
    with open(csv_filename) as loanfile:
        loanreader = csv.reader(loanfile)
        header_row = loanreader.next() # move past header row
        for row in loanreader:
            # read important loan information
            loan_bal = float(row[2])
            loan_rate = float(row[3])
            loan_term = int(row[4])
            loan_asset_value = float(row[6])
            # create asset
            loan_car = Prius(loan_asset_value)
            # create loan
            l = FixedAutoLoan(loan_bal,loan_rate,loan_term,loan_car)
            # append loan to list
            loan_list += [l]
    loanPool = LoanPool(loan_list)
    return loanPool

def loanPool_to_CSV(loanPool, csv_filename):
    # employs the loanPool getHistory() method to get a list:
    # [(Balance, Interest_Due, Principal_Due, Recoveries, WAR, WAM)]
    # and saves this into a CSV file
    header_list = [("Period","Balance", "Interest Due", "Principal Due","Recoveries","WAR","WAM")]
    with open(csv_filename,"wb") as output_file:
        writer=csv.writer(output_file)
        writer.writerows(header_list)
        writer.writerows(loanPool)

def abs_to_CSV(abs, csv_filename):
    # employs the structuredProduct getWaterfall() method to retrieve a series of lists
    # then zips these lists into a single list
    # then places the zipped list into a csv file
    tranche_histories = abs.getWaterfall() # returns a list for each tranche
    reserves = abs.getReserves()
    # create a list of period numbers from the length of a tranche list which has 1 row per period
    period_list=range(len(tranche_histories[0]))
    period_list = [[i] for i in period_list] # transform into list of lists
    # create a header line
    header_list=[("Period")]
    tranche_counter = 0
    for tranche in tranche_histories:
        tranche_counter += 1
        # Interest Due, Interest Paid, Interest Shortfall, Principal Paid, Balance
        header_list += ["T"+str(tranche_counter)+" Interest Due","T"+str(tranche_counter)+" Interest Paid","T"+str(tranche_counter)+" Interest Shortfall","T"+str(tranche_counter)+" Principal Paid","T"+str(tranche_counter)+" Balance"]
    header_list += ["Reserve Balance"]
    # append the tranche lists
    master_list = period_list # start with list of periods
    for tranche in tranche_histories:
        current_period = 0
        for period in tranche:
            for item in period:
                master_list[current_period] += [item]
            current_period += 1
    # add reserve account balances
    current_period = 0
    for row in master_list:
        row += [reserves[current_period]]
        current_period += 1
    # master_list = zip(master_list,abs.getReserves())
    # output to CSV file
    with open(csv_filename,"wb") as output_file:
        fieldnames = header_list
        writer=csv.writer(output_file)
        header_writer=csv.DictWriter(output_file, fieldnames=fieldnames)
        # writer.writerows(header_list)
        header_writer.writeheader()
        writer.writerows(master_list)
    # print "Debug: header list"
    # print header_list


# need method to accept lists of lists and save it into
# two CSV files
# All of structured security tranches' data for a given time period
# will be in a single row of the CSV file (the reserve balance
# should be included in this; each time period gets its own row
