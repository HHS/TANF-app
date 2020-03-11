#!/usr/bin/env python3
#
# This script takes a CSV export of the Aggregate table in the FTANF
# spreadsheet
#
import csv
import sys
import datetime

with open(sys.argv[1]) as csvfile:
    # # first line is empty
    # next(csvfile)

    # next couple of lines seem to be metadata?
    next(csvfile)
    next(csvfile)

    # next line is the item #
    next(csvfile)

    # Descripton line!
    dline = csvfile.readline()
    descriptions = dline.rstrip().split(',')

    # length line
    lline = csvfile.readline()
    lengths = lline.rstrip().split(',')
    # get rid of cruft at start of line
    lengths.pop(0)
    lengths.pop(0)
    lengths.pop(0)

    # from line
    fline = csvfile.readline()
    froms = fline.rstrip().split(',')

    # to line
    tline = csvfile.readline()
    tos = tline.rstrip().split(',')

    # commentline
    cline = csvfile.readline()
    comments = cline.rstrip().split(',')

    # print the header out
    nowdate = datetime.datetime.now()
    print('HEADER' + str(nowdate.year) + str((nowdate.month - 1) // 3 + 1) + 'XXX')

    # process the file
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        comment = row.popitem(last=False)
        statefipscode = row.popitem(last=False)
        tribalcode = row.popitem(last=False)
        mylengths = lengths.copy()
        myline = ''
        for _, v in row.items():
            length = mylengths.pop(0)
            myline = myline + f'{v:{length}}'
        if myline.startswith(('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7')):
            print(myline)
        else:
            print('invalid line: ' + myline, file=sys.stderr)

    # print the trailer out
    print('TRAILER' + 'XXX')
