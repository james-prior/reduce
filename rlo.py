#!/usr/bin/env python

#"Copyright 2009 Bryan Harris"
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
#

'''
Need to use docstrings more. 
Things are very rough right now. Release early, release often. 

*.txt files
Plain text files
Tab characters and only tab characters delimit fields. 
Excluding other whitespace as field delimiters allows fields to have 
spaces in them. This is useful in the header lines. 
Each line in a file has the same number of fields as all the other lines.  
The fields are also known as columns.
The fields in the first line have labels, which are ignored by this program. 
The fields in the second line have the units. 
   Let's hope that the units are spelled consistently, 
   so that the program can recognize and use them automatically. 
   (jep:) I don't think the program does this yet, 
   but we'll have to make it do so. 
The rest of the lines have numerical data, one number per field. 
Scientific notation is fine. 
For all lines (including but not limited to header lines and 
numerical data lines), 
it seems that the columns must be as follows (start at 0 for first column): 
0 (dataFile.DataFile.TIME) time (unit is one second)
1 (dataFile.DataFile.STROKE) displacement (aka "stroke") unit is 1 inch
2 (dataFile.DataFile.LOAD) force (unit is one pound-force)
It seems that other columns are not used except to repeat them in output file. 
It seems that there must not be more than six columns. 

It seems that 6 for dataFile.DataFile_SL.ZERO_LOAD (6) is a special trick 
value index. Maybe lower values are reserved for columns of input. 

Output *.txt file: 

Every line has the same number of fields. 
Fields are separated by tabs (not any other whitespace). 
First line is header line. There is only one header line. 
Fields in the header line either: 
    o   have meaningful info in the format "Label [unit]" 
    o   have useless number (e.g. '-3.437E-1'). 
            The number seems to be from the corresponding field of the 
            first line of numerical data, and seems to be an artifact of 
            an "off by one" bug that overwrites data in the output with 
            header info. 
            Should these columns have an empty header field? 
            Should such columns be suppressed from the output altogether? 
    o   'blank'

Column Index (starting from zero), Header Line, Description: 
0, Time [sec], echoes column 0 of input (time), reformated in fixed point. 
1, Stroke [in], seems to be displacement - (minimum of all displacements)
                does this have early line skew? 
2, Load [lbf], seems to echo column 2 of input (without first line)
3, <float number>, seems to be copy of column 3 of input
4, <float number>, seems to be copy of column 4 of input
5, 'blank', <empty field>
6, Zeroed Load [lbf], is this the force - (force when no load) ?

"zero load" == (force when no load) ?

"zero load" is the measured force when the sample is not being touched. 
Is the weight of the sample part of the zero load?
If the part of a sample breaks off, 
should the zero load value decrease by the weight of the broken off part, 
when that part breaks off? 

I get the impression that the data from the numerical lines of input 
are copied over to an output structure, then fields 1,2,5,6 of 
the first line of output are _overwritten_ with header info, 
causing the loss of the numerical data that used to be there. 
I'll fix this stuff. 

Column 0 (time) seems to be an exception to the above. 

#!!! It seems that data for the first or second line of numerical data from 
     the input file is not reflected in the output file. 
     Is this good? Is this a bug? 
     Is this related to the detection of the minimum displacement? 
     Is there line skew in columns of ouputs? 

#!!! Stroke seems to be an artful term. 
         What is its definition? 
             Is stroke, just the difference (delta) between the 
             displacement of a particular line, and the lowest displacement? 
         Compare and contrast stroke with displacement. 
'''

import tempfile
import shutil
import os
import time
import sys

import numpy
import getopt

from dataFile import *
from measurementFile import *
from tee import *
from xlrd import *

'''
Reduces and plots a load-only time-stoke-load f
Input should be tab delimited data with the first two lines 
containing column names and units respectively.
'''
N_POINTS_FOR_EST = 150

def usage():
    print >>sys.stderr, '%s [-h] [--help]' % sys.argv[0]

if __name__ != '__main__':
    print >>sys.stderr, 'ERROR: The', __name__,
    print >>sys.stderr, 'module is meant to be run only as the main module.'
    usage()
    sys.exit(os.EX_USAGE)

try:
    opts, args = getopt.gnu_getopt(
        sys.argv[1:], 'hn:t:g:', ('help', 'passes=', 'threshold=', 'gage='))
    n_passes = -1
    threshold = .5
    gage_length_in = 0
    for o, a in opts:
        if o in ('-n', '--passes'):
            n_passes = int(a) #!!! this is not referenced anywhere
        elif o in ('-h', '--help'):
            raise getopt.GetoptError('')
        elif o in ('-t', '--threshold'):
            threshold = float(a) #!!! this is not referenced anywhere
        elif o in ('-g', '--gage'):
            gage_length_in = float(a)
