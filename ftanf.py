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
    recordcount = 0
    for row in csvreader:
        # harvest a few metadata items first
        _, comment = row.popitem(last=False)
        _, statefipscode = row.popitem(last=False)
        _, tribalcode = row.popitem(last=False)
        _, recordtype = row.popitem(last=False)

        mylengths = lengths.copy()
        myline = recordtype.rjust(int(mylengths.pop(0)))
        for k, v in row.items():
            length = mylengths.pop(0)
            try:
                length = int(length)
            except ValueError:
                # if there is no length set, try a default.
                # XXX probably should just not handle this so that the spreadsheet gets fixed
                print('no length for column: ' + k + ' Using 8 as a default', file=sys.stderr)
                length = 8
            length = int(length)

            # right justify strings and zero pad numbers
            try:
                v = int(v)
                myline = myline + str(v).rjust(int(length), '0')
            except ValueError:
                myline = myline + v.rjust(int(length))

        # Do some validation to make sure that this is a real line
        if myline.startswith(('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7')):
            print(myline)
            recordcount = recordcount + 1
        else:
            print('invalid line: ' + myline, file=sys.stderr)

    # print the trailer out
    print('TRAILER' + str(recordcount).rjust(7, '0') + '         ')
