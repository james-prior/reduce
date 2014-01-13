#"Copyright 2010 Bryan Harris"
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
import shutil

class measFile:
    filename = ""
    description = ""
    sponsor = ""
    tech = ""
    acct_number = ""
    date = ""
    sheets = []
    specimens = []
    sheet_count = 0
    book = ""
    name_rows = (5,10,15,20,25,30,35,40,45,50)
    name_cols = (0,5)
    def __init__(self, name, *args, **kwargs):
        self.sheets = []
        self.specimens = []
        self.filename = name
        self.book = xlrd.open_workbook(self.filename)
        for sheet in self.book.sheets() :
            is_a_meas_sheet = True
            if (sheet.nrows == 0) :
                is_a_meas_sheet = False
            else :
                if sheet.row(0)[4].value.find("Measurement Sheet") == -1 : 
                    is_a_meas_sheet = False
                if sheet.row(4)[0].value.find("Specimen ID") == -1:
                    is_a_meas_sheet = False
                if sheet.row(4)[5].value.find("Specimen ID") == -1:
                    is_a_meas_sheet = False
            if (is_a_meas_sheet == True) : 
                #print sheet.name, "is a measurement sheet!"
                self.sheets.append(sheet) 
        self.sheet_count = len(self.sheets)
        #print "sheet_count:",self.sheet_count
        for sheet in self.sheets :
            for arow in self.name_rows :
                for acol in self.name_cols :
                    acell = sheet.row(arow)[acol]
                    if acell.ctype == 1 : 
                        acell = acell.value
                        acell = acell.upper()
                        acell = acell.replace("STL","")
                        acell = acell.strip()
                        thisSpec = specRec(acell,arow,acol,sheet)
                        self.specimens.append(thisSpec)
                        #thisSpec.getMeasurements(sheet)
                        #thisSpec.getThickness(sheet)
                        #thisSpec.getLength(sheet)
                        #print acell
                        #print len(self.specimens)
            
    def __str__(self):
        return self.filename
    
class specRec:
    import math
    stl_ID = ""
    row = -1
    column = -1
    length = 0
    width = 0
    thick = 0
    diameter = 0
    area = 0
    def __init__(self, name, row, column, sheet, *args, **kwargs):
        self.stl_ID = name
        self.row = row
        self.column = column
        self.getMeasurements(sheet)
        if self.width != 0 and self.thick != 0 : self.area = self.thick*self.width
        if self.diameter != 0 : self.area = self.diameter**2*math.pi/4
        
    def __str__(self):
        return str(self.stl_ID)+ ", "+ str(self.row) + ", " + str(self.column)
        
    def getMeasurements(self,sheet):
        self.getWidth(sheet)
        self.getThickness(sheet)
        self.getLength(sheet)
        self.getDiameter(sheet)
        
    def getWidth(self, sheet):
        for offset in (1,2,3):
            if self.width == 0 and \
                sheet.row(self.row)[self.column+offset].value.lower().find("width") != -1 :
                self.width = sheet.row(self.row+4)[self.column+offset].value
                #print "Setting width to", self.width
        return self.width
            
    def getThickness(self, sheet):
        for offset in (1,2,3):
            if self.thick == 0 and \
                sheet.row(self.row)[self.column+offset].value.lower().find("thickness") != -1 :
                self.thick = sheet.row(self.row+4)[self.column+offset].value
                #print "Setting thickness to", self.thick
        return self.thick
        
    def getLength(self, sheet):
        for offset in (1,2,3):
            if self.length == 0 and \
                sheet.row(self.row)[self.column+offset].value.lower().find("length") != -1 :
                self.length = sheet.row(self.row+4)[self.column+offset].value
                #print "Setting length to", self.length
        return self.length
        
    def getDiameter(self, sheet):
        for offset in (1,2,3):
            if self.diameter == 0 and \
                sheet.row(self.row)[self.column+offset].value.lower().find("diameter") != -1 :
                self.diameter = sheet.row(self.row+4)[self.column+offset].value
                #print "Setting diameter to", self.diameter
        return self.diameter
    
if __name__== '__main__' :
    print sys.argv[1]
    an_excel_file = measurementFile(sys.argv[1])
    print an_excel_file
    sheet1 = an_excel_file.book.sheet_by_index(0)
    print sheet1.name