except getopt.GetoptError, info: #!!! what is info? 
    print info
    usage()
    sys.exit(os.EX_USAGE)

# Redirect writes to stdout to go to both standard output and a log file. 
real_stdout = sys.stdout
sys.stdout = tee = Tee([real_stdout, open('script.log', 'w')])

base_path = os.getcwd()
print 'base_path:', base_path

def create_directory(directory):
    # Create directory, but only if needed. 
    if not os.access(directory, os.W_OK):
        try:
            os.mkdir(directory)
        except:
            print >>sys.stderr, ('ERROR: Could not create %s directory. '
                % directory)
            sys.exit(os.EX_CANTCREAT)
        else:
            print directory, 'created'

    # Test for ability to write to directory. 
    if not os.access(directory, os.W_OK):
        print >>sys.stderr, ('ERROR: Could not write to the %s directory.'
            % directory)
        sys.exit(os.EX_IOERR)

# reduce_path is name of directory to put reduced data in. 
reduce_path = os.path.join(base_path, 'reduced')
print 'reduce_path:', reduce_path
create_directory(reduce_path)

# image_path is name of directory to put pretty plot images in.  
image_path = os.path.join(reduce_path, 'png')
print 'image_path:', image_path
create_directory(image_path)

summary_file_path = os.path.join(reduce_path, 'summary.dat')
print 'summary_file_path:', summary_file_path
summary_file = open(summary_file_path, 'w')
print >>summary_file, 'Specimen\tRate\tPeak Load'

working_files = []
measurement_file_names = []

# Copy the text (*.txt) and Excel (*.xls) files into a working directory and 
# make separate lists of them.  
for filename in os.listdir(base_path):
    sourcefile = os.path.join(base_path, filename)
    destfile = os.path.join(reduce_path, filename)
    if filename.lower().endswith('.txt'):
        shutil.copyfile(sourcefile, destfile)
        working_files.append(destfile)
    if filename.lower().endswith('.xls'):
        shutil.copyfile(sourcefile, destfile)
        measurement_file_names.append(destfile)

def isfloat(s):
    '''
    Takes a single argument. 
    Returns True if that argument can be interpreted as a float; 
    returns False otherwise. 
    '''
    try:
        float(s)
    except:
        return False
    else:
        return True

def has_non_float(s):
    '''
    Takes a single argument. 
    Returns True if that argument has any non-floats; 
    returns False otherwise. 
    '''
    for word in s.split():
        if not isfloat(word):
            return True
    else:
        return False
    #!!! I'm thinking of replacing the above code with the following code. 
    #!!! My reservation is that the following is too tricky. 
    #!!! Is it too tricky, or is my unease a symptom of my unfamiliarity 
    #!!! with Python and the "Python way"? 
    #!!! import operator
    #!!! return not reduce(operator.__and__,map(isfloat,s.split()),True)

# Remove header lines from files listed in working_files. 
#
# Header lines are lines that have stuff that can not be interpreted as float. 
#!!! Consider doing this closer to where data is consumed. 
for filename in working_files:
    srcfile = open(filename, 'rU')
    dstfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
    for line in srcfile:
        if not has_non_float(line):
            dstfile.write(line)
        #!!! I wonder about replacing the above if statement with: 
        #!!! if reduce(operator.__and__,map(isfloat,s.split()),True):
    dstfile.close()
    srcfile.close()
    shutil.move(dstfile.name, filename)

print time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.localtime())
print 'user:', os.times()[0], 's'
print 'system:', os.times()[1], 's'
print

# Start prcessing the data files. 

print 'Measurement Files:'
print
measurement_files = []
for meas_file_name in measurement_file_names:
    print meas_file_name
    measurement_files.append(MeasFile(meas_file_name)) #!!! should this be moved up to where measurement_file_names are appended? How does what MeasFile return differ from what it is passed? 

os.chdir(reduce_path) # !!! try to eventually eliminate. 

for filename in map(os.path.basename, working_files):
    print 'Analyzing:', filename

    # Plot the raw data and move the picture to image_path directory.
    DataFile_SL(filename).moby_foo(
        image_path,
        measurement_files,
        gage_length_in,
        N_POINTS_FOR_EST,
        summary_file)

    print time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.localtime())
    print 'user:', os.times()[0], 's'
    print 'system:', os.times()[1], 's'
    print

