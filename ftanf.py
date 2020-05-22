#!/usr/bin/env python3
#
# This script takes a CSV export of the Aggregate table in the FTANF
# spreadsheet.  It is _really_ format-dependent, so if OFA changes the
# format of that xls, you will need to fix this to match.  CSV is such
# a terrible format.
#
# usage:  ./ftanf.py /path/to/section_x.xlsx > tanfdatareportingfile.txt
#

############################################
# # Setup script and open sheet           ##
############################################

import sys
import xlrd

# Open the workbook
xl_workbook = xlrd.open_workbook(sys.argv[1])

# Open first sheet by index
xl_sheet = xl_workbook.sheet_by_index(1)
print('Opening Sheet: %s' % xl_sheet.name)

def pad_field_data(field_length_list, value_data):
    padded_string = ''
    for i, field_length in enumerate(field_length_list):
        try:
            length = int(field_length)
        except ValueError:
            # if there is no length set, we are at the end, so stop processing
            continue

        # right justify strings and zero pad numbers
        try:
            h = int(value_data[i])
            padded_string = padded_string + str(h).rjust(int(length), '0')
        except ValueError:
            padded_string = padded_string + value_data[i].rjust(int(length))

    return padded_string

############################################
# # Process header                       ##
############################################

# Grab header row by index (i.e. row 1 equals index 0)
header_row = xl_sheet.row_values(0)

if 'HEADER' not in header_row:
    raise Exception('MissingSection', 'missing header line!')

# Grab header field lenghts on row 3
header_field_lengths = xl_sheet.row_values(2)
header_data = xl_sheet.row_values(5)[1:]
headerstring = ''

if header_field_lengths[0] == 'Length':
    headerstring = pad_field_data(header_field_lengths[1:], header_data)

# print the header out
print(headerstring)

############################################
# # Process section                       ##
############################################

sectionline = xl_sheet.row_values(7)
# if 'Section' not in sectionline:
#     print(sectionline)
#     raise Exception('MissingSection', 'missing section data!')

section_field_description = xl_sheet.row_values(10)
section_field_lengths = xl_sheet.row_values(11)[1:]


recordcount = 0

for row_index in range(16,(xl_sheet.ncols-1)):
    try:
        data_row_values = xl_sheet.row_values(row_index)[1:]
        if data_row_values[0].startswith(('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7')):
            recordcount = recordcount + 1
            section_string = pad_field_data(section_field_lengths, data_row_values)
            print(section_string)
    except IndexError:
        break



############################################
# # Process section                       ##
############################################
print('TRAILER' + str(recordcount).rjust(7, '0') + '         ')
