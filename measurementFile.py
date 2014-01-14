#!/usr/bin/env python

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

import math
import sys
import xlrd

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
    name_rows = []#range(7, 50+1, 5) #!!! magice numbers
    name_cols = []#range(0, 5+1, 5) #!!! magice numbers
    
    def find_magic_numbers(self,sheet):
        if (sheet.nrows > 0):
            minrow = None
            for row in range(0,sheet.nrows):
                for col in range(0,sheet.ncols):
                    acell = sheet.row(row)[col]
                    if acell.ctype == 1:
                        if acell.value.find('Specimen ID')!=-1: 
                            #Searches whole sheet for the "Specimen ID" label
                            #and remembers those columns 
                            self.name_cols += [col]
                            #Also saves the row so we can ignore stuff above here
                            minrow = row
                            
            for col in self.name_cols:
                for row in range(minrow,sheet.nrows):
                    acell = sheet.row(row)[col+1]
                    #look in the next column over from the specimen ID's
                    if acell.ctype == 1:
                        #looks for text and assumes these are the labels
                        #the rest should be numbers
                        self.name_rows += [row]
            
    
    def __init__(self, filename):
        self.sheets = []
        self.specimens = []
        self.filename = filename
        self.book = xlrd.open_workbook(self.filename)
        for sheet in self.book.sheets():
            self.find_magic_numbers(sheet)
            if (sheet.nrows > 0
            and sheet.row(0)[4].value.find('Measurement Sheet') != -1):
                # The sheet is a measurement sheet. 
                print sheet.name, 'is a measurement sheet!'
                self.sheets.append(sheet)
        #print 'number of sheets:', self.len(self.sheets)
        for sheet in self.sheets:
            for arow in self.name_rows:
                for acol in self.name_cols:
                    #print arow,acol
                    acell = sheet.row(arow)[acol]
                    #print acell.ctype
                    if acell.ctype == 1: #!!! cell contans text
                        #!!! what's going on with the following assignment? Does acell.value have any effect? 
                        specID = acell.value.upper().replace('STL', '').strip()
                        print "Found specimen number:",specID
                        specimen = Specimen(specID, arow, acol, sheet)
                        self.specimens.append(specimen)
                        
                    else:
                        print "Cell", sheet.name, arow, acol, " was the wrong type, not text!"
                        

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
        #!!! Infortunately this needs to work on measurement sheets which are 
        #!!! undocumented and change without notice :-)
        #!!! The area value is never used, so why bother calculating the it? 
        try:
            #print self.stl_id
            if self.dimension['thickness'] != None and self.dimension['width'] != None:
                a = self.dimension['thickness'] * self.dimension['width']
                #print "The area of", self.stl_id, "is", a
            
        except KeyError:
            pass
        else:
            if a != 0: #!!! is this check necessary? Yes, prevents X/0 errors
                self.area = a
                #print "The area of", self.stl_id, "is", self.area

        try:
            if self.dimension['diameter'] != None:
                a = self.dimension['diameter'] ** 2 * math.pi / 4
        except KeyError:
            pass
        else:
            if a != 0: #!!! is this check necessary? 
                self.area = a
                #print "The area of", self.stl_id, "is", self.area
	def __iter__(self,item):
	    return 	self.dimension.__iter__(item)

    def __str__(self):
        return str(self.stl_id) + ', ' + str(self.row) + ', '+str(self.column)

    def fetch_measurements(self, sheet):
        '''
        Searches through the specified "sheet" for 
        for width, thickness, length, and diameter values and 
        saves found values in the self.dimension dictionary. 

        Takes one argument, a "sheet". 
        '''
        #print "fetching measurements"
        for i in ['width','thickness','length','diameter']:
            #print "Looking for", self.stl_id, i
            for column in range(self.column+1,self.column+3+1):
                #print i, column
                try: 
                    self.dimension[i]
                except(KeyError):
                    self.dimension[i] = None;
                if sheet.row(self.row)[column].value.lower().find(i) != -1:
                    self.dimension[i] = sheet.row(self.row + 4)[column].value
                    print 'Setting specimen', self.stl_id, i, 'to', self.dimension[i]
                #else:
                    #print "did not find", i, "at column", column 

if __name__== '__main__':
    print sys.argv[1]
    an_excel_file = MeasFile(sys.argv[1]) #!!!
    #print an_excel_file
    sheet1 = an_excel_file.book.sheet_by_index(0)
    print sheet1.name
