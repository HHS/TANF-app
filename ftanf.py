#!/usr/bin/env python3
#
# This script takes a CSV export of the Aggregate table in the FTANF
# spreadsheet.  It is _really_ format-dependent, so if OFA changes the
# format of that xls, you will need to fix this to match.  CSV is such
# a terrible format.
#
# usage:  ./ftanf.py /path/to/exported.csv > tanfdatareportingfile.txt
#
import csv
import sys


def popFromFront(mydictionary):
    keys = list(mydictionary.keys())
    key = keys[0]
    return mydictionary, mydictionary.pop(key)


def readLineStripLabel(f):
    line = f.readline()
    linethings = line.rstrip().split(',')
    # get rid of label at start of line
    linethings.pop(0)
    return linethings


with open(sys.argv[1]) as csvfile:
    ############################################
    # first section is the HEADER section
    headerline = csvfile.readline()
    if 'HEADER' not in headerline:
        raise Exception('MissingSection', 'missing header line!')

    # header titles
    next(csvfile)

    # header field lengths
    headerfieldlengths = readLineStripLabel(csvfile)

    # header field froms
    next(csvfile)

    # header field tos
    next(csvfile)

    # header comments
    next(csvfile)

    # header data!
    headerdata = readLineStripLabel(csvfile)

    # build the headerstring from the header data
    headerstring = ''
    for i in headerfieldlengths:
        try:
            length = int(i)
        except ValueError:
            # if there is no length set, we are at the end, so stop processing
            continue

        h = headerdata.pop(0)

        # right justify strings and zero pad numbers
        try:
            h = int(h)
            headerstring = headerstring + str(h).rjust(int(length), '0')
        except ValueError:
            headerstring = headerstring + h.rjust(int(length))

    # print the header out
    print(headerstring)

    # empty line
    next(csvfile)

    ############################################
    # next is section 3 aggregate data
    section3line = csvfile.readline()
    if 'SECTION 3 - AGGREGATE' not in section3line:
        print(section3line)
        raise Exception('MissingSection', 'missing section 3 aggregate data!')

    # metadata lines
    next(csvfile)
    next(csvfile)
    next(csvfile)

    # Descripton line!
    descriptions = readLineStripLabel(csvfile)

    # length line
    lengths = readLineStripLabel(csvfile)

    # from line
    froms = readLineStripLabel(csvfile)

    # to line
    tos = readLineStripLabel(csvfile)

    # commentline
    comments = readLineStripLabel(csvfile)

    # itemline
    itemthings = readLineStripLabel(csvfile)

    # process the file
    csvreader = csv.DictReader(csvfile, fieldnames=descriptions)
    recordcount = 0
    for row in csvreader:
        # harvest a few metadata items first
        row, comment = popFromFront(row)
        row, recordtype = popFromFront(row)

        mylengths = lengths.copy()
        myline = recordtype.rjust(int(mylengths.pop(0)))
        for _, v in row.items():
            length = mylengths.pop(0)
            try:
                length = int(length)
            except ValueError:
                # if there is no length set, we are at the end, so stop processing
                continue
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
            print('skipping invalid line: ' + myline, file=sys.stderr)

    # print the trailer out
    print('TRAILER' + str(recordcount).rjust(7, '0') + '         ')
