#"Copyright 2010 Bryan Harris"
# Copyright 2011 James Prior
#
#This file is part of Reduce.
#
#    Reduce is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Reduce is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Reduce.  If not, see <http://www.gnu.org/licenses/>.

import os
import xlrd
import tempfile

import math

class MeasFile:
    filename = ''
    if False: #!!! unused variablles, consider deleting them. 
        description = ''
        sponsor = ''
        tech = ''
        acct_number = ''
        date = ''
    sheets = []
    specimens = [] #!!! the accumulated specimens are never used, so why bother? 
    book = ''
    name_rows = range(5, 50+1, 5) #!!! magice numbers
    name_cols = range(0, 5+1, 5) #!!! magice numbers

    def __init__(self, filename):
        self.sheets = []
        self.specimens = []
        self.filename = filename
        self.book = xlrd.open_workbook(self.filename)
        for sheet in self.book.sheets():
            and sheet.row(0)[4].value.find('Measurement Sheet') != -1
            and sheet.row(6)[0].value.find('Specimen ID') != -1
            and sheet.row(6)[5].value.find('Specimen ID') != -1):
                # The sheet is a measurement sheet. 
                # print sheet.name, 'is a measurement sheet!'
                self.sheets.append(sheet)
        #print 'number of sheets:', self.len(self.sheets)
        for sheet in self.sheets:
            for arow in self.name_rows:
                for acol in self.name_cols:
                    acell = sheet.row(arow)[acol]
                    if acell.ctype == 1: #!!! magic number
                        #!!! what's going on with the following assignment? Does acell.value have any effect? 
                        acell = acell.value
                        acell = acell.upper()
                        acell = acell.replace('STL', '')
                        acell = acell.strip()
                        specimen = Specimen(acell, arow, acol, sheet)
                        self.specimens.append(specimen)
                        #this_spec.get_measurements(sheet)
                        #this_spec.get_thickness(sheet)
                        #this_spec.get_length(sheet)
                        #print acell
                        #print len(self.specimens)

    def __str__(self):
        return self.filename

class Specimen:
    stl_id = None
    row = None
    column = None
    area = None
    dimension = {}

    def __init__(self, name, row, column, sheet):
        self.stl_id = name
        self.row = row
        self.column = column
        self.fetch_measurements(sheet)
        #!!! need documentation about spreadsheet format (or examples) to further 
        #!!! The area value is never used, so why bother calculating the it? 
        try:
            a = self.dimension['thickness'] * self.dimension['width']
        except KeyError:
            pass
        else:
            if a != 0: #!!! is this check necessary? 
                self.area = a

        try:
            a = self.dimension['diameter'] ** 2 * math.pi / 4
        except KeyError:
            pass
        else:
            if a != 0: #!!! is this check necessary? 
                self.area = a

    def __str__(self):
        return str(self.stl_id) + ', ' + str(self.row) + ', '+str(self.column)

    def fetch_measurements(self, sheet):
        '''
        Searches through the specified "sheet" for 
        for width, thickness, length, and diameter values and 
        saves found values in the self.dimension dictionary. 

        Takes one argument, a "sheet". 
        '''
        for i in ['width','thickness','length','diameter']:
            for column in range(self.column+1,self.column+3+1):
                if self.dimension[i] == 0 and \
                    sheet.row(self.row)[column].value.lower().find(i) != -1:
                    self.dimension[i] = sheet.row(self.row + 4)[column].value
                    #print 'Setting', i, 'to', self[i]

if __name__== '__main__':
    print sys.argv[1]
    an_excel_file = MeasFile(sys.argv[1]) #!!!
    print an_excel_file
    sheet1 = an_excel_file.book.sheet_by_index(0)
    print sheet1.name
