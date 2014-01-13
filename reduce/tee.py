#! /usr/bin/python
# Copyright 2011 James E. Prior
#
# This is the tee module. 
#
#    Tee is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    Tee is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Tee  If not, see <http://www.gnu.org/licenses/>.
#

class Tee:
    '''
    Simplifies writing to multiple files. 

    Instead of repeating a print for each file one needs to output to, 
    one uses a single print that redirects to an instance of this class.  

    For example, instead of doing: 
       print 'big long ugly messy stuff'
       print >>file1 'big long ugly messy stuff'
       print >>file2 'big long ugly messy stuff'
    one does the following:
       tee=Tee([sys.stdout,file1,file2])
       ...
       print >>tee 'big long ugly messy stuff'
    '''
    def __init__(self,list_of_open_files):
        '''
        Accepts one argument, a list of files that are already open. 
        '''
        self.files=list_of_open_files
    def write(self,s):
        '''
        Accepts one argument, and writes it to each of the files 
        that were specified when the instance was created.  
        '''
        for f in self.files:
            f.write(s)

