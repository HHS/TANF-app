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

class FTANFProcess:
    def __init__(self, file_path, data_index):
        self.record_count = 0
        self.xl_workbook = xlrd.open_workbook(file_path)
        self.xl_sheet = self.xl_workbook.sheet_by_index(1)
        self.data_index = data_index
        print('Opening Sheet: %s' % self.xl_sheet.name)

    def pad_field_data(self, field_length_list, value_data):
        padded_string = ''
        for i, field_length in enumerate(field_length_list):
            try:
                length = int(field_length)
            except ValueError:
                # if there is no length set, we are at the end, so stop processing
                continue

            # right justify strings and zero pad numbers
            else:
                try:
                    h = int(value_data[i])
                    padded_string = padded_string + str(h).rjust(int(length), '0')
                except ValueError:
                    if len(value_data[i]) > 0:
                        padded_string = padded_string + value_data[i].rjust(int(length))
                    else:
                        padded_string = padded_string + value_data[i].zfill(length)

        return padded_string

    def build_header(self):
        # Grab header row by index (i.e. row 1 equals index 0)
        header_row = self.xl_sheet.row_values(0)

        if 'HEADER' not in header_row:
            raise Exception('MissingSection', 'missing header line!')

        # Grab header field lenghts on row 3
        header_field_lengths = self.xl_sheet.row_values(2)
        header_data = self.xl_sheet.row_values(5)[1:]
        headerstring = ''

        if header_field_lengths[0] == 'Length':
            headerstring = self.pad_field_data(header_field_lengths[1:], header_data)

        # print the header out
        print(headerstring)

    def build_body(self):
        section_field_lengths = self.xl_sheet.row_values(11)[1:]

        #iterate through the rows and check if they start with a T1-6,
        # if so add length padding and print
        for row_index in range(self.data_index,(self.xl_sheet.ncols-1)):
            try:
                data_row_values = self.xl_sheet.row_values(row_index)[1:]
                if data_row_values[0].startswith(('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7')):
                    self.record_count = self.record_count + 1
                    section_string = self.pad_field_data(section_field_lengths, data_row_values)
                    print(section_string)
            except IndexError:
                break


    def build_trailer(self):
        print('TRAILER' + str(self.record_count).rjust(7, '0') + '         ')

    def build_section(self):
        self.build_header()
        self.build_body()
        self.build_trailer()


section = FTANFProcess(sys.argv[1], 15)
section.build_section()
