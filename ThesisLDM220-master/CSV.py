import csv

HEADER = ["Name", "Contact", "Employer", "DosimeterID", "EntryTime", "ExitTime", "Total Visit Dose", "ReactorStatus", "Notes"]

def report_creation(data, name):

    with open(name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADER)
        writer.writerows(data)
